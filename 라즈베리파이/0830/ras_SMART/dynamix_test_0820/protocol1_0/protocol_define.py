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
# Control table address
ADDR_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
ADDR_GOAL_POSITION      = 30
ADDR_PRESENT_POSITION   = 36

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 7                # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 57600
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
DXL_106_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
DXL_106_MAXIMUM_POSITION_VALUE  = 4095            # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_64_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
DXL_64_MAXIMUM_POSITION_VALUE  = 1023   
DXL_28_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
DXL_28_MAXIMUM_POSITION_VALUE  = 1023   
DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold
EX106_MINIMUM_ANGLE_VAULE = 0
EX106_MAXIMUM_ANGLE_VAULE = 245.7
RX64_MINIMUM_ANGLE_VAULE = 0
RX64_MAXIMUM_ANGLE_VAULE = 296.6
RX28_MINIMUM_ANGLE_VAULE = 0
RX28_MAXIMUM_ANGLE_VAULE = 296.6