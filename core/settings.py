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


class PostgresSettings:
    def __init__(self, **params_json):
        self.host = params_json['host']
        self.port = params_json['port']
        self.database = params_json['database']
        self.user = params_json['user']
        self.password = params_json['password']

        if ASSERTS:
            assert type(self.host) is str
            assert len(self.host) != 0
            assert type(self.port) is int
            assert self.port != 0
            assert type(self.database) is str
            assert len(self.database) != 0
            assert type(self.user) is str
            assert len(self.user) != 0
            assert type(self.password) is str
            assert len(self.password) != 0


class Settings:
    def __init__(self, **params_json):
        self.host = params_json['host']
        self.port = params_json['port']
        self.ping_host = params_json['ping_host']
        self.ping_port = params_json['ping_port']
        self.api_host = params_json['api_host']
        self.api_port = params_json['api_port']
        self.provider_name = params_json['provider_name']
        self.database_name = params_json['database_name']
        self.debug = params_json['debug']
        self.asserts = params_json['asserts']
        self.postgres = PostgresSettings(**params_json['postgres'])
        self.redis = RedisSettings(**params_json['redis'])
        self.use_centrifuge = params_json['use_centrifuge']

        if ASSERTS:
            assert type(self.host) is str
            assert len(self.host) != 0
            assert type(self.port) is int
            assert self.port != 0

            assert type(self.ping_host) is str
            assert len(self.ping_host) != 0
            assert type(self.ping_port) is int
            assert self.ping_port != 0

            assert type(self.api_host) is str
            assert len(self.api_host) != 0
            assert type(self.api_port) is int
            assert self.api_port != 0

            assert type(self.provider_name) is str
            assert len(self.provider_name) != 0

            assert type(self.database_name) is str
            assert len(self.database_name) != 0

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
