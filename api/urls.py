from django.urls import path

from .views import *

urlpatterns = [
    path('', home_page, name='home_page'),
    path('api/v1/users/', user_register, name='user_register'),
    path('api/v1/users/<int:client_id>/', user_update_crypto_key, name='user_update_crypto_key'),
    path('api/v1/ping/<int:client_id>/', ping_operation, name='ping_operation'),
    path('api/v1/lookup/<str:username>/<str:provider_name>/', lookup_operation, name='lookup_operation'),
]