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

import os,time, math
import numpy as np

from protocol_define import *

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library


class Dynamixel():
    def __init__(self, BAUD = BAUDRATE, PORT = DEVICENAME):
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.BAUD = BAUD
        self.PORT = PORT
        self.portHandler = PortHandler(self.PORT)
        self.DXL_LIST = {}
        self.MAX_ID = 255
        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.packetHandler = PacketHandler(PROTOCOL_VERSION) 


    def OpenPort(self):
        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()


        # Set port baudrate
        if self.portHandler.setBaudRate(self.BAUD):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

    def Find(self, MAX_DXL_ID=255):
        current_id=0
        while(current_id <= MAX_DXL_ID):
            dxl_model_number, dxl_comm_result, dxl_error = self.packetHandler.ping(self.portHandler, current_id)
            if dxl_comm_result == COMM_SUCCESS:
                print("[ID:%03d] ping Succeeded. Dynamixel model number : %d" % (current_id, dxl_model_number))
                self.DXL_LIST[current_id]=dxl_model_number
            time.sleep(0.01)
            current_id+=1
            
    def EnableTorque(self):
        # Enable Dynamixel Torque
        for id in self.DXL_LIST:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
            if dxl_comm_result == COMM_SUCCESS:
                print("[ID:%03d] Dynamixel has been successfully connected"% id)

    def GoalPosition(self, DXL_ID, angle = 0):
        # Write goal position
        dxl_model_number = self.DXL_LIST[DXL_ID]
        MIN_ANGLE = 0
        MAX_ANGEL=0
        MAXIMUM_POSITION_VALUE=0
        
        if dxl_model_number == 107:
            MIN_ANGLE = EX106_MINIMUM_ANGLE_VAULE
            MAX_ANGEL=EX106_MAXIMUM_ANGLE_VAULE
            MAXIMUM_POSITION_VALUE=DXL_106_MAXIMUM_POSITION_VALUE
        elif dxl_model_number == 64:
            MIN_ANGLE = RX64_MINIMUM_ANGLE_VAULE
            MAX_ANGEL=RX64_MAXIMUM_ANGLE_VAULE
            MAXIMUM_POSITION_VALUE=DXL_64_MAXIMUM_POSITION_VALUE
        elif dxl_model_number == 28: 
            MIN_ANGLE = RX28_MINIMUM_ANGLE_VAULE
            MAX_ANGEL=RX28_MAXIMUM_ANGLE_VAULE
            MAXIMUM_POSITION_VALUE=DXL_28_MAXIMUM_POSITION_VALUE

        if angle >MAX_ANGEL:
            angle = MAX_ANGEL
        elif angle < MIN_ANGLE:
            angle =  MIN_ANGLE
        
        default = MAXIMUM_POSITION_VALUE / MAX_ANGEL 
        temp= np.trunc(default*100)/100
        position = math.ceil(temp * angle)
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, DXL_ID, ADDR_GOAL_POSITION, position)

        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

    def PresentPosition(self, DXL_ID):
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, DXL_ID, ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" %self.packetHandler.getRxPacketError(dxl_error))

        return dxl_present_position

    def PortClose(self):
        # Close port
        self.portHandler.closePort()


