#!/usr/bin/python
from MangDang.mini_pupper.ESP32Interface import ESP32Interface
import time

# start position (neutral position)
positions = [512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512]
# which servos to move: count servos from 1 to 12
servos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# maximum deviation from neutral position
max_delta = 50

# move only hips
#servos = [1, 4, 7, 10]

# move only upper legs
#servos = [2, 5, 8, 11]

# move only lower legs
#servos = [3, 6, 9, 12]

an_shoulder_id = [2, 5, 8, 11]
an_shoulder_dir = [1, 1, 1, 1]

an_knee_id = [3, 6, 9, 12]
an_knee_dir = [1, 1, 1, 1]

esp32 = ESP32Interface()

delta = 1
upper_max = min(512 + max_delta, 1023)
lower_min = max(512 - max_delta, 0)

t_period = 2

while True:
    esp32.servos_set_position(positions)

    for n_index, n_servo in enumerate(an_shoulder_id):
        positions[n_servo - 1] += an_shoulder_dir[n_index]
        if positions[n_servo - 1] > upper_max:
            positions[n_servo - 1] = upper_max 
        elif positions[n_servo - 1] < lower_min:
            positions[n_servo - 1] = lower_min

    for n_index, n_servo in enumerate(an_knee_id):
        positions[n_servo - 1] += an_knee_dir[n_index]
        if positions[n_servo - 1] > upper_max:
            positions[n_servo - 1] = upper_max 
        elif positions[n_servo - 1] < lower_min:
            positions[n_servo - 1] = lower_min



    # limit to configured maximum deviation
    if positions[servos[0] - 1] >= upper_max or positions[servos[0] - 1] <= lower_min:
        delta *= -1

    time.sleep(t_period / (2*max_delta))


