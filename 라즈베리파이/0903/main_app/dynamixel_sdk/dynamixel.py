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

import os,time, sys, math
import numpy as np
from dynamixel_sdk.protocol_define import *

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


class DynamixelSDK():
    def __init__(self, BAUD = BAUDRATE, PORT = DEVICENAME):
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.BAUD = BAUD
        self.PORT = PORT
        self.portHandler = PortHandler(self.PORT)
        self.DXL_LIST = {}
        self.RX_LIST = {}
        self.MX_LIST={}
        self.MX_MODE = 3
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
                if dxl_model_number == MX64_MODEL_NUMBER:
                    self.MX_LIST[current_id] = dxl_model_number
                else: 
                    self.RX_LIST[current_id] = dxl_model_number

                self.DXL_LIST[current_id]=dxl_model_number
            current_id+=1
        print(self.DXL_LIST)

    def SetDelay(self, RETURN_DELAY = 0):
        for id in self.MX_LIST:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, id, ADDR_MX_RETURN_DELAY_TIME, RETURN_DELAY)
            if dxl_comm_result == COMM_SUCCESS:
                print("[ID:%03d] Dynamixel Set Delay %d"% id, RETURN_DELAY)
        for id in self.RX_LIST:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, id, ADDR_RX_RETURN_DELAY_TIME, RETURN_DELAY)
            if dxl_comm_result == COMM_SUCCESS:
                print("[ID:%03d] Dynamixel Set Delay %d"% id, RETURN_DELAY)

    def ControlTorque(self, id, torque = OFF):
        # Enable Dynamixel Torque
        if id in self.MX_LIST:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, id, ADDR_MX_TORQUE_ENABLE, torque)
            if dxl_comm_result == COMM_SUCCESS:
                print("[ID:%03d] Dynamixel has TORQUE (0: OFF, 1: ON) = "% id, torque)
        elif id in self.RX_LIST:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, id, ADDR_RX_TORQUE_ENABLE, torque)
            if dxl_comm_result == COMM_SUCCESS:
                print("[ID:%03d] Dynamixel has TORQUE (0: OFF, 1: ON) = "% id, torque)

    def SetWheelMode(self, dxl_list):
        # Enable Dynamixel Torque
        for id in dxl_list:
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, id, ADDR_SET_CW_ANGLE_LIMIT, 0)
            if dxl_comm_result == COMM_SUCCESS:
                dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, id, ADDR_SET_CCW_ANGLE_LIMIT, 0)
                if dxl_comm_result == COMM_SUCCESS:
                    print("[ID:%03d] Dynamixel Now Wheel Mode"% id)  

    def SetWheelSlope(self, dxl_list, slope=32):
        # Enable Dynamixel Torque
        for id in dxl_list:
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, id, ADDR_SET_CW_SLOPE, slope)
            if dxl_comm_result == COMM_SUCCESS:
                dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, id, ADDR_SET_CCW_SLOPE, slope)
                if dxl_comm_result == COMM_SUCCESS:
                    print("[ID:%03d] Dynamixel Wheel Slope %d"% id, slope)

    def SetOperationMode(self, mode):
        # Enable Dynamixel Torque
        if len(self.MX_LIST) >0:
            for id in self.MX_LIST:
                dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, id, ADDR_SET_OPERATING_MODE, mode)
                if dxl_comm_result == COMM_SUCCESS:
                    if mode == SPEED_MODE:
                        print("[ID:%03d] Dynamixel now SPEED MODE"% id)
                        self.MX_MODE = SPEED_MODE
                    elif mode == POSITON_MODE:
                        print("[ID:%03d] Dynamixel now POSITION MODE"% id)
                        self.MX_MODE = POSITON_MODE
                    elif mode == MULTI_TURN_MODE:
                        print("[ID:%03d] Dynamixel now MULTI-TURN MODE"% id) 
                        self.MX_MODE = MULTI_TURN_MODE
                    
    def GoalPosition(self, DXL_ID, angle = 0):
        # Write goal position
        dxl_model_number = self.DXL_LIST[DXL_ID]
        command = ADDR_RX_GOAL_POSITION

        min_position_angle = 0
        max_mosition_angle =0
        minimum_angle_value = 0
        
        if dxl_model_number == EX106_MODEL_NUMBER:
            min_position_angle = 0
            max_mosition_angle =EX106_MAXIMUM_POSITION_VALUE
            minimum_angle_value=EX106_MINIMUM_ANGLE_VAULE

        if dxl_model_number == MX64_MODEL_NUMBER:
            min_position_angle = 0
            max_mosition_angle =MX64_MAXIMUM_POSITION_VALUE
            minimum_angle_value=MX64_MINIMUM_ANGLE_VAULE

        elif dxl_model_number == RX64_MODEL_NUMBER:
            min_position_angle = 0
            max_mosition_angle =RX64_MAXIMUM_POSITION_VALUE
            minimum_angle_value=RX64_MINIMUM_ANGLE_VAULE

        elif dxl_model_number == RX28_MODEL_NUMBER: 
            min_position_angle = 0
            max_mosition_angle =RX28_MAXIMUM_POSITION_VALUE
            minimum_angle_value=RX28_MINIMUM_ANGLE_VAULE

        # position = 0
        # one_turn = 26624
        # zero = 2048
        positon_value = int(round(angle / minimum_angle_value))
        if positon_value >max_mosition_angle:
            positon_value = max_mosition_angle

        elif positon_value < min_position_angle:
            positon_value =  min_position_angle

        dxl_comm_result = True
        dxl_error = True

        if DXL_ID in self.MX_LIST:
            command = ADDR_MX_GOAL_POSITION
            if self.MX_MODE == MULTI_TURN_MODE:
                one_angle = 24576 / 360
                positon_value = int(round(one_angle * angle))
            
            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, DXL_ID, command, positon_value)
        
        else : 
            dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, DXL_ID, command, positon_value)

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


