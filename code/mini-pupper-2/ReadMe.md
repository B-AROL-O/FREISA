# MiniPupper SD Card
MiniPupper uses a Raspberry Pi 4 - 4GB compute module without embedded flash memory, it requires an SD card with the operating system and the application to function.

This documents will guide you toward buring a working SD card for MiniPupper.

## Burn Ubuntu Server

Download ubuntu server 22.04.03 image for Raspberry Pi

Use RaspberryPi Imager, select credentials, SSH and WiFi SSID and credentials, and burn an high quality SD card.

Plug in the SD card inside mini pupper, detect the address of the Raspberry Pi either via an IP scanner, or by looking at the router DHCP leasing.

sudo apt update
sudo apt upgrade
sudo reboot

cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_2_bsp.git mini_pupper_bsp
cd mini_pupper_bsp
./install.sh
sudo reboot

Repositories needed for the Web Controller

cd ~
git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git
cd StanfordQuadruped
./install.sh

cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_web_controller.git
./mini_pupper_web_controller/webserver/install.sh

# Demos

Put the demos in ~/mini_pupper_bsp/demos/

- test-haptic-power-readings.py : move front right leg, you'll see movement on other legs. Use it to test motors and motor IDs
- test-gpio-servo.py : moves axis 13 on ttyAMA1 500-650 to test the sprinkler piston
- demo.py: Demo