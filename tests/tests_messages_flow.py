import os
import socket
import struct
import unittest
from multiprocessing import Process
from time import sleep

from Crypto import Random

from core.clients.clients import Client
from core.core import Core
from core.crypto.cipher import AESCipher
from core.messages.base import Request, Message
from core.messages.common import SetAddressRequest, ParticipantLookupRequest
from core.settings import Settings


class TestsMessagesFlow(unittest.TestCase):
    aes = AESCipher()
    secret = b'11111111111111111111111111111111'

    @classmethod
    def setUpClass(cls):
        cls.port = 4000
        cls.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls.socket.bind(('127.0.0.1', cls.port))
        cls.socket.settimeout(2)

    @classmethod
    def tearDownClass(cls):
        cls.socket.close()

    def setUp(self):
        self.settings = Settings.load_config('../conf.json')

        # Centrifuge uses it's own internal process.
        # During running the tests this process prevents correct server shutdown and socket does not returns port.
        # To prevent it - centrifuge should be simply disabled.
        # (it is not used in this tests)
        self.settings.use_centrifuge = False

        self.core = Core(self.settings)

        def run():
            # It is necessary to seed random in forked process,
            # otherwise - Crypto would throw an error.
            Random.atfork()

            self.core.run()

        self.process = Process(target=run)
        self.process.start()

        # Wait until server would be stopped.
        sleep(0.5)

    def tearDown(self):
        self.core._communicator.socket.close()
        os.kill(self.process.pid, 15)
        os.kill(self.process.pid, 9)

        # Wait until server would be started.
        sleep(0.5)

    def test_set_address(self):
        client = self.__generate_client()
        self.__send_request(
            SetAddressRequest(client.id, '127.0.0.1', self.port))

        self.assertEqual(self.__read_response(), Message.Types.set_address_ack)

    def test_set_address_invalid_port(self):
        client = self.__generate_client()
        self.__send_request(
            SetAddressRequest(client.id, '127.0.0.1', 0))

        self.assertIsNone(self.__read_response())

    def test_participant_lookup(self):
        c1 = self.__generate_client(id=1)
        c2 = self.__generate_client(id=2, name='test_lookup')
        self.__send_request(
            ParticipantLookupRequest(c1.id, '127.0.0.1', self.port, c2.name))

        self.assertEqual(self.__read_response(), Message.Types.participant_lookup_ack)
        self.assertEqual(self.__read_response(), Message.Types.connection_request)

    def test_participant_lookup_very_long_name(self):
        # todo: add constraint to the specs, that participant name can't be greater than 214 symbols.

        c1 = self.__generate_client(id=1)
        c2 = self.__generate_client(id=2, name='t'*214)
        self.__send_request(
            ParticipantLookupRequest(c1.id, '127.0.0.1', self.port, c2.name))

        self.assertEqual(self.__read_response(), Message.Types.participant_lookup_ack)
        self.assertEqual(self.__read_response(), Message.Types.connection_request)

    def test_get_all_clients(self):
        self.__generate_client(id=1, name='c1')
        self.__generate_client(id=2, name='c2')
        self.__generate_client(id=3, name='c3')

        clients_ids = self.core._clients_handler.get_all_clients_ids()
        self.assertEqual(len(clients_ids), 3)

    def __generate_client(self, id=1, name='test'):
        client = Client(id, name, self.secret)
        self.core._clients_handler.set_ipv4_address(client, '127.0.0.1', self.port)
        return client

    def __send_request(self, message: Request):
        content = self.aes.encrypt(message.serialize(), self.secret)
        data = bytes(bytearray([len(content)])) + struct.pack('>I', message.client_id) + content
        self.socket.sendto(data, (self.settings.host, self.settings.port))

    def __read_response(self):
        try:
            content, address = self.socket.recvfrom(4096)
            dec_content = self.aes.decrypt(content, self.secret)
            type_id, nonce = struct.unpack('>BI', dec_content[:5])
            return type_id

        except:
            return None
