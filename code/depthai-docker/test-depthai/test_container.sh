#!/bin/bash
docker run --rm \
    --privileged \
    --name=shoot-on-oak-d-lite \
    -v /dev/bus/usb:/dev/bus/usb \
    -v "$HOME"/oak-d-lite-photos/container:/photo-capture/ \
    -v "$HOME"/test-depthai:/test-depthai/ \
    --device-cgroup-rule='c 189:* rmw' \
    depthai-test:latest \
    python3 /test-depthai/photo-saver.py
