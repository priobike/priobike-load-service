from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path("start", views.PostAppStart.as_view(), name="add-app-start"),
]
