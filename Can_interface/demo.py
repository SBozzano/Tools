#! /usr/bin/env python3
#
#  Copyright (C) 2018-2022 HMS Technology Center Ravensburg GmbH, all rights reserved
#  See LICENSE.txt for more information
#                                   
"""
Demo application for the simplyCAN API, sending and receiving
11-bit CAN messages at 250 KBaud.
Adapt the COM/TTY port in the last code line to your needs.
To abort the demo application, press Ctrl+C.

This demo software has functional restrictions and is therefore not intended
to be used in productive environments.
"""
# standard library imports
import os
import sys
import time
import signal
# application specific imports
import simply_can
from simply_can import Message

SimplyObj = None


def error(simply):
    err = simply.get_last_error()
    print("Error:", simply.get_error_string(err))
    simply.close()
    sys.exit(-1)


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    if SimplyObj:
        SimplyObj.close()
    sys.exit(0)


def receive_messages(simply):
    res, msg = simply.receive()
    if res == 1:
        print(msg)
        return True
    elif res == -1:
        error()
    return False


def send_message(simply, msg):
    simply.send(msg)
    simply.flush_tx_fifo()
    msg.ident = (msg.ident + 1) % 0x3FF


def main(ser_port, baudrate):
    global SimplyObj
    print("\n#### simplyCAN Demo 2.0 (c) 2018-2022 HMS ####\n")

    # abort with Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    simply = simply_can.SimplyCAN()
    SimplyObj = simply
    if not simply.open(ser_port): error(simply)

    id = simply.identify()
    if not id: error(simply)

    print("Firmware version:", id.fw_version.decode("utf-8"))
    print("Hardware version:", id.hw_version.decode("utf-8"))
    print("Product version: ", id.product_version.decode("utf-8"))
    print("Product string:  ", id.product_string.decode("utf-8"))
    print("Serial number:   ", id.serial_number.decode("utf-8"))

    res = simply.stop_can()  # to be on the safer side
    res &= simply.initialize_can(baudrate)
    res &= simply.start_can()
    if not res: error(simply)

    lastSent = 0
    TxMsg = Message(0x100, [1, 2, 3, 4, 5, 6, 7, 8])
    print("Run application...")
    while True:
        if time.time() - lastSent > 1.0:  # one message every second
            lastSent = time.time()
            send_message(simply, TxMsg)
            print("CAN Status:", simply.can_status())
        if not receive_messages(simply):
            time.sleep(0.01)


# main("/dev/ttyACM0", 250)    # for Linux
main("COM20", 500)  # for Windows
