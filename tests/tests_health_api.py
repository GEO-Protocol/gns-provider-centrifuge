import unittest
import requests
from time import sleep

from core.core import Core
from core.settings import Settings


class TestsHealth(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.load_config('../conf.yaml')
        self.core = Core(self.settings)
        self.core.run_web_server()
        sleep(5)

    def tearDown(self):
        self.core.terminate()

    def test_health(self):
        r = requests.get(
            "http://127.0.0.1:"+str(self.settings.api_port)+"/api/v1/status/"
        )
        if r.json()["state"] != "operational":
            if str(r.json()["percent"]) == "-1":
                assert False, "Provider instance is not operational due cluster info not ok"
            else:
                assert False, "Provider instance is not operational due to low percentage: "+str(r.json()["percent"])
