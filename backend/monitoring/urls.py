from django.urls import path

from . import views

app_name = 'monitoring'

urlpatterns = [
    path("metrics", views.GetMetricsResource.as_view(), name="get-metrics"),
]