FROM ghcr.io/tiryoh/ros2-desktop-vnc:humble

ARG USERNAME

USER root

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt update && apt autoremove -y
RUN apt-get -y install --no-install-recommends tar curl zip unzip

RUN useradd -ms /bin/bash $USERNAME
RUN usermod -aG sudo $USERNAME
RUN mkdir -p "/etc/sudoers.d"]
RUN echo "$USERNAME ALL=(ALL:ALL) NOPASSWD: ALL" | tee "/etc/sudoers.d/$USERNAME"
COPY ./entrypoint.sh /entrypoint.sh

ENV USER ubuntu
ENV PASSWD ubuntu

ENTRYPOINT ["/bin/bash", "-c", "/entrypoint.sh"]
