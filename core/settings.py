import yaml


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
    def __init__(self, **params_yaml):
        self.host = params_yaml['host']
        self.port = params_yaml['port']
        self.database = params_yaml['database']
        self.user = params_yaml['user']
        self.password = params_yaml['password']

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
    def __init__(self, **params_yaml):
        self.host = params_yaml['host']
        self.port = params_yaml['port']
        self.ping_host = params_yaml['ping_host']
        self.ping_port = params_yaml['ping_port']
        self.api_host = params_yaml['api_host']
        self.api_port = params_yaml['api_port']
        self.provider_name = params_yaml['provider_name']
        self.postgres = PostgresSettings(**params_yaml['postgres'])
        self.redis = RedisSettings(**params_yaml['redis'])
        self.instances = params_yaml['instances']

        self.debug = params_yaml['debug']
        self.asserts = params_yaml['asserts']

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

            assert type(self.debug) is bool
            assert type(self.asserts) is bool

    @staticmethod
    def load_config(conf_file_path='conf.yaml'):
        with open(conf_file_path, 'r') as stream:
            s = Settings(
                **yaml.safe_load(stream))

            if s.debug:
                global DEBUG
                DEBUG = True

            if s.asserts:
                global ASSERTS
                ASSERTS = True

            return s
