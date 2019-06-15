import os,sys
import logging
import subprocess

from core.model.context import Context
from core.service.client.json import Manager as ClientManager
from core.thread.lookup import Lookup
from core.thread.ping import Ping

from core.settings import Settings


class Core:
    def __init__(self, settings: Settings):
        self._settings = settings
        self.__init_logging()

        self.client_manager = ClientManager(self._settings)
        self.context = Context(
            self._settings,
            self.client_manager,
            self.logger
        )

        self.ping_controller = None
        self.lookup_controller = None

        self.ping_process = None
        self.lookup_process = None
        self.django_process = None

        # self.pool = multiprocessing.Pool()
        # self.ctx = multiprocessing.get_context("spawn")  # Use process spawning instead of fork
        # self.pool = self.ctx.Pool()

    def run(self):
        self.run_threads()
        self.run_web_server()

    def run_threads(self):
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules[Settings.__module__].__file__)))
        self.ping_process = subprocess.Popen([
            "python", "-u",
            "server.py",
            "-m",
            "ping"
        ], bufsize=0, cwd=root_path)

        root_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules[Settings.__module__].__file__)))
        self.lookup_process = subprocess.Popen([
            "python", "-u",
            "server.py",
            "-m",
            "lookup"
        ], bufsize=0, cwd=root_path)

    def run_web_server(self):
        logging.info("WebServer started")
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules[Settings.__module__].__file__)))
        self.django_process = subprocess.Popen([
            "python", "-u",
            "manage.py",
            "runserver",
            str(self._settings.api_host) + ":" + str(self._settings.api_port)
        ], bufsize=0, cwd=root_path)

    def run_ping(self):
        self.ping_controller = Ping(self.context)
        self.ping_controller.run()

    def run_lookup(self):
        self.lookup_controller = Lookup(self.context)
        self.lookup_controller.run()

    def wait(self):
        if self.ping_process:
            self.ping_process.wait()
        if self.lookup_process:
            self.lookup_process.wait()
        if self.django_process:
            self.django_process.wait()

    def terminate(self):
        if self.ping_process:
            self.ping_process.terminate()
        if self.lookup_process:
            self.lookup_process.terminate()
        if self.django_process:
            self.django_process.terminate()

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
