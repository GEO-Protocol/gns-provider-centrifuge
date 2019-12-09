import json
import redis

from core.settings import Settings


class Manager:
    expiration_time_in_seconds = 60 * 30  # 30 minutes
    redis_query_cnt_max = 100

    def __init__(self, settings: Settings):
        self._settings = settings
        self._redis_pool = None
        self._redis_query_cnt = self.redis_query_cnt_max
        self._reconnect_redis()

    def _reconnect_redis(self):
        if self._redis_query_cnt < self.redis_query_cnt_max:
            return
        self._redis_query_cnt = 0
        if self._redis_pool != None:
            self._redis_pool.disconnect()
        self._redis_pool = redis.ConnectionPool(
            host=self._settings.redis.host,
            port=self._settings.redis.port,
            db=self._settings.redis.db)

    def _redis(self):
        return redis.Redis(connection_pool=self._redis_pool)

    def load(self, client):
        dump = self._redis().get(self.key_name(client))
        if not dump:
            self.save(client)
            return client
        client.address = json.loads(dump.decode("utf-8"))
        self._reconnect_redis()
        return client

    def save(self, client):
        # timestamp = int(round(time.time() * 1000))
        # print("timestamp1="+str(client.time_updated))
        # print("timestamp2="+str(timestamp))

        dump = json.dumps(client.address)

        # pipe = self._redis().pipeline()
        # pipe.execute()

        status = self._redis().set(self.key_name(client), dump, ex=self.expiration_time_in_seconds)
        if status != True:
            self._settings.logger.error(
                "Cannot save client '" + client.username + "' address '" + client.address + "' to redis.")

        self._reconnect_redis()

    def key_name(self, client):
        # self._settings.provider_name + "_" +
        return str(client.id)

    def delete(self, client):
        self._redis().delete(self.key_name(client))
