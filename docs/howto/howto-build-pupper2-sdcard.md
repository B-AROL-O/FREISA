# INTRODUCTION

I need to build an headless image for the SD card for the Pupper 2 with ROS2

# INSTRUCTIONS

## Download Raspberry Pi Imager

The easiest way to burn an image is to use Raspberry Pi Imager

[Raspberry Pi Imager](https://www.raspberrypi.com/software/)

## Configure Image

On OS select others, and get the latest ubuntu 22 for raspberry Pi 4 (image works on 3 to 4 regular and CM)

I use the server version as I don't need the desktop when connecting on microhdmi, this should be a full headless setup

![](/docs/howto/images/rpiimager-1-os.png)

![](/docs/howto/images/rpiimager-2-settings.png)

![](/docs/howto/images/rpiimager-3-settings.png)

![](/docs/howto/images/rpiimager-4-burn.png)

Burn the SD card, plug it in the Pupper and start

### Download Ubuntu

Alternative, download Ubuntu and burn it with a regular imager

[]()

TODO: instructions to manually configure files


## Find Pupper IP

WiFi DHCP look in your router

![](/docs/howto/images/Pupper%20IP.png)

Ping the pupper

CMD host machine

```
ping  192.168.1.221 -n 9999
```

![](/docs/howto/images/Pupper%20IP%20Ping.png)

Connect with Putty

![](/docs/howto/images/Pupper%20SSH%20Putty.png)