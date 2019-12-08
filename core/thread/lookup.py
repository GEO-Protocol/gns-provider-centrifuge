import socket
import struct
import netstruct
import time

from ..model.context import Context
from .base import Base


class Lookup(Base):
    def __init__(self, context: Context):
        super().__init__(context)
        self.host = context.settings.host
        self.port = context.settings.port

    def send_error(self, data, address):
        # self.send_message(data, address)
        pass

    def run(self):
        self.context.logger.info("LookupController started at port: " + str(self.port))
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

            # Reading username and provider name
            s = netstruct.NetStruct(b"<B H")
            (protocol_version, username_len,) = s.unpack(data)

            if protocol_version != self.protocol_version:
                self.context.logger.info("PROTOCOL VERSION ERROR: "+protocol_version)
                self.send_error(("PROTOCOL VERSION ERROR: "+protocol_version).encode('ascii'), address)
                continue

            user_address = data[3:3+username_len].decode('ascii')
            try:
                (username, provider) = user_address.split(self.context.settings.gns_address_separator)
            except:
                self.send_error("WRONG FORMAT".encode('ascii'), address)
                continue

            # Check if provider name matches our provider's name
            if provider != self.context.settings.provider_name:
                self.send_error("UNKNOWN PROVIDER".encode('ascii'), address)
                continue

            client = self.context.client_manager.find_by_username(username)
            if client:
                if not client.address:
                    self.send_error("NO ADDRESS YET".encode('ascii'), address)
                    continue

                if self.context.settings.debug:
                    self.context.logger.info(
                        "Lookup received:" + " username='" + username + "'" + " provider='" + provider + "'")

                # Hard-coding, for now
                protocol_version = 0
                max_unsigned_32 = 4294967295
                message_type = 800

                # Packing protocol version, message type and other integers
                values = (protocol_version, max_unsigned_32, message_type)
                s = struct.Struct("<B I H")
                ret_data = s.pack(*values)

                # Packing request string (username@provider_name)
                ret_data += struct.pack("<H", len(user_address))
                ret_data += user_address.encode('ascii')

                # Packing client address: IP and PORT
                client_address = client.address[0] + ":" + str(client.address[1])
                ret_data += struct.pack("<B", len(client_address))
                ret_data += client_address.encode('ascii')

                # Sending packed data back as a response
                self.send_message(ret_data, address)
            else:
                self.send_error("NOT FOUND".encode('ascii'), address)
