#!/bin/bash

apt update && apt upgrade -y

apt install python3-pip

cd /workspaces/ || exit 1
