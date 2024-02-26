import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from app.models import Start


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

        metrics.append(f'n_app_starts {Start.objects.count()}')
        
        with open(str(settings.BASE_DIR) + f"/static/load_response.json", "r") as f:
            response_json = json.loads(f.read())
        metrics.append(f'load_warning {int(response_json["warning"])}')
        
        with open(str(settings.BASE_DIR) + f"/data/load_debug.json", "r") as f:
            debug_json = json.loads(f.read())
            
        metrics.append(f'current_bucket_start_counts {debug_json["current_bucket_start_counts"]}')
        metrics.append(f'past_buckets_avg {debug_json["past_buckets_avg"]}')

        content = '\n'.join(metrics) + '\n'
        return HttpResponse(content, content_type='text/plain')
        