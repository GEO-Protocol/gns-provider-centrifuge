

class ClientManager:
    def find_by_id(self, id):
        raise NotImplementedError

    def find_by_username(self, username):
        raise NotImplementedError

    def create(self, id, name):
        raise NotImplementedError

    def save(self, client):
        raise NotImplementedError

    def delete(self, client):
        raise NotImplementedError
