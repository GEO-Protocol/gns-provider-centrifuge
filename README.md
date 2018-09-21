![](https://docs.google.com/drawings/d/e/2PACX-1vTd6yjvZnmWHmcmUSKvpUW6GCkEogxluJNmefFI0_r-SZV8pHxk1yrw52XNHgv1tUvqKr1Ta6lDsFjc/pub?w=933&h=419)

</br>

# Overview
This repository is part of [GNS ecosystem](https://github.com/GEO-Protocol/specs-gns).   
It provides infrastructure component for the providers, that allows NAT traversing [todo: add link to specs] for some categories of mobile users.

</br>
</br>

# Deployment
### Requirements
* Public IPv4 address (IPv6 is also [planned](https://github.com/GEO-Protocol/gns_provider_centrifuge/issues/1)) if you plan to provide world-wide available service;
* [Redis server](https://redis.io/) or [redis cluster](https://redis.io/topics/partitioning), if you plan to deploy multiple instances;
* python 3.6+ (see [requirements.txt](https://github.com/GEO-Protocol/gns_provider_centrifuge/blob/master/requirements.txt))

### Installation
1. `cd <target directory>`
1. `git clone https://github.com/GEO-Protocol/gns_provider_centrifuge.git ./`
1. `virtualenv -p /usr/bin/python3.5 venv`
1. `source venv/bin/activate`
1. [optional] `pip install pip --upgrade`
1. `pip install -r requirements.txt`
1. Edit `conf.json` according to your environment. (`nano conf.json`)
1. Run centrifuge `python server.py`

##### Example of conf.json
```json
{
  "asserts": true,
  "debug": false,
  "host": "0.0.0.0",
  "port": 9000,
  "redis": {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 0
  },
  "use_centrifuge": true
}
```

### Systemd service
It is recommended to run the server as a `systemd` service to automatically reload it in case of any failure.

##### Example of systemd.service
```ini
[Unit]
Description=GNS Centrifuge Instance
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=10

[Service]
Type=simple
Restart=always
RestartSec=5
User=<user>
ExecStart=/<___destination dir___>/venv/bin/python /<___destination dir___>/server.py 
WorkingDirectory=/<___destination dir___>/
```
