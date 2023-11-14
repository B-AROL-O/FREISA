#!/bin/bash
docker run --rm \
    --privileged \
    --name=oak-d-lite-server \
    -v /dev/bus/usb:/dev/bus/usb \
    -v .:/oak-d-lite-module/ \
    --device-cgroup-rule='c 189:* rmw' \
    depthai-test:latest \
    python3 /oak-d-lite-module/vision_webserver.py
