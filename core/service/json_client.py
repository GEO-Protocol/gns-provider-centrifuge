import json

from core.service.client import ClientManager
from core.model.client import Client


class JsonClientManager(ClientManager):
    def __init__(self, path):
        self.path = path

        #client = self.create(1, "minyor")
        #self.save(client)

    def load_handle(self):
        try:
            file = open(self.path)
            handle = json.load(file)
            return handle
        except:
            print("Initialising Json DB...")
            data = {
                "clients": {},
                "user_names": {}
            }
            self.save_handle(data)
            return data

    def save_handle(self, handle):
        with open(self.path, 'w') as cpm_file_out:
            json.dump(handle, cpm_file_out, indent=4, ensure_ascii=False)

    @staticmethod
    def load_client(json_obj):
        client = Client()
        client.id = int(json_obj.get("id", None))
        client.username = json_obj.get("username", None)
        client.address = json_obj.get("address", None)
        client.time_created = json_obj.get("time_created", None)
        client.time_updated = json_obj.get("time_updated", None)
        return client

    def find_by_id(self, id):
        handle = self.load_handle()
        clients = handle["clients"]
        json_obj = clients.get(str(id), None)
        if not json_obj:
            return None
        return self.load_client(json_obj)

    def find_by_username(self, username):
        handle = self.load_handle()
        user_names = handle["user_names"]
        id = str(user_names.get(username, None))
        if not id:
            return None
        clients = handle["clients"]
        json_obj = clients.get(str(id), None)
        if not json_obj:
            return None
        return self.load_client(json_obj)

    def create(self, id, username):
        return Client(id, username)

    def save(self, client):
        id = str(client.id)
        handle = self.load_handle()
        clients = handle["clients"]
        obj = clients.get(id, None)
        if not obj:
            clients[id] = {}
            user_names = handle["user_names"]
            user_names[client.username] = client.id
            obj = clients.get(id, None)
        obj["id"] = client.id
        obj["username"] = client.username
        obj["address"] = client.address
        obj["time_created"] = client.time_created
        obj["time_updated"] = client.time_updated
        self.save_handle(handle)

    def delete(self, client):
        id = str(client.id)
        handle = self.load_handle()
        clients = handle["clients"]
        obj = clients.get(id, None)
        if obj:
            del clients[id]
            user_names = handle["user_names"]
            obj = user_names.get(client.username, None)
            if obj:
                del user_names[client.username]
            self.save_handle(handle)
