import json


DEBUG = True
ASSERTS = True


class RedisSettings:
    def __init__(self, **params_json):
        self.host = params_json['host']
        self.port = params_json['port']
        self.db = params_json['db']

        if ASSERTS:
            assert type(self.host) is str
            assert len(self.host) != 0
            assert type(self.port) is int
            assert self.port != 0


class Settings:
    def __init__(self, **params_json):
        self.host = params_json['host']
        self.port = params_json['port']
        self.debug = params_json['debug']
        self.asserts = params_json['asserts']
        self.redis = RedisSettings(**params_json['redis'])
        self.use_centrifuge = params_json['use_centrifuge']

        if ASSERTS:
            assert type(self.host) is str
            assert len(self.host) != 0
            assert type(self.port) is int
            assert self.port != 0
            assert type(self.debug) is bool
            assert type(self.asserts) is bool
            assert type(self.use_centrifuge) is bool

    @staticmethod
    def load_config(conf_file_path='conf.json'):
        with open(conf_file_path, 'r') as content:
            s = Settings(
                **json.loads(content.read()))

            if s.debug:
                global DEBUG
                DEBUG = True

            if s.asserts:
                global ASSERTS
                ASSERTS = True

            return s
