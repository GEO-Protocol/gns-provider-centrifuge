import socket
import struct

from core.communicator.exceptions import TooLongMessageError
from core.messages.base import Request, Endpoint
from core.messages.encrypted import EncryptedRequest, EncryptedResponse
from core.settings import Settings


class Communicator:
    """
    Implements network communication layer (data transferring).
    Does not implement encryption.

    todo: add IPv6 support.
    """

    socket_timeout = 0.2

    def __init__(self, settings: Settings):
        self.__init_socket(settings)

    def get_received_requests(self) -> [Request]:
        """
        :returns:
            list of encrypted requests, that was received from the socket.
            In case if no requests was received - returns empty list.
        """

        data, remote_endpoint = self.__read_from_socket()
        if not data:
            return []

        messages = []
        try:
            total_bytes_processed = 0
            while total_bytes_processed < len(data):

                # noinspection PyTypeChecker
                message, bytes_processed = self.__try_collect_message(
                    data, remote_endpoint, total_bytes_processed)

                messages.append(message)
                total_bytes_processed += bytes_processed

        except TooLongMessageError:
            # In case if some message would be recognized as to long to fit into one packet -
            # return already collected messages and stop processing of rest data,
            # because the rest bytes flow is invalid.
            return messages

        return messages

    def send(self, response: EncryptedResponse, endpoint: Endpoint) -> None:
        """
        Writes encrypted response to the socket.

        :param response: encrypted data, that should be sent to the endpoint.
        :param endpoint: address and port to which the data should be sent.
        """
        self.socket.sendto(response.data, (endpoint.ipv4_address, endpoint.port))

    def __init_socket(self, settings: Settings):
        self.socket = socket.socket(
            socket.AF_INET,         # Internet
            socket.SOCK_DGRAM)      # UDP

        self.socket.bind((settings.host, settings.port, ))
        self.socket.settimeout(self.socket_timeout)

    def __read_from_socket(self) -> (bytes, tuple):
        """
        :returns:
            data, that was received to the socket,
            and pair <ipv4_address, port> from wich data was received.
        """

        try:
            return self.socket.recvfrom(512)

        except socket.timeout as e:
            # In case if socket reported error - raise it upper.
            if e.args[0] != 'timed out':
                raise e

            # Socket reported timeout error.
            # No messages can be parsed, but the error itself should be ignored.
            return None, None

    @staticmethod
    def __try_collect_message(raw_data: bytes,
                              remote_endpoint: tuple,
                              next_message_index: int) -> (Request, int):
        """
        :param raw_data: binary data received from the socket.
        :param next_message_index: position from which message parsing must be started.
            In case if several messages are present in the "raw_data" -
            this method must be called several times with different "first_byte_index".

        :return: collected message and count of bytes processed.
        """

        message_size, client_id = struct.unpack('>BI', raw_data[next_message_index:next_message_index + 5])
        if message_size > len(raw_data):
            # todo: [improvement] add messages separation support
            raise TooLongMessageError('At this moment message partitioning is not supported')

        header_size = 5
        bytes_processed = header_size + message_size
        data = raw_data[
               next_message_index + header_size:
               next_message_index + bytes_processed]

        return EncryptedRequest(remote_endpoint, client_id, data), bytes_processed
