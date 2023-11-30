#!/usr/bin/env python3

#sprinkler
import logging
import time
import serial
import struct
#camera
import argparse
import json
import time
import warnings

try:
    import requests
except ImportError:
    raise ImportError(
        "Install the 'requests' Python package by running \
            'pip3 install requests'"
    )

#send robot command via UDP
from UDPComms import Publisher
import pygame


def direction_helper(trigger, opt1, opt2):
    if trigger == opt1:
        return -1
    if trigger == opt2:
        return 1
    return 0

def direction_helper(opt1, opt2):
    if opt1:
        return -1
    if opt2:
        return 1
    return 0

#----------------------------------------------------------------
# Compose SCS message
#----------------------------------------------------------------
#Move to 500
#sb_message = bytes.fromhex("ff ff 0d 05 03 2a 01 f4 cb")
#move to 600
#sb_message = bytes.fromhex("ff ff 0d 05 03 2a 02 58 66")

SERVO_STATUS_FAIL = 1
SERVO_STATUS_OK = 0

INST_WRITE = 0x03

SERVO_GOAL_POSITION_L = 42
SERVO_GOAL_POSITION_H = 43

def write_frame(ID, instruction, parameters):
    length = len(parameters) + 2
    buffer = bytearray([0xFF, 0xFF, ID, length, instruction]) + parameters
    chk_sum = ~(sum(buffer[2:]) & 0xFF)
    buffer.append(chk_sum & 0xFF)

    return buffer

def write_register_word(id, reg, value):
    buffer = bytearray([reg]) + bytearray(struct.pack(">H", value))
    return write_frame(id, INST_WRITE, buffer)

def set_goal_position(ID, position):
    return bytes(write_register_word(ID, SERVO_GOAL_POSITION_L, position))

#----------------------------------------------------------------
# DEMO
#----------------------------------------------------------------
#load camera model
#loop
#get plant distance and heading
#move toward the plant
#when close enough rotate
#activate sprinkler!

def use_camera(addr: str, period: float | int = 30):
    """
    Define a pipeline for using the camera and switching between models every
    30 seconds.

    ### Input parameters
    - addr: server address
    - period: time each model is used for
    """

    #serial port to extra 13th axis sprinkler
    gcl_ser = serial.Serial( port = '/dev/ttyAMA1', baudrate = 500000, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS,timeout = 0, write_timeout =1.0 )
    gcl_ser.reset_input_buffer()
    gcl_ser.reset_output_buffer()

    #UDP message
    pub = Publisher(8830)
    MESSAGE_RATE = 20

    # Get list of valid models
    mod_info = requests.get(addr + "models_info").json()
    mod_names = list(mod_info.keys())
    assert len(mod_names) > 0, "No models available"
    ind = 0

    #seek plant
    n_state = 0


    while True:
        # Select the model
        curr_mod = mod_names[ind]
        x = requests.post(addr + f"change_model?model={str(curr_mod)}")
        assert x.status_code == 204, "Unable to communicate with server"

        print(f"> Started model {curr_mod}")

        # Give some time for setup
        time.sleep(2)

        t_start = time.time()
        while time.time() - t_start < period:
            res = requests.get(addr + "latest_inference")
            if res.status_code == 200:
                out = res.json()
                print(json.dumps(out))
                
                #seek plant
                if (n_state == 0):
                    if (out.d < 0.3):
                        #rotate
                        n_state = 1

                    else:
                        if (out.y > 0.3):
                            send_udp_message("right")
                        elif (out.y < -0.3):
                            send_udp_message("left")
                        else:
                            send_udp_message("forward")
                #rotate
                elif (n_state >= 1) and (n_state <= 3):
                    send_udp_message("right")
                    n_state = n_state +1
                #activate sprinkler
                elif (n_state == 4):
                    #sprinkle!
                    sb_message = set_goal_position(13, 500)
                    n_state = 5
                #reset sprinkler
                elif (n_state == 5):
                    sb_message = set_goal_position(13, 650)
                    n_state = 6
                else:
                    return



            elif res.status_code == 404:
                print("No available result")
            else:
                warnings.warn(f"Server error {res.status_code}")


            time.sleep(0.5)


def send_udp_message( s_direction ):

    rx_ = 0.0
    ry_ = 0.0
    lx_ = 0.0
    ly_ = 0.0
    l_alpha = 0.15
    r_alpha = 0.3
    
    msg =
    {
        "ly": 0,
        "lx": 0,
        "rx": 0,
        "ry": 0,
        "L2": 0,
        "R2": 0,
        "R1": 0,
        "L1": 0,
        "dpady": 0,
        "dpadx": 0,
        "x": 0,
        "square": 0,
        "circle": 0,
        "triangle": 0,
        "message_rate": MESSAGE_RATE,
    }
    if s_direction == "idle"):
        pass
    elif (s_direction == "right"):
        lx_ = l_alpha * 1.0 + (1 - l_alpha) * lx_
        msg["lx"] = lx_
    elif (s_direction == "left"):
        lx_ = l_alpha * (-1.0) + (1 - l_alpha) * lx_
        msg["lx"] = lx_
    elif (s_direction == "forward"):
        ly_ = l_alpha * 1.0 + (1 - l_alpha) * ly_
        msg["ly"] = ly_
    else:
        print("ERR:direction")
        
    msg["message_rate"] = MESSAGE_RATE
    pub.send(msg)
    return


def main():
    parser = argparse.ArgumentParser(description="Parser")

    parser.add_argument(
        "-u", "--url", type=str, help="Server URL (with port)", default=None
    )

    args = parser.parse_args()
    # Get the server address
    if args.url is None:
        # Default to localhost:9090
        serv_addr = "http://localhost:9090/"
    else:
        serv_addr = str(args.url)
        if not serv_addr.startswith("http://"):
            serv_addr = "http://" + serv_addr
        if not serv_addr.endswith("/"):
            serv_addr = serv_addr + "/"

    # Launch the loop
    try:
        use_camera(serv_addr)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    main()





        




