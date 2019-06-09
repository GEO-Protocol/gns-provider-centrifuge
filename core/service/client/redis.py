import json
import redis

from core.model.client import Client
from core.settings import Settings


class Manager:
    def __init__(self, settings: Settings):
        self._redis_pool = redis.ConnectionPool(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db)

    def _redis(self):
        return redis.Redis(connection_pool=self._redis_pool)

    def load(self, client):
        dump = self._redis().get("client_"+str(client.id))
        if not dump:
            self.save(client)
            return client
        json_obj = json.loads(dump.decode("utf-8"))
        client.address = json_obj[0]
        client.time_updated = json_obj[1]
        return client

    def save(self, client):
        dump = json.dumps([client.address, client.time_updated])
        pipe = self._redis().pipeline()
        pipe.set("client_"+str(client.id), dump)
        pipe.execute()

    def delete(self, client):
        self._redis().delete("client_"+str(client.id))
