/*******************************************************************************
* Copyright 2016 ROBOTIS CO., LTD.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

#include <Dynamixel2Arduino.h>

// Please modify it to suit your hardware.

#define DXL_SERIAL   Serial1
#define DEBUG_SERIAL Serial
 

#define TIMEOUT 10    //default communication timeout 10ms
#define BROADCAST_ID  254
#define MODEL_NUMBER_ADDR  0
#define MODEL_NUMBER_LENGTH  2

DYNAMIXEL::InfoFromPing_t recv_info[32];  //Set the maximum DYNAMIXEL in the network to 32

uint16_t model_num = 0;
uint8_t ret = 0;
uint8_t recv_count = 0;

const uint8_t DXL_ID = BROADCAST_ID;
const float DXL_PROTOCOL_VERSION = 1.0;

Dynamixel2Arduino dxl(DXL_SERIAL, 2);

void setup() {
  // put your setup code here, to run once:
  
  // Use UART port of DYNAMIXEL Shield to debug.

  DEBUG_SERIAL.begin(115200);   //Set debugging port baudrate to 115200bps
  while(!DEBUG_SERIAL);         //Wait until the serial port for terminal is opened
  
  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  dxl.begin(1000000);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);

  DEBUG_SERIAL.print("Ping for PROTOCOL ");
  DEBUG_SERIAL.print(DXL_PROTOCOL_VERSION, 1);
  DEBUG_SERIAL.print(", ID ");
  DEBUG_SERIAL.println(DXL_ID);

  ret = dxl.ping(DXL_ID, recv_info, sizeof(recv_info), sizeof(recv_info)*3);

    while (recv_count < ret) {
      DEBUG_SERIAL.print("DYNAMIXEL Detected!");
      dxl.read(recv_info[recv_count].id, MODEL_NUMBER_ADDR, MODEL_NUMBER_LENGTH, (uint8_t*)&model_num, sizeof(model_num), TIMEOUT);
      DEBUG_SERIAL.print(", ID: ");
      DEBUG_SERIAL.print(recv_info[recv_count].id);
      DEBUG_SERIAL.print(" Model Number: ");
      DEBUG_SERIAL.println(model_num);
      recv_count++;
    }
}

void loop() {
  // put your main code here, to run repeatedly:
}