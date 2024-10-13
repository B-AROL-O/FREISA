---
title: "HOWTO - ANAVI Handle"
date: "2024-10-12"
---

## Introduction

Following up to [a thread on X](https://x.com/leonanavi/status/1834916587679498323) we tried to use a [ANAVI Handle](https://www.crowdsupply.com/anavi-technology/anavi-handle) to interact and control [FREISA](https://github.com/B-AROL-O/FREISA).

## Reference Documents

* [ANAVI Handle on CrowdSupply](https://www.crowdsupply.com/anavi-technology/anavi-handle)
* [ANAVI Handle Assembly Guide for Open Source Nunchuk to USB Adapter](https://www.youtube.com/watch?v=ZAnON53XiUk) - Leon Anavi on YouTube, 2024-05-22
* [GitHub: AnaviTechnology/anavi-handle](https://github.com/AnaviTechnology/anavi-handle)
* [GitHub: AnaviTechnology/anavi-handle-sw](https://github.com/AnaviTechnology/anavi-handle-sw)
* [Seeed Studio XIAO RP2040](https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html) - Supports Arduino, MicroPython and CircuitPython

## Assembling and testing ANAVI Handle

ANAVI Handle is an open source hardware USB-C adapter with [XIAO RP2040](https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html) for [Nunchuk compatible controllers](https://en.wikipedia.org/wiki/Wii_Remote#Nunchuk). It allows you to connect Nunchuk controller to a personal computer and use it as USB device (HID): mouse, keyboard or joystick/gamepad.

This chapter provides step by step instructions how to assemble ANAVI Handle.

### ANAVI Handle Assembly Guide

Follow [this video on YouTube](https://www.youtube.com/watch?v=ZAnON53XiUk)

[![ANAVI Handle Assembly Guide for Open Source Nunchuk to USB Adapter](https://img.youtube.com/vi/ZAnON53XiUk/0.jpg)](https://www.youtube.com/watch?v=ZAnON53XiUk "ANAVI Handle Assembly Guide for Open Source Nunchuk to USB Adapter")

ANAVI Handle comes as a do-it-yourself kit in a very simple packaging.

The kit contains the Printed Circuit Board, Acrylic Enclosures, nuts and screws.
Furthermore, there are additional kits that provide a compatible [Nunchuk controller](https://en.wikipedia.org/wiki/Wii_Remote#Nunchuk), either in black or white colors.

#### Step 1: Peel Off Protective Films

Step number 1 is to peel off the protective films from both sides of the Acrylic Enclosures.

#### Step 2: Top Acrylic Enclosure

ANAVI Handle comes with:

* 4x M2.5 10mm screws
* 8x M2.5 nuts

Take the Top Acrylic Enclosure which has a notch for the Nintendo Nunchuk controller.

Place the four screws in the dedicated mounting holes, and fasten them with the four nuts.
You can even do it without a screwdriver, you can do it with your bare hands.
The process is super-simple and straightforward.

#### Step 3: PCB

Take the Printed Circuit Board and insert the Top Acrylic Enclosure with the screws and the nuts in the mounting holes of the PCB.

As a result, the PCB of the ANAVI Handle will be below the four nuts.

#### Step 4: Bottom Acrylic Enclosure

Take the Bottom Acrylic Enclosure, place it below the Printed Circuit Board, and fasten it with four nuts.

As you can see in the video you can do it with your bare hands.
Of course, if you use a screwdriver, it might be slightly easier.

By the end of this step, you have your ANAVI Handle fully assembled.

#### Step 5: Nunchuk

Step number 5 is to a plug a Nunchuk or a compatible controller into the ANAVI Handle and to connect it to a computer using a USB-C cable.

A green light will indicate that the connection to the computer and the controller is successful.

### ANAVI Handle Demo

ANAVI Handle is an entirely Open Source that combines an Open Source Hardware Printed Circuit Board with free and Open Source firmware written in [CircuitPython](https://circuitpython.org/).
The source code is [available at GitHub](https://github.com/AnaviTechnology/anavi-handle-sw).

The default open-source firmware uses an RGB LED to indicate the connection status:

* Green light: Nunchuk controller is connected correctly.
* Blue light: The Nunchuk controller is disconnected from the ANAVI Handle.
* Red light: The Nunchuk controller is absent or improperly connected.

A green LED confirms a successful connection between the Nunchuk, the ANAVI Handle, and your computer.

## Using ANAVI Handle to control FREISA Robot Dog

TODO

<!-- EOF -->
