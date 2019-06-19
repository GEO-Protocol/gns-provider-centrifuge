import sys
import json
import redis

from django.http import JsonResponse
from django.http import QueryDict

from core.service.client.json import Manager as ClientManager
from core.settings import Settings

from health.settings import Settings as HealthSettings
from health import Check


global_health_settings = None
global_client_manager = None


def get_health_settings():
    global global_health_settings
    if not global_health_settings:
        global_health_settings = HealthSettings.load_config()
    return global_health_settings


#def get_client_manager():
#    global global_client_manager
#    if not global_client_manager:
#        global_client_manager = ClientManager(get_settings())
#    return global_client_manager


def provider_health_check(request):
    health_settings = get_health_settings()
    health_check = Check(health_settings)

    port = Check.get_binding_port()
    if health_settings.api_port != port:
        return JsonResponse({
            "state": "error"
        })

    health_check.providers()

    cluster_info = health_check.load_cluster_info()
    cluster_state = cluster_info.get("cluster_state", None)
    if not cluster_state or cluster_state != "ok":
        return JsonResponse({
            "state": "non-operational"
        })

    return JsonResponse({
        "state": "operational"
    })

    return JsonResponse({
        "state": "degraded"
    })
