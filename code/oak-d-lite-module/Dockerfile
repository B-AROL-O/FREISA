FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y wget build-essential cmake pkg-config libjpeg-dev libtiff5-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran git

RUN git clone https://github.com/luxonis/depthai.git depthai

RUN ./depthai/docker_dependencies.sh

RUN python3 ./depthai/install_requirements.py

WORKDIR /
COPY requirements.txt .
RUN pip3 install --no-cache -r requirements.txt
