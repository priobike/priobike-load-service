from app.models import Bucket, Status
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


@method_decorator(csrf_exempt, name='dispatch')
class GetMetricsResource(View):
    def get(self, request):
        """
        Generate Prometheus metrics as a text file and return it.
        """
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            return HttpResponseForbidden()

        metrics = []

        last_bucket = Bucket.objects.order_by('-end_time').first()
        if last_bucket:
            metrics.append(f'last_bucket_cpm {last_bucket.cpm}')
        else:
            metrics.append('last_bucket_cpm 0')

        last_status = Status.objects.order_by('-time').first()
        if last_status:
            metrics.append(f'last_status_warning {int(last_status.warning)}')
            metrics.append(f'last_status_bucket_length {last_status.bucket_length}')
            metrics.append(f'last_status_app_starts {last_status.app_starts}')
            metrics.append(f'last_status_past_buckets_avg_cpm {last_status.past_buckets_avg}') # cpm
        else:
            metrics.append('last_status_warning 0')
            metrics.append('last_status_bucket_length 0')
            metrics.append('last_status_app_starts 0')
            metrics.append('last_status_past_buckets_avg_cpm 0') # cpm

        content = '\n'.join(metrics) + '\n'
        return HttpResponse(content, content_type='text/plain')
        