#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# Author: Ryu Woon Jung (Leon)

#
# *********     Read and Write Example      *********
#
#
# Available DXL model on this example : All models using Protocol 1.0
# This example is tested with a DXL MX-28, and an USB2DYNAMIXEL
# Be sure that DXL MX properties are already set as %% ID : 1 / Baudnum : 34 (Baudrate : 57600)
#

import os,time, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynamixel_sdk.dynamixel import *


dynamixel = DynamixelSDK()

dynamixel.OpenPort()
dynamixel.Find(30)
# servo.SetOperationMode(,MULTI_TURN_MODE)

for id in dynamixel.MX_LIST:
    # dynamixel.ControlTorque(id, OFF)
    # dynamixel.SetOperationMode(POSITON_MODE)
    # dynamixel.ControlTorque(id, ON)
    # dynamixel.GoalPosition(id ,0)
    dynamixel.ControlTorque(id, OFF)
    dynamixel.SetOperationMode(MULTI_TURN_MODE)
    dynamixel.ControlTorque(id, ON)

for id in dynamixel.RX_LIST:
    dynamixel.ControlTorque(id, ON)
    dynamixel.GoalPosition(id ,0)

# for id in dynamixel.RX_LIST:
    # dynamixel.ControlTorque(id, OFF)

time.sleep(3)
angle = 0
while True:
    for id in dynamixel.MX_LIST:
        dynamixel.GoalPosition(id ,0)
    for id in dynamixel.RX_LIST:
        dynamixel.GoalPosition(id ,0)
        print("0")
    time.sleep(3)

    for id in dynamixel.MX_LIST:
        dynamixel.GoalPosition(id ,120)
    for id in dynamixel.RX_LIST:
        dynamixel.GoalPosition(id ,120)
    print("120")

    time.sleep(3)

    for id in dynamixel.MX_LIST:
        dynamixel.GoalPosition(id ,240)
    for id in dynamixel.RX_LIST:
        dynamixel.GoalPosition(id ,240)
    print("240")

    time.sleep(3)

    for id in dynamixel.MX_LIST:
        dynamixel.GoalPosition(id ,360)
    for id in dynamixel.RX_LIST:
        dynamixel.GoalPosition(id ,360)
    print("360")
    time.sleep(3)
    for id in dynamixel.MX_LIST:
        dynamixel.GoalPosition(id ,240)
    for id in dynamixel.RX_LIST:
        dynamixel.GoalPosition(id ,240)
    print("240")
    time.sleep(3)
    for id in dynamixel.MX_LIST:
        dynamixel.GoalPosition(id ,120)
    for id in dynamixel.RX_LIST:
        dynamixel.GoalPosition(id ,120)
    print("120")
    time.sleep(3)
    pass