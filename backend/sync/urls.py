from django.conf import settings
from django.urls import path

from . import views

app_name = 'sync'

if settings.WORKER_MODE and settings.SYNC_EXPOSED:
    urlpatterns = [
        path("sync", views.SyncResource.as_view(), name="sync"),
    ]
else:
    urlpatterns = []