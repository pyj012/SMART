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

import os,time
from dynamixel import Dynamixel


servo = Dynamixel()

servo.OpenPort()
servo.Find(30)
servo.EnableTorque()
angle = 0

while True:
    # servo.GoalPosition(7, 300)
    # servo.GoalPosition(10, 300)
    # servo.GoalPosition(11, 300)
    for id in servo.DXL_LIST:
        print(id)
        servo.GoalPosition(id, 300)
    time.sleep(1)
    # servo.GoalPosition(7, 0)
    for id in servo.DXL_LIST:
        servo.GoalPosition(id, 0)
    # servo.GoalPosition(11, 0)

    time.sleep(1)
    # servo.GoalPosition(180)
    # time.sleep(1)
    # servo.GoalPosition(245.7)
    # time.sleep(1)
    # servo.GoalPosition(180)
    # time.sleep(1)
    # servo.GoalPosition(90)
    # time.sleep(1)