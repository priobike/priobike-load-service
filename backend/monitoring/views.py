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

        # Add debug tracks to n_tracks.
        metrics.append(f'n_app_starts {Start.objects.count()}')

        content = '\n'.join(metrics) + '\n'
        return HttpResponse(content, content_type='text/plain')
        