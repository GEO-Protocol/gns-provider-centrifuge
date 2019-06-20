import os
import unittest
import requests
import random
import string
import time

from core.core import Core
from core.settings import Settings
import client as client_pkg


class TestsMessagesRegAndUpdate(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.load_config('../conf.yaml')
        self.core = Core(self.settings)
        self.core.run_threads()
        time.sleep(0.5)

        self.test_clients_count = 100
        self.test_clients_start_id = 1234567000
        self.test_clients = []
        print("Creating "+str(self.test_clients_count)+" test clients...")
        for i in range(self.test_clients_count):
            test_client = self.__TestClient(self.core.client_manager, self.test_clients_start_id+i)
            self.test_clients.append(test_client)
            test_client.create()

    def tearDown(self):
        print("Deleting "+str(self.test_clients_count)+" test clients...")
        for test_client in self.test_clients:
            test_client.delete()
        self.core.terminate()

    def test_ping(self):
        start_time = time.time()

        for test_client in self.test_clients:
            client_pkg.send_ping(self.settings.ping_host, self.settings.ping_port, test_client.test_client_id)
            time.sleep(0.005)

        hours, rem = divmod(time.time() - start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        print("Finished in {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    def test_lookup(self):
        for test_client in self.test_clients:
            client_pkg.send_ping(self.settings.ping_host, self.settings.ping_port, test_client.test_client_id, False)
            time.sleep(0.005)

        start_time = time.time()

        for test_client in self.test_clients:
            client_pkg.send_lookup(
                self.settings.provider_name, self.settings.host, self.settings.port,test_client.test_client_username)
            time.sleep(0.005)

        hours, rem = divmod(time.time() - start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        print("Finished in {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    class __TestClient:
        def __init__(self, client_manager, id):
            self._client_manager = client_manager
            self.test_client_id = id
            self.test_client_username = "test_client_"+str(id)
            self.test_client_key = "".join([random.choice(string.digits) for i in range(16)])

        def create(self):
            self.delete()
            client = self._client_manager.create(
                self.test_client_id,
                self.test_client_username)
            self._client_manager.save(client)

        def delete(self):
            client = self._client_manager.find_by_id(self.test_client_id)
            if not client:
                return
            self._client_manager.delete(client)
