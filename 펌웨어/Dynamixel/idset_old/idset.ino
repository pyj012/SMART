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
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560) // When using DynamixelShield
  #include <SoftwareSerial.h>
  SoftwareSerial soft_serial(7, 8); // DYNAMIXELShield UART RX/TX
  #define DXL_SERIAL   Serial
  #define DEBUG_SERIAL soft_serial
  const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN
#elif defined(ARDUINO_SAM_DUE) // When using DynamixelShield
  #define DXL_SERIAL   Serial
  #define DEBUG_SERIAL SerialUSB
  const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN
#elif defined(ARDUINO_SAM_ZERO) // When using DynamixelShield
  #define DXL_SERIAL   Serial1
  #define DEBUG_SERIAL SerialUSB
  const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN
#elif defined(ARDUINO_OpenCM904) // When using official ROBOTIS board with DXL circuit.
  #define DXL_SERIAL   Serial3 //OpenCM9.04 EXP Board's DXL port Serial. (Serial1 for the DXL port on the OpenCM 9.04 board)
  #define DEBUG_SERIAL Serial
  const int DXL_DIR_PIN = 22; //OpenCM9.04 EXP Board's DIR PIN. (28 for the DXL port on the OpenCM 9.04 board)
#elif defined(ARDUINO_OpenCR) // When using official ROBOTIS board with DXL circuit.
  // For OpenCR, there is a DXL Power Enable pin, so you must initialize and control it.
  // Reference link : https://github.com/ROBOTIS-GIT/OpenCR/blob/master/arduino/opencr_arduino/opencr/libraries/DynamixelSDK/src/dynamixel_sdk/port_handler_arduino.cpp#L78
  #define DXL_SERIAL   Serial3
  #define DEBUG_SERIAL Serial
  const int DXL_DIR_PIN = 84; // OpenCR Board's DIR PIN.
#elif defined(ARDUINO_OpenRB)  // When using OpenRB-150
  //OpenRB does not require the DIR control pin.
  #define DXL_SERIAL Serial1
  #define DEBUG_SERIAL Serial
  const int DXL_DIR_PIN = -1;
#else // Other boards when using DynamixelShield
  #define DXL_SERIAL   Serial1
  #define DEBUG_SERIAL Serial
  const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN
#endif
 #define TIMEOUT 10    //default communication timeout 10ms
#define BROADCAST_ID  254
#define MODEL_NUMBER_ADDR  0
#define MODEL_NUMBER_LENGTH  2

DYNAMIXEL::InfoFromPing_t recv_info[32];  //Set the maximum DYNAMIXEL in the network to 32
const uint8_t DXL_ID = BROADCAST_ID;

uint16_t model_num = 0;
uint8_t ret = 0;
uint8_t recv_count = 0;
const uint8_t DEFAULT_DXL_ID = 1;
const float DXL_PROTOCOL_VERSION = 1.0;

Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

//This namespace is required to use Control table item names
using namespace ControlTableItem;
  uint8_t present_id = DEFAULT_DXL_ID;
  uint8_t new_id = 3;
  int chang_id = 0;
 int process =0;
void setup() {
  // put your setup code here, to run once:
  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(57600);
  
}

void loop() {
  while(1)
  {
    DEBUG_SERIAL.println("input number to change servoid");
    if (DEBUG_SERIAL.available()>0)
    {
      chang_id = DEBUG_SERIAL.read();
      if(chang_id)
      {
        process = 1;
      }
    }
    if (process)
    {
      process=0;
      DEBUG_SERIAL.print("change servoid to");
      DEBUG_SERIAL.print(chang_id);

      dxl.begin(1000000);
      // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
      dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);

      DEBUG_SERIAL.print("Ping for PROTOCOL ");
      DEBUG_SERIAL.print(DXL_PROTOCOL_VERSION, 1);
      DEBUG_SERIAL.print(", ID ");
      DEBUG_SERIAL.println(DXL_ID);
      
      ret = dxl.ping(DXL_ID, recv_info, sizeof(recv_info), sizeof(recv_info)*3);
      if(ret>0)
      {
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
      else
      {
        DEBUG_SERIAL.print("err cant find motor");
      }
      if(model_num>0)
      {
        DEBUG_SERIAL.print("start to change id");
        DEBUG_SERIAL.print(", ID ");
        DEBUG_SERIAL.print(present_id);
        DEBUG_SERIAL.print(": ");
        if(dxl.ping(present_id) == true) {
          DEBUG_SERIAL.print("ping succeeded!");
          DEBUG_SERIAL.print(", Model Number: ");
          DEBUG_SERIAL.println(dxl.getModelNumber(present_id));
        }
        // Turn off torque when configuring items in EEPROM area
        dxl.torqueOff(present_id);
        
        // set a new ID for DYNAMIXEL. Do not use ID 200
        new_id = chang_id;
        if(dxl.setID(present_id, new_id) == true){
          DEBUG_SERIAL.print("ID has been successfully changed to ");
          DEBUG_SERIAL.println(new_id);
        }
        else
        {
          DEBUG_SERIAL.print("ID changed fail ");
        }
      }
    }
    // put your main code here, to run repeatedly:
    // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
    else
    {
      delay(1000);
      
        continue;
    }
  }
}