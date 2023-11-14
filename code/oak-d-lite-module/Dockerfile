FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y wget build-essential cmake pkg-config libjpeg-dev libtiff5-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran git

RUN git clone https://github.com/luxonis/depthai/tree/main && cd depthai

# ADD docker_dependencies.sh .
RUN ./docker_dependencies.sh

# ADD . /depthai
RUN python3 install_requirements.py
