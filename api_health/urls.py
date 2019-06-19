from django.urls import path

from .views import *

urlpatterns = [
    path('api/v1/status/', provider_health_check, name='provider_health_check'),
]