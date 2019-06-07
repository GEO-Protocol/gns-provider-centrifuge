import socket
import netstruct

from ..model.context import Context
from .base import Base


class Ping(Base):
    def __init__(self, context: Context):
        super().__init__(context)
        self.host = context.settings.ping_host
        self.port = context.settings.ping_port

    def _run(self):
        # It is necessary to init socket in the same process, that would use it,
        # to prevent data races.
        self.socket = socket.socket(
            socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDP
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))
        while True:
            # Waiting for new data
            (data, address) = self.socket.recvfrom(512)
            data = data[self.header_size:]

            # Reading client id and timestamp
            s = netstruct.NetStruct(b"<B I Q")
            (protocol_version, id, time_updated) = s.unpack(data)

            # Retrieving client from db and updating its address and timestamp
            client = self.context.client_manager.find_by_id(id)
            if client:
                if not client.time_updated or int(client.time_updated) < int(time_updated):
                    self.context.logger.info(
                        "Ping received:"+" id="+str(id)+" address="+str(address)+" time_updated="+str(time_updated))
                    client.address = address
                    client.time_updated = time_updated
                    self.context.client_manager.save(client)
                    self.send_message("OK".encode('ascii'), address)
                else:
                    self.send_message("TOO FAST".encode('ascii'), address)
            else:
                self.send_message("NOT FOUND".encode('ascii'), address)
