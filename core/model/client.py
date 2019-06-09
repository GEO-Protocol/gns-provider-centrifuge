import time


class Client:
    def __init__(self, id=None, username=None):
        # db fields
        self.id = id
        self.username = username
        self.secret = None
        self.time_created = time.time()

        # redis fields
        self.address = None
        self.time_updated = None
