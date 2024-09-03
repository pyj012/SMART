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
  #define DXL_SERIAL   Serial3
  #define DEBUG_SERIAL soft_serial
  const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN

#endif
 float f_1present_position = 0.0;
float f_2present_position = 0.0;
int max_id = 6;

float pre_positionList[6]; 
int motor_stateList[6];

const uint8_t DXL_ID = 2;
const float DXL_PROTOCOL_VERSION = 1.0;
Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

//This namespace is required to use Control table item names
using namespace ControlTableItem;

void setup() {
  // put your setup code here, to run once:
  
  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(57600);
  while(!DEBUG_SERIAL);

  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  dxl.begin(1000000);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  // Get DYNAMIXEL information
  for(int i = 1; i<=max_id; i++)
  {
    dxl.ping(i);

    // Turn off torque when configuring items in EEPROM area
    dxl.torqueOff(i);
    dxl.setOperatingMode(i, OP_POSITION);
    dxl.torqueOn(i);

    // Limit the maximum velocity in Position Control Mode. Use 0 for Max speed
    dxl.writeControlTableItem(PROFILE_VELOCITY, i, 30);
    delay(1);
    
   DEBUG_SERIAL.print(i);

  }

}

void loop() {
  // put your main code here, to run repeatedly:
  
  // Please refer to e-Manual(http://emanual.robotis.com/docs/en/parts/interface/dynamixel_shield/) for available range of value. 
  // Set Goal Position in RAW value
  // dxl.setGoalPosition(DXL_ID, 1000);

  // while (abs(1000 - i_present_position) > 10)
  // {
  //   i_present_position = dxl.getPresentPosition(DXL_ID);
  //   DEBUG_SERIAL.print("Present_Position(raw) : ");
  //   DEBUG_SERIAL.println(i_present_position);
  // }
  // delay(1000);


  // Set Goal Position in DEGREE value
  // dxl.setGoalPosition(DXL_ID, 245, UNIT_DEGREE);
  // delay(1000);
  // dxl.setGoalPosition(DXL_ID, 120, UNIT_DEGREE);
  // delay(1000);
  f_1present_position = 0.0;
 f_2present_position = 0.0;
  int state = 0;

  for (int id=1; id<=max_id; id++)
  {
    pre_positionList[max_id]=0;
    motor_stateList[max_id]=0;
    dxl.setGoalPosition(id, 0, UNIT_DEGREE);

  }
  while (1)
  {
    for (int id = 1; id<=max_id;id++)
    {
      if(abs(5.7 - pre_positionList[id]) > 2.0)
      {
        motor_stateList[id]=1;
      }

      else
      {
        pre_positionList[id]=dxl.getPresentPosition(1, UNIT_DEGREE);
        DEBUG_SERIAL.print("Present_Position(degree) : ");
        DEBUG_SERIAL.println(pre_positionList[id]);
      }
      state += motor_stateList[id];
    }
    if(state == max_id)
    {
      state=0;
      break;
    } 

  }
  delay(2000);

  for (int id=1; id<=max_id; id++)
  {
    pre_positionList[max_id]=0;
    motor_stateList[max_id]=0;
    dxl.setGoalPosition(id, 180, UNIT_DEGREE);

  }
  while (1)
  {
    for (int id = 1; id<=max_id;id++)
    {
      if(abs(5.7 - pre_positionList[id]) > 2.0)
      {
        motor_stateList[id]=1;
      }

      else
      {
        pre_positionList[id]=dxl.getPresentPosition(1, UNIT_DEGREE);
        DEBUG_SERIAL.print("Present_Position(degree) : ");
        DEBUG_SERIAL.println(pre_positionList[id]);
      }
      state += motor_stateList[id];
        

    }
    if(state == max_id)
    {
      state=0;
      break;
    }
  }
  delay(2000);
}
