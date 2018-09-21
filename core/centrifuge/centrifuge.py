import logging
import socket
from multiprocessing import Process
from time import sleep

from Crypto import Random

from core.clients.handler import ClientsHandler
from core.crypto.cipher import AESCipher
from core.messages.common import PingResponse
from core.messages.encrypted import EncryptedResponse
from core.settings import Settings, DEBUG


class Centrifuge:
    timeout = 5    # seconds

    def __init__(self, settings: Settings):
        self._settings = settings
        self._cipher = AESCipher()

    def run_async(self):
        self._process = Process(target=self._run)
        self._process.start()

    def _run(self):
        # It is necessary to seed random in forked process,
        # otherwise - Crypto would throw an error.
        Random.atfork()

        # It is necessary to init socket in the same process, that would use it,
        # to prevent data races.
        self.socket = socket.socket(
            socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDP

        # To prevent concurrent redis pool usage - centrifuge init's it's own clients handler.
        clients = ClientsHandler(self._settings)

        while True:
            sleep(self.timeout)
            for client_id in clients.get_all_clients_ids():
                client = clients.get_by_id(client_id)
                if not client:
                    pass

                addresses_and_ports = clients.get_ipv4_addresses_and_ports(client.id)
                if not addresses_and_ports:
                    pass

                for address, port in addresses_and_ports:
                    ping = PingResponse()
                    enc = EncryptedResponse(ping.serialize())
                    self.socket.sendto(enc.data, (address, port))

                    if DEBUG:
                        logging.info(f'PING sent to {address}:{port}')

