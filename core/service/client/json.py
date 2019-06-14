import os,sys
import json

import core.service.client.interface as interface
import core.service.client.redis as redis
from core.model.client import Client
from core.settings import Settings


class Manager(interface.Manager):
    def __init__(self, settings: Settings):
        self.root_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules[Settings.__module__].__file__)))
        self.redis = redis.Manager(settings)
        self.path = os.path.join(self.root_path, settings.database_name + ".json")
        self.clients_by_id = {}
        self.clients_by_username = {}

        self._load_json()
        # client = self.create(1, "minyor")
        # self.save(client)

    def find_by_id(self, id):
        id = str(id)
        client = self.clients_by_id.get(id, None)
        if client:
            return self.redis.load(client)
        handle = self._load_json()
        clients = handle["clients"]
        json_obj = clients.get(str(id), None)
        if not json_obj:
            return None
        client = self._load_client(json_obj)
        self.clients_by_id[id] = client
        self.clients_by_username[client.username] = client
        return self.redis.load(client)

    def find_by_username(self, username):
        client = self.clients_by_username.get(username, None)
        if client:
            return self.redis.load(client)
        handle = self._load_json()
        user_names = handle["user_names"]
        id = str(user_names.get(username, None))
        if not id:
            return None
        clients = handle["clients"]
        json_obj = clients.get(str(id), None)
        if not json_obj:
            return None
        client = self._load_client(json_obj)
        self.clients_by_id[id] = client
        self.clients_by_username[client.username] = client
        return self.redis.load(client)

    def create(self, id, username):
        return Client(id, username)

    def save(self, client, redis_only=False):
        self.redis.save(client)
        if redis_only:
            return
        id = str(client.id)
        handle = self._load_json()
        clients = handle["clients"]
        obj = clients.get(id, None)
        if not obj:
            clients[id] = {}
            user_names = handle["user_names"]
            user_names[client.username] = client.id
            obj = clients.get(id, None)
        obj["id"] = client.id
        obj["username"] = client.username
        obj["secret"] = client.secret
        obj["time_created"] = client.time_created
        self._save_json(handle)

    def delete(self, client, redis_only=False):
        self.redis.delete(client)
        if redis_only:
            return
        id = str(client.id)
        handle = self._load_json()
        clients = handle["clients"]
        obj = clients.get(id, None)
        if obj:
            del clients[id]
            user_names = handle["user_names"]
            obj = user_names.get(client.username, None)
            if obj:
                del user_names[client.username]
            self._save_json(handle)

    def _load_json(self):
        try:
            file = open(self.path)
            handle = json.load(file)
            file.close()
            return handle
        except:
            assert False, "Error: Cannot load Json DB."

    def _save_json(self, handle):
        with open(self.path, 'w') as cpm_file_out:
            json.dump(handle, cpm_file_out, indent=4, ensure_ascii=False)

    @staticmethod
    def _load_client(json_obj):
        client = Client()
        client.id = int(json_obj.get("id", None))
        client.username = json_obj.get("username", None)
        client.secret = json_obj.get("secret", None)
        client.time_created = json_obj.get("time_created", None)
        return client
