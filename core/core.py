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

        self.ping_controller = Ping(self.context)
        self.lookup_controller = Lookup(self.context)
        self.django_process = None

        # self.pool = multiprocessing.Pool()
        # self.ctx = multiprocessing.get_context("spawn")  # Use process spawning instead of fork
        # self.pool = self.ctx.Pool()

    def run(self, run_threads=True):
        # print("django version: "+django.get_version())
        logging.info("Operations processing started")
        print()

        if run_threads:
            self.ping_controller.run_async()
            self.lookup_controller.run_async()

        root_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.modules[Settings.__module__].__file__)))
        self.django_process = subprocess.Popen([
            "python", "-u",
            "manage.py",
            "runserver",
            str(self._settings.api_host) + ":" + str(self._settings.api_port)
        ], bufsize=0, cwd=root_path)

    def terminate(self):
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
