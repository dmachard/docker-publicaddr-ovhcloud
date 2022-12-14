# What is this?

Docker image to publish your public IPv4 and V6 addresses to a list of OVH domains.

## Get your OVH credentials

Before to start, you need to create [OVH API Keys](https://eu.api.ovh.com/createToken) with the following [example](./doc/ovh_token.png) and you will be issued three keys:
- the application key
- your secret application key
- a secret consumer key

## Docker run

```
sudo docker run -d --env-file ./env.list --name=mon publicaddr-ovhcloud:latest
```

## Docker build

Build docker image

```
sudo docker build . --file Dockerfile -t publicaddr-ovhcloud
```

## Environment variables

| Variables | Description |
| ------------- | ------------- |
| PUBLICADDR_OVHCLOUD_DEBUG | debug mode 1 or 0 |
| PUBLICADDR_OVHCLOUD_UPDATE | delay between check, default is 3600s |
| PUBLICADDR_OVHCLOUD_ZONE | dns zone to update |
| PUBLICADDR_OVHCLOUD_SUBDOMAINS | list of subdomains to update, comma separated |
| PUBLICADDR_OVHCLOUD_ENDPOINT | ovh endpoint, default is ovh-eu |
| PUBLICADDR_OVHCLOUD_APPLICATION_KEY | ovh application key |
| PUBLICADDR_OVHCLOUD_APPLICATION_SECRET | ovh application secret |
| PUBLICADDR_OVHCLOUD_CONSUMER_KEY | ovh consumer key |

## Run from source

```
python3 -c "import publicaddr_ovhcloud as lib; lib.start_monitor();"
```