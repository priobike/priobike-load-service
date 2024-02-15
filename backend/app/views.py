import json

from app.models import Start
from django.http import JsonResponse, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


@method_decorator(csrf_exempt, name='dispatch')
class PostAppStart(View):
    def post(self, request):
        try:
            Start.objects.create()
        except Exception as e:
            return HttpResponseServerError(json.dumps({"error": "Internal server error."}))
        
        return JsonResponse({"success": True})