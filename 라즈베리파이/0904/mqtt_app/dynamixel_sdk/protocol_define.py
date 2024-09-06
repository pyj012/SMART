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

# Control table address
ADDR_RX_TORQUE_ENABLE      = 24             
ADDR_MX_TORQUE_ENABLE      = 64               # Control table address is different in Dynamixel model

ADDR_RX_GOAL_POSITION      = 30
ADDR_MX_GOAL_POSITION = 116
ADDR_PRESENT_POSITION   = 36
ADDR_RX_RETURN_DELAY_TIME = 5
ADDR_MX_RETURN_DELAY_TIME = 9

ADDR_SET_CW_ANGLE_LIMIT = 6
ADDR_SET_CCW_ANGLE_LIMIT = 8
ADDR_SET_CW_SLOPE = 28
ADDR_SET_CCW_SLOPE =29
ADDR_SET_MOVING_SPEED = 32
ADDR_SET_PRESENT_SPEED = 38
ADDR_SET_OPERATING_MODE = 11
ADDR_RX_PING = 3
ADDR_MX_PING = 7
# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 7                # Dynamixel ID : 1
BAUDRATE                    = 1000000             # Dynamixel default baudrate : 57600
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
ON = 1
OFF = 0

SPEED_MODE= 1
POSITON_MODE= 3
MULTI_TURN_MODE= 4
TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque

RX28_MODEL_NUMBER = 28
RX64_MODEL_NUMBER = 64
MX64_MODEL_NUMBER = 311
EX106_MODEL_NUMBER = 107
EX106_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
EX106_MAXIMUM_POSITION_VALUE  = 4095            # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
RX64_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
RX64_MAXIMUM_POSITION_VALUE  = 1023  
MX64_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
MX64_MAXIMUM_POSITION_VALUE  = 4095    
RX28_MINIMUM_POSITION_VALUE  = 0           # Dynamixel will rotate between this value
RX28_MAXIMUM_POSITION_VALUE  = 1023   
EX106_MINIMUM_ANGLE_VAULE = 0.06
MX64_MINIMUM_ANGLE_VAULE = 0.0879
RX64_MINIMUM_ANGLE_VAULE = 0.29
RX28_MINIMUM_ANGLE_VAULE = 0.29

DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold
