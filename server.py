from core.core import Core
from core.settings import Settings


if __name__ == '__main__':
    settings = Settings.load_config()
    core = Core(settings).run()
