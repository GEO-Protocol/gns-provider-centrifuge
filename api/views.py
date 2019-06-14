import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

from core.service.client.json import Manager as ClientManager
from core.settings import Settings


global_client_manager = None


def get_client_manager(request):
    # client_manager = request.session.get('client_manager')
    # request.session['client_manager'] = client_manager

    global global_client_manager
    if not global_client_manager:
        settings = Settings.load_config()
        global_client_manager = ClientManager(settings)
    return global_client_manager


def home_page(request):
    return HttpResponse(
        "<pre>"
        "This is REST API for: 'gns-provider-centrifuge'.\n"
        "USAGE:\n"
        "  - User registration:\n"
        "\tPOST /api/v1/users/\n"
        "\t{\n"
        "\t\t'id': [int, required],\n"
        "\t\t'username': [string, required],\n"
        "\t\t'key': [string, required, hex-string crypto key].\n"
        "\t}\n"
        "\t\n"
        "  - Crypto key update for existing user:\n"
        "\tPATCH /api/v1/users/:id/\n"
        "\t{\n"
        "\t\t'key': [string, required, hex-string crypto key].\n"
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
        client_manager = get_client_manager(request)
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
        client_manager = get_client_manager(request)
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
