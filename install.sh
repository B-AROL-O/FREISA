#!/bin/bash
# ===========================================================================
# Project: FREISA
#
# Description: Install FREISA software stack on a brand new Mini Pupper 2
# ===========================================================================

set -e
# set -x

# export BASEDIR=$HOME
export BASEDIR=$PWD

cd $BASEDIR

echo "INFO: Updating Operating System packages"
sudo apt update && sudo apt -y dist-upgrade && sudo apt -y autoremove --purge

echo "INFO: Updating $BASEDIR/FREISA"
if [ ! -e FREISA ]; then
    git clone --depth 1 \
        -b main \
        -o origin \
        https://github.com/B-AROL-O/FREISA.git \
        FREISA
fi
cd FREISA
git pull --all --prune
git describe --all --dirty
cd -

echo "INFO: Updating $BASEDIR/mini_pupper_bsp"
if [ ! -e mini_pupper_bsp ]; then
    git clone --depth 1 \
        -b mini_pupper_2pro_bsp \
        -o upstream \
        https://github.com/mangdangroboticsclub/mini_pupper_2_bsp.git \
        mini_pupper_bsp
fi
cd mini_pupper_bsp
git pull --all --prune
git status
git describe --all --dirty
cd -

echo "INFO: Updating $BASEDIR/mini_pupper_ros"
if [ ! -e mini_pupper_ros ]; then
    git clone --depth 1 \
        -b ros2-dev \
        -o origin \
        https://github.com/B-AROL-O/mini_pupper_ros.git \
        mini_pupper_ros
fi
cd mini_pupper_ros
git pull --all --prune
git status
git describe --all --dirty
cd -

echo "INFO: Updating $BASEDIR/mini_pupper_web_controller"
if [ ! -e mini_pupper_web_controller ]; then
    git clone --depth 1 \
        -b main \
        -o upstream \
        https://github.com/mangdangroboticsclub/mini_pupper_web_controller.git \
        mini_pupper_web_controller
fi
cd mini_pupper_web_controller
git pull --all --prune
git status
git describe --all --dirty
cd -

# TODO

# EOF