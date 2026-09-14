# Debian 11 "bullseye" has aged out of active maintenance: its
# debian-security package pool is being pruned (some .deb files 404 while
# apt's own index still lists them), and docker-library/python's active
# branch no longer even carries a bullseye variant for this Python series.
# Moved to "bookworm" (Debian 12, current stable). See issue #119.
FROM python:3.10-bookworm

RUN apt-get update && apt-get install -y wget build-essential cmake pkg-config libjpeg-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran git

# Pin to the "main" branch explicitly: upstream changed the repository's
# default branch to "readme" (docs only), which lacks docker_dependencies.sh
# and install_requirements.py and broke the unpinned clone. See issue #104.
RUN git clone --depth 1 --branch main https://github.com/luxonis/depthai.git depthai

# docker_dependencies.sh's own Debian/Ubuntu package list (fetched live from
# upstream, so it can't be edited directly) still names two packages Debian
# has since dropped from bookworm: `libtbb2` (obsoleted outright; the
# `libtbb-dev` entry already listed alongside it covers the same need) and
# `libdc1394-22-dev` (renamed to `libdc1394-dev`). Patch the cloned copy
# in place before running it. See issue #119.
RUN sed -i \
    -e '/^\s*libtbb2\s*$/d' \
    -e 's/\blibdc1394-22-dev\b/libdc1394-dev/' \
    depthai/docker_dependencies.sh

RUN ./depthai/docker_dependencies.sh

RUN useradd -m depthai
USER depthai

RUN python3 ./depthai/install_requirements.py

WORKDIR /

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

HEALTHCHECK CMD curl -f http://localhost:9090/ || exit 1

CMD ["python3", "/oak-d-lite-module/vision_webserver.py"]
