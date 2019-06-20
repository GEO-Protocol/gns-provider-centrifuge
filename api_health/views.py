import sys
import json
import redis

from django.http import JsonResponse
from django.http import QueryDict

from core.settings import Settings
from health import Check


global_settings = None


def get_settings():
    global global_settings
    if not global_settings: global_settings = Settings.load_config()
    return global_settings


def provider_health_check(request):
    health_settings = get_settings()
    health_check = Check(health_settings)

    cluster_info = health_check.load_cluster_info()
    cluster_state = cluster_info.get("cluster_state", None)
    if not cluster_state or cluster_state != "ok":
        return JsonResponse({
            "state": "non-operational",
            "percent": str(-1)
        })

    percent = health_check.providers()
    if percent < 70:
        return JsonResponse({
            "state": "non-operational",
            "percent": str(percent)
        })

    if percent < 100:
        return JsonResponse({
            "state": "degraded",
            "percent": str(percent)
        })

    return JsonResponse({
        "state": "operational",
        "percent": str(percent)
    })
