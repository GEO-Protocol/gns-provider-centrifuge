import time


class Client:
    def __init__(self, id=None, username=None):
        self.id = id
        self.username = username
        self.address = None
        self.time_created = time.time()
        self.time_updated = None
