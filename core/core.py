import logging

from core.service.client.json import Manager as ClientManager
from core.model.context import Context
from core.settings import Settings
from core.thread.lookup import Lookup
from core.thread.ping import Ping


class Core:
    def __init__(self, settings: Settings):
        self._settings = settings
        self.__init_logging()

        self.client_manager = ClientManager("db.json", self._settings)
        self.context = Context(
            self._settings,
            self.client_manager,
            self.logger
        )

        self.ping_controller = Ping(self.context)
        self.lookup_controller = Lookup(self.context)

    def run(self):
        logging.info("Operations processing started")

        self.ping_controller.run_async()
        self.lookup_controller.run_async()

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
