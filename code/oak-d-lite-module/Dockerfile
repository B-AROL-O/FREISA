FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y wget build-essential cmake pkg-config libjpeg-dev libtiff5-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran git

# Pin to the "main" branch explicitly: upstream changed the repository's
# default branch to "readme" (docs only), which lacks docker_dependencies.sh
# and install_requirements.py and broke the unpinned clone. See issue #104.
RUN git clone --depth 1 --branch main https://github.com/luxonis/depthai.git depthai

RUN ./depthai/docker_dependencies.sh

RUN useradd -m depthai
USER depthai

RUN python3 ./depthai/install_requirements.py

WORKDIR /

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

HEALTHCHECK CMD curl -f http://localhost:9090/ || exit 1

CMD ["python3", "/oak-d-lite-module/vision_webserver.py"]
