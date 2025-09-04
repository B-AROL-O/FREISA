#!/usr/bin/python

import time
from os import listdir
from os.path import isfile, join

print(f"INFO: {__file__}")

on_freisa = False

try:
    # Try importing package MangDang
    from MangDang.mini_pupper.display import BehaviorState, Display
    on_freisa = True
    print("DEBUG: Running on FREISA")
except ImportError:
    print("WARNING: Running in simulation")

basedir = "."
if on_freisa:
    basedir = "/home/ubuntu/FREISA/assets/faces"

# Retrieve the list of all "*.png" files in the current directory
all_images = [
    join(basedir, f) for f in listdir(basedir) if isfile(join(basedir, f)) and f[-4:] == ".png"
]

# print(f"DEBUG: len={len(all_images)}, all_images={all_images}")

# Make our doggo display all_images in sequence
if on_freisa:
    disp = Display()
k = 0
for f in sorted(all_images):
    k += 1
    print(f"DEBUG: Displaying file #{k}: {f}")
    if on_freisa:
        disp.show_image(f)
    time.sleep(5)

if on_freisa:
    disp.show_state(BehaviorState.LOWBATTERY)
    time.sleep(5)
    disp.show_ip()

# EOF
