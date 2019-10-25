import os,sys
import logging
import subprocess
import socket
import redis

from core.settings import Settings
from core.service.client.postgres import Manager as ClientManager
import client as client_pkg


class Check:
    def __init__(self, settings: Settings):
        self._settings = settings
        self.__init_logging()

        self.client_manager = ClientManager(self._settings)

        self._redis_pool = redis.ConnectionPool(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db)

        self.django_process = None

    def _redis(self):
        return redis.Redis(connection_pool=self._redis_pool)

    def run(self):
        self.run_web_server()

    def run_web_server(self):
        logging.info("WebServer for health check started")
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules[Settings.__module__].__file__)))
        self.django_process = subprocess.Popen([
            "python", "-u",
            "manage.py",
            "runserver",
            str(self._settings.api_host) + ":" + str(self._settings.api_port)
        ], bufsize=0, cwd=root_path)

    def wait(self):
        if self.django_process:
            self.django_process.wait()

    def _random_client(self):
        client = None
        tries_count = 0
        tries_max = 5
        while True:
            client_id = self._redis().randomkey()
            try:
                client_id = int(client_id)
            except:
                return None
            print("Random redis key: "+str(client_id))
            client = self.client_manager.find_by_id(client_id)
            if not client and tries_count < tries_max:
                tries_count += 1
                continue
            return client

    def providers(self):
        client = self._random_client()
        if not client:
            return 0
        print("Picked random client: " + str(client.id) + " : " + client.username)
        providers_checked = 0
        for provider_address in self._settings.instances:
            host_and_port = provider_address.split(':')
            print("Checking provider by address: "+host_and_port[0]+":"+host_and_port[1])
            response = client_pkg.send_lookup(
                self._settings.provider_name,
                host_and_port[0], int(host_and_port[1]),
                client.username, self._settings.gns_address_separator, wait_seconds_for_response=1)
            if response:
                providers_checked += 1
        print("providers_checked="+str(providers_checked))
        print("len(self._settings.instances)="+str(len(self._settings.instances)))
        percent = int(
            (float(providers_checked) / float(len(self._settings.instances))) * 100
        )
        return percent

    def load_cluster_info(self):
        output = subprocess.check_output([
            'redis-cli',
            '-h', str(self._settings.redis.host),
            '-p', str(self._settings.redis.port),
            'CLUSTER', 'INFO'])
        output = output.decode('UTF-8')
        output = output.split("\n")
        cluster_info = {}
        for line in output:
            name_val = line.split(":")
            if len(name_val) < 2:
                continue
            name_val[1] = name_val[1][:-1]
            cluster_info[name_val[0]] = name_val[1]
        # cluster_info["cluster_state"] = "ok"
        return cluster_info

    def __init_logging(self) -> None:
        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler('operations.log')
        errors_handler = logging.FileHandler('errors.log')
        errors_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter('%(asctime)s: %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        errors_handler.setFormatter(formatter)

        self.logger = logging.getLogger()
        self.logger.addHandler(file_handler)
        self.logger.addHandler(errors_handler)
        self.logger.addHandler(stream_handler)

        if self._settings.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    @staticmethod
    def get_binding_port():
        try:
            conn_str = str(socket.gethostbyname(socket.gethostname()) + "----" + sys.argv[-1])
            conn_arr = conn_str.split(":")
            return int(conn_arr[len(conn_arr) - 1])
        except:
            return 0
