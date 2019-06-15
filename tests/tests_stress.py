import os
import unittest
import requests
import random
import string
from time import sleep

from core.core import Core
from core.settings import Settings


class TestsMessagesRegAndUpdate(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.load_config('../conf.json')
        self.core = Core(self.settings)
        self.core.run(False)
        sleep(5)

        self.test_client_id = "1234567890"
        self.test_client_username = "test_client"
        self.test_client_key = "".join([random.choice(string.digits) for i in range(16)])

    def tearDown(self):
        self.__delete_test_client()
        self.core.terminate()

    def test_ping(self):
        self.__delete_test_client()
        r = requests.post(
            "http://127.0.0.1:"+str(self.settings.api_port)+"/api/v1/users/",
            data={
                'id': self.test_client_id,
                'username': self.test_client_username,
                'key': self.test_client_key
            }
        )
        if r.json()["status"] != "success":
            assert False, r.json()["msg"]

        print("Success: '" + str(r.json()) + "'")

    def __create_test_client(self):
        self.__delete_test_client()
        client = self.core.client_manager.create(
            self.test_client_id,
            self.test_client_username)
        self.core.client_manager.save(client)

    def __delete_test_client(self):
        client = self.core.client_manager.find_by_id(self.test_client_id)
        if not client:
            return
        self.core.client_manager.delete(client)
