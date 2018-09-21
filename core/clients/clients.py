import base64
import gzip

import msgpack

from core.settings import ASSERTS


class Client:
    def __init__(self, id: int, name: str, secret: bytes):
        self.id = id
        self.name = name
        self.secret = secret
        self.ipv4_address = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: int):
        self._id = id
        if ASSERTS:
            assert type(id) is int
            assert id >= 0
            assert id <= 2**32

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        if ASSERTS:
            assert type(name) is str
            assert len(name) > 0
            assert len(name) <= 256

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, secret: bytes):
        self._secret = secret
        if ASSERTS:
            assert type(secret) is bytes
            assert len(secret) == 32

    # @property
    # def ipv4_address(self):
    #     if self._ipv4_address is not None:
    #         return socket.inet_ntoa(self._ipv4_address)
    #     else:
    #         return None
    #
    # @ipv4_address.setter
    # def ipv4_address(self, address: str or None):
    #     if address is not None:
    #         # No need to store string in memory in case of thousands of addresses.
    #         self._ipv4_address = socket.inet_aton(address)
    #     else:
    #         self._ipv4_address = None
    #
    #     if ASSERTS:
    #         assert type(address) in (str, type(None), )
    #         if address is not None:
    #             assert len(self._ipv4_address) == 4

    def serialize(self):
        """
        Serializes client to the bytes85 representation.

        :returns: serialized string representation.
        """

        return base64.b85encode(
            gzip.compress(
                msgpack.packb(
                    (self._id,
                     self._name.encode('utf-8'),
                     self._secret,
                     # self._ipv4_address,
                     ))))

    @staticmethod
    def deserialize(raw):
        """
        Deserialize raw base85 representation of the client's data.

        :param raw: encoded representation.
        :returns: deserialized client instance.
        """

        v = msgpack.unpackb(
            gzip.decompress(
                base64.b85decode(
                    raw)))

        client = Client(
            v[0],
            v[1].decode('utf-8'),
            v[2])

        # client.ipv4_address = socket.inet_ntoa(v[3]) if v[3] else None
        return client
