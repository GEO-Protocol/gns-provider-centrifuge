import os,sys
import logging
import subprocess
import socket

from health.settings import Settings


class Check:
    def __init__(self, settings: Settings):
        self._settings = settings
        self.__init_logging()

        self.django_process = None

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

    def providers(self):
        for provider_address in self._settings.providers:
            print("provider_address="+provider_address)

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
            print("line="+str(line))
            name_val[1] = name_val[1][:-1]
            cluster_info[name_val[0]] = name_val[1]
        # cluster_info["cluster_state"] = "ok"
        return cluster_info

    @staticmethod
    def get_binding_port():
        try:
            conn_str = str(socket.gethostbyname(socket.gethostname()) + "----" + sys.argv[-1])
            conn_arr = conn_str.split(":")
            return int(conn_arr[len(conn_arr) - 1])
        except:
            return 0

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
