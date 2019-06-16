import json
import subprocess
import redis

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

from core.service.client.json import Manager as ClientManager
from core.settings import Settings


global_settings = None
global_client_manager = None


def get_settings():
    global global_settings
    if not global_settings:
        global_settings = Settings.load_config()
    return global_settings


def get_client_manager():
    # client_manager = request.session.get('client_manager')
    # request.session['client_manager'] = client_manager

    global global_client_manager
    if not global_client_manager:
        global_client_manager = ClientManager(get_settings())
    return global_client_manager


def home_page(request):
    return HttpResponse(
        "<pre>"
        "This is REST API for: 'gns-provider-centrifuge'.\n"
        "USAGE:\n"
        "  - User registration:\n"
        "\tPOST /api/v1/users/\n"
        "\tParameters {\n"
        "\t\t'id': [int, required],\n"
        "\t\t'username': [string, required],\n"
        "\t\t'key': [string, required, hex-string crypto key].\n"
        "\t}\n"
        "\tReturns {\n"
        "\t\t'status': [string, success | error].\n"
        "\t\t'msg': [string, error or success message].\n"
        "\t}\n"
        "\t\n"
        "  - Crypto key update for existing user:\n"
        "\tPATCH /api/v1/users/:id/\n"
        "\tParameters {\n"
        "\t\t'key': [string, required, hex-string crypto key].\n"
        "\t}\n"
        "\tReturns {\n"
        "\t\t'status': [string, success | error].\n"
        "\t\t'msg': [string, error or success message].\n"
        "\t}\n"
        "\t\n"
        "  - Health Check:\n"
        "\tGET /api/v1/status/\n"
        "\tReturns {\n"
        "\t\t'state': [string, operational | degraded | non-operational].\n"
        "\t}\n"
        "\t\n"
        "</pre>"
    )


@csrf_exempt
def user_register(request):
    if request.method != 'POST':
        return JsonResponse({
            "status": "error",
            "msg": "POST method is required"
        })

    client_id = request.POST.get("id", None)
    username = request.POST.get("username", None)
    key = request.POST.get("key", None)
    if not client_id:
        return JsonResponse({
            "status": "error",
            "msg": "'id' parameter is mandatory"
        })
    if not username:
        return JsonResponse({
            "status": "error",
            "msg": "'username' parameter is mandatory"
        })
    if not key:
        return JsonResponse({
            "status": "error",
            "msg": "'key' parameter is mandatory"
        })

    try:
        client_manager = get_client_manager()
        client = client_manager.find_by_id(int(client_id))
        if client:
            assert False, "Client '"+str(client_id)+"' already registered"
        client = client_manager.find_by_username(username)
        if client:
            assert False, "Client '"+str(username)+"' already registered"
        client = client_manager.create(int(client_id), str(username))
        client.secret = key
        client_manager.save(client)
        return JsonResponse({
            "status": "success",
            "msg": "User: '"+str(client_id)+"' has been registered"
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "msg": str(e)
        })


@csrf_exempt
def user_update_crypto_key(request, client_id):
    if request.method != 'PATCH':
        return JsonResponse({
            "status": "error",
            "msg": "PATCH method is required"
        })

    data = QueryDict(request.body)
    key = data.get("key", None)
    if not key:
        return JsonResponse({
            "status": "error",
            "msg": "'key' parameter is mandatory"
        })

    try:
        client_manager = get_client_manager()
        client = client_manager.find_by_id(int(client_id))
        if not client:
            assert False, "Client '"+str(client_id)+"' is not found"
        client.secret = key
        client_manager.save(client)
        return JsonResponse({
            "status": "success",
            "msg": "User: '"+str(client_id)+"' crypto key has been updated"
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "msg": str(e)
        })


def load_cluster_info():
    output = subprocess.check_output(['redis-cli', 'CLUSTER', 'INFO'])
    output = output.decode('UTF-8')
    output = output.split("\n")
    cluster_info = {}
    for line in output:
        name_val = line.split(":")
        if len(name_val) < 2:
            continue
        name_val[1] = name_val[1][:-1]
        cluster_info[name_val[0]] = name_val[1]
    # cluster_info["cluster_state"] = "ok"
    return cluster_info


def provider_health_check(request):
    cluster_info = load_cluster_info()
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
