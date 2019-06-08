import socket
import struct
import netstruct

from ..model.context import Context
from .base import Base


class Lookup(Base):
    def __init__(self, context: Context):
        super().__init__(context)
        self.host = context.settings.host
        self.port = context.settings.port

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
            # print("data=" + self.bytes_to_str(data))

            # Reading username and provider name
            s = netstruct.NetStruct(b"<B H")
            (protocol_version, username_len,) = s.unpack(data)
            print("protocol_version=" + str(protocol_version) + " username_len=" + str(username_len))
            username = data[3:3+username_len].decode('ascii')
            try:
                (username, provider) = username.split('@')
            except:
                self.send_message("WRONG FORMAT".encode('ascii'), address)
                continue

            # Check if provider name matches our provider's name
            if provider != self.context.settings.provider_name:
                self.send_message("UNKNOWN PROVIDER".encode('ascii'), address)
                continue

            client = self.context.client_manager.find_by_username(username)
            if client:
                if not client.address:
                    self.send_message("NO ADDRESS YET".encode('ascii'), address)
                    continue

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
                ret_data += data

                # Packing client address: IP and PORT
                client_address = client.address[0] + str(client.address[1])
                ret_data += struct.pack("<B", len(client_address))
                ret_data += client_address.encode('ascii')

                # Sending packed data back as a response
                self.send_message(ret_data, address)
            else:
                self.send_message("NOT FOUND".encode('ascii'), address)
