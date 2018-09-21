import socket

import redis
from redis.client import Pipeline

from core.clients.clients import Client
from core.settings import Settings, ASSERTS


class ClientsHandler:
    """
    todo: adjust centrifuge timeouts per address
    """

    default_address_ttl = 60*60*10     # 10 minutes

    def __init__(self, settings: Settings):
        self.redis_pool = redis.ConnectionPool(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db)

    def set_ipv4_address(self, client: Client, ipv4_address: str, port: int):
        """
        Sets (or updates) client IPv4 address in redis.
        Sets default ttl for the record.
        Flushes client's record ttl to the default.

        :param client: client, that must be updated/reset.
        :param ipv4_address: address that must be updated/reset.
        :param port: port, to which PING messages must be sent by this address.
        """

        if ASSERTS:
            socket.inet_aton(ipv4_address)
            assert port < 2**16
            assert port > 0

        # todo: check contract if record with such name is present.
        # todo: check contract if record with such name points to this provider.

        pipe = self._redis().pipeline()
        self._set_client(client, pipe)
        self._set_address(client, ipv4_address, port, pipe)
        pipe.execute()

    def get_by_id(self, client_id: int) -> Client or None:
        """
        :param client_id: id of the client, that must be fetched from the redis.
        :returns: client instance, or None in case if no such client is present in the redis.
        """
        if ASSERTS:
            assert client_id >= 0
            assert client_id <= 2**32

        raw = self._redis().get(f'#{client_id}')
        if raw is None:
            return None

        return Client.deserialize(raw)

    def get_by_name(self, name: str) -> Client or None:
        """
        :param name: name of the participant that must be found.
        :return: found client, or None in cae if no client is present.
        """

        if ASSERTS:
            assert type(name) is str
            assert len(name) > 0

        client_id = self._redis().get(f'!{name}')
        if client_id is None:
            return None

        return self.get_by_id(int(client_id))

    def get_all_clients_ids(self):
        """
        :returns: list of ids of all clients, that are present in redis.
        """

        ids = self._redis().keys('#*')
        ids = [int(id.decode('utf-8').split('#')[1]) for id in ids]
        return ids

    def get_ipv4_addresses(self, client_id: int) -> []:
        """
        :param client_id: id of the client, which ipv4 addresses should be fetched from the redis.
        :returns: list of ipv4 addresses, that are related to the client.
        """

        if ASSERTS:
            assert client_id >= 0
            assert client_id <= 2**32

        ipv4_addresses = self._redis().keys(f'{client_id}:*')
        return [record.decode('utf-8').split(':')[1] for record in ipv4_addresses]

    def get_ipv4_addresses_and_ports(self, client_id: int) -> []:
        """
        :param client_id: id of the client, which ipv4 addresses and ports should be fetched from the redis.
        :return: list of ipv4 addresses and ports, that are related to the client.
        """

        if ASSERTS:
            assert client_id >= 0
            assert client_id <= 2**32

        ipv4_addresses = self._redis().keys(f'{client_id}:*')

        pipe = self._redis().pipeline()
        for address in ipv4_addresses:
            pipe.get(address)
        ports = pipe.execute()
        ports = [int(port) for port in ports]

        ipv4_addresses = [record.decode('utf-8').split(':')[1] for record in ipv4_addresses]
        return zip(ipv4_addresses, ports)

    def _redis(self):
        return redis.Redis(connection_pool=self.redis_pool)

    def _set_client(self, client: Client, pipe: Pipeline) -> None:
        if ASSERTS:
            assert '!' not in client.name

        pipe.setex(f'#{client.id}', client.serialize(), self.default_address_ttl)
        pipe.setex(f'!{client.name}', client.id, self.default_address_ttl)

    def _set_address(self, client: Client, ipv4_address: str, port:int, pipe: Pipeline) -> None:
        pipe.setex(f'{client.id}:{ipv4_address}', port, self.default_address_ttl)
