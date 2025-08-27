#!/usr/bin/python

import time

from MangDang.mini_pupper.display import BehaviorState, Display

disp = Display()

# Hard code contents of mini_pupper_eyes_v2_fixed.zip

disp.show_image("/home/ubuntu/test/eyes2_sorpresa.png")
time.sleep(5)
disp.show_image("/home/ubuntu/test/eyes2_pensiero_04.png")

# TODO: Display in sequence all "*.png" files in the current directory

# disp.show_image('/var/lib/mini_pupper_bsp/test.png')

# time.sleep(5)
# disp.show_state(BehaviorState.REST)
# time.sleep(5)
# disp.show_state(BehaviorState.TROT)
# time.sleep(5)
disp.show_state(BehaviorState.LOWBATTERY)
time.sleep(5)
disp.show_ip()

# EOF
