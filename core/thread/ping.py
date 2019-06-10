import socket
import netstruct

from ..model.context import Context
from .base import Base


class Ping(Base):
    def __init__(self, context: Context):
        super().__init__(context)
        self.host = context.settings.ping_host
        self.port = context.settings.ping_port

    def send_error(self, data, address):
        # self.send_message(data, address)
        pass

    def _run(self):
        # It is necessary to init socket in the same process, that would use it,
        # to prevent data races.
        self.socket = socket.socket(
            socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDP
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))
        while True:
            # Waiting for new data
            (data, address) = self.socket.recvfrom(512)
            data = data[self.header_size:]

            # Reading client id and timestamp
            s = netstruct.NetStruct(b"<B I Q")
            (protocol_version, id, time_updated) = s.unpack(data)

            if protocol_version != self.protocol_version:
                self.context.logger.info("PROTOCOL VERSION ERROR: "+protocol_version)
                self.send_error(("PROTOCOL VERSION ERROR: "+protocol_version).encode('ascii'), address)
                continue

            # Retrieving client from db and updating its address and timestamp
            client = self.context.client_manager.find_by_id(id)
            if client:
                print("PING 1: username=" + client.username + " address=" + str(client.address))
                if not client.time_updated or int(client.time_updated) < int(time_updated):
                    self.context.logger.info(
                        "Ping received:"+" id="+str(id)+" address="+str(address)+" time_updated="+str(time_updated))
                    client.address = address
                    client.time_updated = time_updated
                    self.context.client_manager.save(client, True)
                    print("PING 2: username=" + client.username + " address=" + str(client.address))
                    self.send_error("OK".encode('ascii'), address)
                else:
                    self.context.logger.info("TOO FAST")
                    self.send_error("TOO FAST".encode('ascii'), address)
            else:
                self.context.logger.info("NOT FOUND")
                self.send_error("NOT FOUND".encode('ascii'), address)
