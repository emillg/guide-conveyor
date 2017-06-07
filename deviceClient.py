# *****************************************************************************
# Copyright (c) 2017 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Hari hara prasad Viswanathan - Initial Contribution
# *****************************************************************************

import time
import sys
import uuid
import threading
import time
import signal
import os
import random
import ibmiotf.device
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)


# Variables
motor_up_time = time.time()
running_status = False


class set_interval():  # Timer wrapper
    def __init__(self, func, sec):
        def func_wrapper():
            self.t = threading.Timer(sec, func_wrapper)
            self.t.start()
            func()
        self.t = threading.Timer(sec, func_wrapper)
        self.t.start()

    def cancel(self):
        self.t.cancel()


def start_handler():  # Turn on motor connected in pin 13
        global motor_up_time
        global running_status
        motor_up_time = time.time()
        running_status = True
        GPIO.output(13, GPIO.HIGH)
        print("starting mototr")


def stop_handler():  # Turn off motor connected in pin 13
        global motor_up_time
        global running_status
        motor_up_time = time.time()
        running_status = False
        GPIO.output(13, GPIO.LOW)
        print("Stoping the motor")


def my_command_callback(cmd):  # Handle device command
    print("Command received: %s" % cmd.command)
    if cmd.command == "stop":
        stop_handler()
    if cmd.command == "start":
        start_handler()


def my_on_publish_callback():
    print("Confirmed event  received by WIoTP\n")


def get_cpu_temperature():  # Return CPU temperature as a character string
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=", "").replace("'C\n", ""))


def get_rpm():  # Return current rpm value
    # we are generating a random value here to represent motor's r.p.m
    if not running_status:
        return 0.0
    delta = -0.1
    if (time.time() % 2) == 0:
        delta = 0.1
    rmp = random.uniform(1, 3.1) + delta
    return round(rmp, 1)


def get_ay():  # Return accelerometer value
    # we are generating a random value here to represent accelerometer
    delta = -0.05
    if (time.time() % 2) == 0:
        delta = 0.05
    ay = random.uniform(-1.0, 1.0) + delta
    return round(ay, 3)


def publish():
        state = "false"
        if running_status:
            state = "true"
        data = {'elapsed': int(time.time() - motor_up_time),
                'running': state,
                'temperature': round(float(get_cpu_temperature()), 2),
                'ay': get_ay(),
                'rpm': get_rpm()}
        success = device_client.publishEvent(
            "sensorData",
            "json",
            {'d': data},
            qos=0,
            on_publish=my_on_publish_callback)
        if not success:
            print("Not connected to WIoTP")

# Initialize the device client.
try:
    device_file = "device.conf"
    device_options = ibmiotf.device.ParseConfigFile(device_file)
    device_client = ibmiotf.device.Client(device_options)
except Exception as e:
        print("Caught exception connecting device: %s" % str(e))
        sys.exit()

device_client.connect()
device_client.commandCallback = my_command_callback

timeout = set_interval(publish, 1)
start_handler()


def signal_handler(signal, frame):
    print ('You pressed Ctrl+C!')
    timeout.cancel()
    GPIO.cleanup()
    # Disconnect the device from the cloud
    device_client.disconnect()

signal.signal(signal.SIGINT, signal_handler)
print ('Press Ctrl+C to exit')
