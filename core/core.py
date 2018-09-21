import logging

from core.clients.handler import ClientsHandler
from core.communicator.communicator import Communicator
from core.flow.processor import RequestsFlow
from core.settings import Settings


class Core:
    def __init__(self, settings: Settings):
        self._settings = settings
        self.__init_logging()
        self.__init_communicator()
        self.__init_clients_handler()
        self.__init_messages_processor()

    def run(self):
        logging.info("Operations processing started")

        while True:
            self.__process_received_requests()

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

    def __init_communicator(self) -> None:
        self._communicator = Communicator(self._settings)

    def __init_clients_handler(self) -> None:
        self._clients_handler = ClientsHandler(self._settings)

    def __init_messages_processor(self) -> None:
        self._requests_flow = RequestsFlow(self._clients_handler)

    def __process_received_requests(self) -> None:
        """
        Processes requests from clients and sends responses to them (if present).
        """

        for request in self._communicator.get_received_requests():
            for processing_response in self._requests_flow.process(request):
                self._communicator.send(
                    processing_response.encrypted_response,
                    processing_response.endpoint)
