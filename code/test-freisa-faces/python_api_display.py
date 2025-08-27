#!/usr/bin/python
from MangDang.mini_pupper.display import Display, BehaviorState
import time

disp = Display()

disp.show_image('/var/lib/mini_pupper_bsp/test.png')
time.sleep(5)
disp.show_state(BehaviorState.REST)
time.sleep(5)
disp.show_state(BehaviorState.TROT)
time.sleep(5)
disp.show_state(BehaviorState.LOWBATTERY)
time.sleep(5)
disp.show_ip()
