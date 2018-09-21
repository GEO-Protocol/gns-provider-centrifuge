import socket
import struct

import netstruct
from Crypto import Random

from core.settings import ASSERTS


class Endpoint:
    def __init__(self, port: int, ipv4_address: str, ipv6_address: str=None):
        self._port = int(port)
        self._ipv4_address = ipv4_address

        # todo: add support of ipv6
#        self._ipv6_address = ipv6_address

    @property
    def port(self):
        return self._port

    @property
    def ipv4_address(self):
        return self._ipv4_address

#    @property
#    def ipv6_address(self):
#        return self._ipv6_address

    def serialize(self) -> bytes:
        # todo: add support of ipv6
        return struct.pack('>H', self._port) + socket.inet_aton(self._ipv4_address)

    @classmethod
    def deserialize(cls, data):
        port = netstruct.unpack('H', data[:2])[0]
        ipv4_address = socket.inet_ntoa(data[2:6])
        return Endpoint(port, ipv4_address)


class Message:
    class Types:
        ping = 0
        pong = 1

        set_address = 10
        set_address_ack = 11

        participant_lookup = 21
        participant_lookup_ack = 22
        participant_lookup_not_found = 23

        connection_request = 31

        @classmethod
        def as_enum(cls):
            return cls.__dict__.values()

    def __init__(self, type_id: int):
        self.type_id = type_id
        self._nonce = Random.get_random_bytes(4)

    @property
    def type_id(self):
        return self._type_id

    @type_id.setter
    def type_id(self, type_id: int):
        self._type_id = type_id
        if ASSERTS:
            assert type(type_id) is int
            assert type_id in self.Types.as_enum()

    def serialize(self) -> bytes:
        return struct.pack('>B', self.type_id) + self._nonce

    @staticmethod
    def deserialize(data, *args, **kwargs):
        type_id = struct.unpack(">B", data[:1])[0]
        return Message(type_id)

    def to_json(self):
        return {
            'type_id': self.type_id,
        }


class Request(Message):
    def __init__(self, type_id: int, client_id: int, remote_ipv4_address: str):
        super(Request, self).__init__(type_id)
        self.client_id = client_id
        self.remote_ipv4_address = remote_ipv4_address

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, client_id: int):
        self._client_id = client_id
        if ASSERTS:
            assert type(client_id) is int
            assert client_id > 0
            assert client_id <= 2**32

    @property
    def remote_ipv4_address(self):
        return self._ipv4_address

    @remote_ipv4_address.setter
    def remote_ipv4_address(self, address: str):
        self._ipv4_address = address
        if ASSERTS:
            assert type(address) is str
            assert len(address) > 0

    def serialize(self) -> bytes:
        return super(Request, self).serialize()

    @classmethod
    def deserialize(cls, data, *args, **kwargs):
        message = super(Request, cls).deserialize(data)
        client_id = struct.unpack(">I", data[1:5])[0]
        return Request(message.type_id, client_id, args[0])

    def to_json(self):
        j = super(Request, self).to_json()
        j.update({
            'ipv4_address': self.remote_ipv4_address,
            'client_id': self.client_id,
        })
        return j


class Response(Message):
    def __init__(self, type_id: int):
        super(Response, self).__init__(type_id)
