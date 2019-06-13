import json
import redis

from core.settings import Settings


class Manager:
    expiration_time_in_seconds = 60 * 30  # 30 minutes

    def __init__(self, settings: Settings):
        self._settings = settings
        self._redis_pool = redis.ConnectionPool(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db)

    def _redis(self):
        return redis.Redis(connection_pool=self._redis_pool)

    def load(self, client):
        dump = self._redis().get(self.key_name(client))
        if not dump:
            self.save(client)
            return client
        client.address = json.loads(dump.decode("utf-8"))
        return client

    def save(self, client):
        # timestamp = int(round(time.time() * 1000))
        # print("timestamp1="+str(client.time_updated))
        # print("timestamp2="+str(timestamp))

        dump = json.dumps(client.address)

        # pipe = self._redis().pipeline()
        # pipe.execute()

        self._redis().set(self.key_name(client), dump, ex=self.expiration_time_in_seconds)

    def key_name(self, client):
        return self._settings.provider_name + "_" + str(client.id)

    def delete(self, client):
        self._redis().delete(self.key_name(client))
