import struct


class EncryptedRequest:
    def __init__(self, remote_endpoint, client_id, binary_data):
        self.remote_endpoint = remote_endpoint
        self.client_id = client_id
        self.data = binary_data

    def serialize(self):
        return struct.pack('>BI', len(self.data), self.client_id) + self.data


class EncryptedResponse:
    def __init__(self, data: bytes):
        self.data = data

    def serialize(self):
        return struct.pack('>BI', len(self.data)) + self.data