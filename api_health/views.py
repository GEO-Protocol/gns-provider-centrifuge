import sys
import json
import redis

from django.http import JsonResponse
from django.http import QueryDict

from core.service.client.json import Manager as ClientManager
from core.settings import Settings

from health.settings import Settings as HealthSettings
from health import Check


global_binding_port = None
global_health_settings = None


def get_binding_port():
    global global_binding_port
    if not global_binding_port: global_binding_port = Check.get_binding_port()
    return global_binding_port


def get_health_settings():
    global global_health_settings
    if not global_health_settings: global_health_settings = HealthSettings.load_config()
    return global_health_settings


def provider_health_check(request):
    health_settings = get_health_settings()
    health_check = Check(health_settings)

    binding_port = get_binding_port()
    if health_settings.api_port != binding_port:
        return JsonResponse({
            "state": "error"
        })

    client_id = health_check.random_client_id()
    print("random_key="+str(client_id))
    if not client_id:
        return False

    cluster_info = health_check.load_cluster_info()
    cluster_state = cluster_info.get("cluster_state", None)
    if not cluster_state or cluster_state != "ok" or not client_id:
        return JsonResponse({
            "state": "non-operational"
        })

    percent = health_check.providers(client_id)
    if percent < 70:
        return JsonResponse({
            "state": "degraded"
        })

    return JsonResponse({
        "state": "operational"
    })
