#!/usr/bin/python
# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import logging
import struct
import time

import serial

# ----------------------------------------------------------------
# Compose SCS message
# ----------------------------------------------------------------
# Move to 500
# sb_message = bytes.fromhex("ff ff 0d 05 03 2a 01 f4 cb")
# move to 600
# sb_message = bytes.fromhex("ff ff 0d 05 03 2a 02 58 66")

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


# ----------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------
# if the file is being read WITH the intent of being executed

if __name__ == "__main__":
    # initialize logs
    logging.basicConfig(
        # level of debug to show
        # level=logging.DEBUG,
        level=logging.INFO,
        # header of the debug message
        format="[%(asctime)s] %(levelname)s %(module)s:%(lineno)d > %(message)s ",
    )
    logging.info("Class definition")
    print("Test GPIO UART")

    gcl_ser = serial.Serial(
        port="/dev/ttyAMA1",
        baudrate=500000,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0,
        write_timeout=1.0,
    )
    gcl_ser.reset_input_buffer()
    gcl_ser.reset_output_buffer()

    print("Serial: ", gcl_ser)

    n_pos = 650
    x_dir = 0

    while True:
        if gcl_ser.is_open:
            # send message
            sb_message = set_goal_position(13, n_pos)
            print("pos:", n_pos)
            if x_dir == 0:
                # go down
                n_pos = n_pos - 2
            else:
                # go up
                n_pos = n_pos + 2

            if n_pos < 500:
                n_pos = 500
                # go up
                x_dir = 1

            if n_pos > 650:
                n_pos = 650
                # go down
                x_dir = 0

            n_byte_sent = gcl_ser.write(sb_message)
            print("msg: ", sb_message, "sent: ", n_byte_sent)
            # try to read from buffer
            s_message_rx = gcl_ser.read(20)
            if len(s_message_rx) > 0:
                print("Received: ", s_message_rx)
        else:
            print("CLOSED")

        # wait
        time.sleep(0.1)
