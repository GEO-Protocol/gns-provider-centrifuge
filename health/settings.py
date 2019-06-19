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


class Settings:
    def __init__(self, **params_yaml):
        self.api_host = params_yaml['api_host']
        self.api_port = params_yaml['api_port']
        self.debug = params_yaml['debug']
        self.asserts = params_yaml['asserts']
        self.redis = RedisSettings(**params_yaml['redis'])

        self.providers = params_yaml['providers']

        if ASSERTS:
            assert type(self.api_host) is str
            assert len(self.api_host) != 0
            assert type(self.api_port) is int
            assert self.api_port != 0

            assert type(self.debug) is bool
            assert type(self.asserts) is bool

    @staticmethod
    def load_config(conf_file_path='conf_health.yaml'):
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
