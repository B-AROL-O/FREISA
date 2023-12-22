#!/usr/bin/python
import time

from MangDang.mini_pupper.ESP32Interface import ESP32Interface

esp32 = ESP32Interface()

torque = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]

print("Haptic Demo Running")

while True:
    st_power = esp32.get_power_status()
    print(f"Power: {st_power}")

    positions = esp32.servos_get_position()
    for i in range(3):
        for k in range(3):
            positions[3 + i + 3 * k] = positions[i]
    esp32.servos_set_position_torque(positions, torque)
    time.sleep(1 / 20)  # 20 Hz
