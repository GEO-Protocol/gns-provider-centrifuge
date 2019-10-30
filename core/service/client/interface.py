

class Manager:
    def find_by_id(self, id):
        raise NotImplementedError

    def find_by_username(self, username):
        raise NotImplementedError

    def create(self, id, name):
        raise NotImplementedError

    def save(self, client, redis_only=False):
        raise NotImplementedError

    def delete(self, client, redis_only=False):
        raise NotImplementedError
