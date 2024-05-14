import json
from datetime import datetime

from app.models import Start, Status
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from sync.models import LoadServiceStartup


@method_decorator(csrf_exempt, name='dispatch')
class SyncResource(View):
    def get(self, request):
        """
        Get the current CPM and delete old starts.
        """
        sync_key = request.GET.get("key")
        if sync_key != settings.SYNC_KEY:
            print(f"Invalid key: {sync_key}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))
        
        bucket_start = request.GET.get("start") # isoformat
        bucket_end = request.GET.get("end") # isoformat
        if not bucket_start or not bucket_end:
            print(f"Invalid start/end: {bucket_start}, {bucket_end}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid start/end."}))
        
        # Parse the bucket start and end times.
        try:
            bucket_start = datetime.fromisoformat(bucket_start)
            bucket_end = datetime.fromisoformat(bucket_end)
        except ValueError:
            print(f"Invalid start/end: {bucket_start}, {bucket_end}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid start/end."}))
        
        # Check if the service started up before the bucket start.
        startups = LoadServiceStartup.objects.order_by("-time")
        if not startups.exists():
            print(f"No startups")
            return HttpResponseBadRequest(json.dumps({"error": "No startups."}))
        most_recent_startup = startups.first()
        if most_recent_startup.time > bucket_start:
            print(f"No startup before {bucket_start}: Earliest is {most_recent_startup.time}")
            return HttpResponseBadRequest(json.dumps({"error": "Service (re)started within the bucket."}))

        # Get the number of app starts in the current bucket.
        current_bucket_start_counts = Start.objects \
            .filter(time__gte=bucket_start, time__lte=bucket_end) \
            .count()
        seconds_in_bucket = (bucket_end - bucket_start).total_seconds()
        if seconds_in_bucket == 0:
            print(f"Invalid bucket: {bucket_start}, {bucket_end}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid bucket."}))
        cpm = current_bucket_start_counts / (seconds_in_bucket / 60)

        # Can delete anything before bucket_start
        Start.objects.filter(time__lt=bucket_start).delete()
        return JsonResponse({"cpm": cpm})
    
    def post(self, request):
        """
        Update the current status.
        """
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            print("Invalid JSON.")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON."}))
        
        sync_key = body.get("key")
        if sync_key != settings.SYNC_KEY:
            print(f"Invalid key: {sync_key}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))
        
        time = body.get("time")
        # Parse the time.
        try:
            time = datetime.fromisoformat(time)
        except ValueError:
            print(f"Invalid time: {time}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid time."}))
        warning = body.get("warning")    
        response_text = body.get("responseText")
        bucket_length = body.get("bucketLength")
        app_starts = body.get("appStarts")
        past_buckets_avg = body.get("pastBucketsAvg")

        Status.objects.create(
            time=time,
            warning=warning,
            response_text=response_text,
            bucket_length=bucket_length,
            app_starts=app_starts,
            past_buckets_avg=past_buckets_avg
        )
        # Delete old objects
        Status.objects.filter(time__lt=time).delete()

        return JsonResponse({"status": "ok"})
