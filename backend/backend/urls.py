"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from backend.views import GetLoadResponseView, HealthcheckView, StatusView

urlpatterns = [
    path('app/', include('app.urls')),
    path('status', StatusView.as_view(), name='status'),
    path('healthcheck', HealthcheckView.as_view(), name='healthcheck'),

    # Originally, this was mapped over an nginx proxy that was removed.
    # Note: For this to work, the staticfiles app must be removed.
    path('static/load_response.json', GetLoadResponseView.as_view(), name='load_response'),
]

if settings.SYNC_EXPOSED:
    urlpatterns.append(path('sync/', include('sync.urls')))

if not settings.WORKER_MODE:
    urlpatterns.append(path(settings.ADMIN_URL, admin.site.urls))
    urlpatterns.append(path('monitoring/', include('monitoring.urls')))
