import struct

import netstruct

from core.messages.base import Request, Response, Endpoint

# todo: use netstruct


class EmptyClassDeserializationMixin:
    @classmethod
    def deserialize(cls, data, *args, **kwargs):
        return cls()


class SetAddressRequest(Request):
    def __init__(self, client_id: int, remote_ipv4_address: str, port: int):
        # todo: add comment for each one parameter
        super().__init__(self.Types.set_address, client_id, remote_ipv4_address)
        self._port = port

    @property
    def port(self):
        return self._port

    def serialize(self) -> bytes:
        return super().serialize() + struct.pack('>H', self.port)

    @staticmethod
    def deserialize(data, *args, **kwargs):
        port = struct.unpack(">H", data[:2])[0]
        return SetAddressRequest(args[0], args[1], port)

    def to_json(self):
        j = super().to_json()
        j.update({
            'port': self.port,
        })
        return j


class SetAddressAckResponse(Response, EmptyClassDeserializationMixin):
    def __init__(self):
        super().__init__(self.Types.set_address_ack)


class ParticipantLookupRequest(Request):
    def __init__(self, client_id: int, remote_ipv4_address: str, port: int, participant_name: str):
        # todo: add comment for each one parameter
        super().__init__(self.Types.participant_lookup, client_id, remote_ipv4_address)
        self._port = port
        self._participant_name = participant_name

    @property
    def port(self):
        return self._port

    @property
    def participant_name(self):
        return self._participant_name

    def serialize(self) -> bytes:
        name_encoded = self._participant_name.encode('utf-8')
        return super().serialize() + struct.pack('>HH', self.port, len(name_encoded)) + name_encoded

    @classmethod
    def deserialize(cls, data, *args, **kwargs):
        port, name_length = struct.unpack(">HH", data[:4])
        name = (data[4:name_length+4]).decode('utf-8')
        return cls(args[0], args[1], port, name)

    def to_json(self):
        j = super().to_json()
        j.update({
            'participant_name': self.participant_name,
        })
        return j


class ParticipantLookupAckResponse(Response, EmptyClassDeserializationMixin):
    def __init__(self):
        super().__init__(self.Types.participant_lookup_ack)


class ParticipantLookupNotFoundResponse(Response, EmptyClassDeserializationMixin):
    def __init__(self):
        super().__init__(self.Types.participant_lookup_not_found)


class ConnectionRequest(Response):
    def __init__(self, initiator_name: str, endpoint: Endpoint):
        super(ConnectionRequest, self).__init__(self.Types.connection_request)
        self._initiator_name = initiator_name
        self._endpoint = endpoint

    @property
    def initiator_name(self) -> str:
        return self._initiator_name

    @property
    def endpoint(self) -> Endpoint:
        return self._endpoint

    def serialize(self) -> bytes:
        return super().serialize() + \
               self.endpoint.serialize() + \
               netstruct.pack(b'H$', self._initiator_name.encode('utf-8'))

    @classmethod
    def deserialize(cls, data, *args, **kwargs):
        endpoint = Endpoint.deserialize(data[:6])
        initiator_name = netstruct.unpack('H$', data[6:])
        return ConnectionRequest(initiator_name, endpoint)
