# MiniPupper SD Card

MiniPupper uses a Raspberry Pi 4 - 4 GB compute module without embedded flash memory, it requires an SD card with the operating system and the applications to function.

This documents will guide you toward burning a working SD card for MiniPupper.

## Burn Ubuntu Server

Download Ubuntu server 22.04.03 image for Raspberry Pi

Use Raspberry Pi Imager, select credentials, SSH and Wi-Fi SSID and credentials, and burn a high quality SD card.

Plug in the SD card inside MiniPupper, detect the address of the Raspberry Pi either via an IP scanner, or by looking at the router DHCP leasing.

Update the system:

```bash
sudo apt update
sudo apt upgrade
sudo reboot
```

Clone the official MangDang repository for the robot:

```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_2_bsp.git mini_pupper_bsp
cd mini_pupper_bsp
./install.sh
sudo reboot
```

Download and install the repositories needed for the Web Controller:

```bash
cd ~
git clone https://github.com/mangdangroboticsclub/StanfordQuadruped.git
cd StanfordQuadruped
./install.sh
```

```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_web_controller.git
./mini_pupper_web_controller/webserver/install.sh
```

# Demos

Put the demos in `~/mini_pupper_bsp/demos/`.

- `test-haptic-power-readings.py`: moves front right leg, you'll see movement on other legs. Use it to test motors and motor IDs
- `test-gpio-servo.py`: moves axis 13 on ttyAMA1 500-650 to test the sprinkler piston
- `demo.py`: full demo program
