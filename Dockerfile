FROM python:3.13.5-alpine

LABEL name="Python PublicAddr Updater for OVHcloud" \
      description="Python PublicAddr Updater for OVHcloud" \
      url="https://github.com/dmachard/publicaddr-ovhcloud" \
      maintainer="d.machard@gmail.com"

WORKDIR /home/monitor
COPY . /home/monitor/

RUN apk update \
    && adduser -D monitor \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

USER monitor

ENTRYPOINT ["python", "-c", "import publicaddr_ovhcloud as lib; lib.start_monitor();"]