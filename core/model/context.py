
class Context:
    def __init__(
            self,
            settings,
            client_manager,
            logger
    ):
        self.settings = settings
        self.client_manager = client_manager
        self.logger = logger
        self.settings.logger = self.logger
