import sys
import getopt

from core.core import Core
from core.settings import Settings
from core.thread.lookup import Lookup
from core.thread.ping import Ping

from health.settings import Settings as HealthSettings
from health import Check


def usage():
    print("Usage:")
    print("\tpython server.py [-v] [-m mode]")
    print("\t\t [-m --mode] : ping, lookup, rest, all, health")
    print("Example:")
    print("\tpython server.py ")


if __name__ == '__main__':
    verbose = False
    mode = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:v", ["help", "mode", "verbose"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-m", "--mode"):
            mode = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    if not mode:
        mode = "all"

    if mode == "health":
        health_settings = HealthSettings.load_config()
        health_check = Check(health_settings)
        health_check.run()
        health_check.wait()
    else:
        settings = Settings.load_config()
        core = Core(settings)
        if mode == "ping":
            core.run_ping()
        elif mode == "lookup":
            core.run_lookup()
        elif mode == "rest":
            core.run(False)
        elif mode == "all":
            core.run()
        else:
            core.run()
        core.wait()
