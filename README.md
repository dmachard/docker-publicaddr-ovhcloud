# What is this?

Docker image to publish your public IPv4 and V6 addresses to a list of OVH domains.

## Get your OVH credentials

Before to start, you need to create [OVH API Keys](https://eu.api.ovh.com/createToken) with the following [example](./doc/ovh_token.png) and you will be issued three keys:

- the application key
- your secret application key
- a secret consumer key

## Docker run

```bash
sudo docker run -d --env-file ./env.list --name=mon dmachard/publicaddr-ovhcloud:latest
```

## Docker build

Build docker image

```bash
sudo docker build . --file Dockerfile -t publicaddr-ovhcloud
```

## Environment variables

| Variables | Description |
| ------------- | ------------- |
| PUBLICADDR_OVHCLOUD_DEBUG | debug mode 1 or 0 |
| PUBLICADDR_OVHCLOUD_HAS_IPV6 | 1 or 0 |
| PUBLICADDR_OVHCLOUD_USE_PROTOCOL | https|dns|stun|all |
| PUBLICADDR_OVHCLOUD_UPDATE | delay between check, default is 3600s |
| PUBLICADDR_OVHCLOUD_ZONE | dns zone to update |
| PUBLICADDR_OVHCLOUD_SUBDOMAINS | list of subdomains to update, comma separated |
| PUBLICADDR_OVHCLOUD_ENDPOINT | ovh endpoint, default is ovh-eu |
| PUBLICADDR_OVHCLOUD_APPLICATION_KEY | ovh application key |
| PUBLICADDR_OVHCLOUD_APPLICATION_SECRET | ovh application secret |
| PUBLICADDR_OVHCLOUD_CONSUMER_KEY | ovh consumer key |

## Run from source

## For developpers

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

```bash
python3 -m pip install -r requirements.txt
python3 example.py -e env.list
```
