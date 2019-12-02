import json
import subprocess
import redis

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

from core.service.client.postgres import Manager as ClientManager
from core.settings import Settings
import client as client_pkg


global_settings = None
global_client_manager = None


def get_settings():
    global global_settings
    if not global_settings: global_settings = Settings.load_config()
    return global_settings


def get_client_manager():
    global global_client_manager
    if not global_client_manager: global_client_manager = ClientManager(get_settings())
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
        "  - Lookup http api:\n"
        "\tGET /api/v1/lookup/:username/:provider_name/\n"
        "\tReturns {\n"
        "\t\t'status': [string, success | error].\n"
        "\t\t'msg': [string, error or success message].\n"
        "\t\t'address': [string, address returned fron loopup operation].\n"
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


def ping_operation(request, client_id):
    if request.method != 'GET':
        return JsonResponse({
            "status": "error",
            "msg": "GET method is required"
        })
    client_pkg.send_ping(get_settings().ping_host, get_settings().ping_port, client_id)
    return JsonResponse({
        "status": "success",
        "msg": "Ping has been sent."
    })


def lookup_operation(request, username, provider_name):
    if request.method != 'GET':
        return JsonResponse({
            "status": "error",
            "msg": "GET method is required"
        })
    result = client_pkg.send_lookup(
        provider_name, get_settings().host, get_settings().port, username, get_settings().gns_address_separator,
        True, 1)
    if result != None:
        return JsonResponse({
            "status": "success",
            "msg": "Lookup operation is successful",
            "address": result
        })
    return JsonResponse({
        "status": "error",
        "msg": "Lookup operation is failed. No such client."
    })

