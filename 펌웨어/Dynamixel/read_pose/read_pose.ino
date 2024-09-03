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

  const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN

//Please see eManual Control Table section of your DYNAMIXEL.
//This example is written for DYNAMIXEL AX & MX series with Protocol 1.0.
//For MX 2.0 with Protocol 2.0, refer to write_x.ino example.
#define ID_ADDR                   3
#define ID_ADDR_LEN               1
#define BAUDRATE_ADDR             4
#define BAUDRATE_ADDR_LEN         1
#define PRESENT_POSITION_ADDR     36
#define PRESENT_POSITION_ADDR_LEN  2

#define TIMEOUT 10    //default communication timeout 10ms

uint8_t returned_id = 0;
uint8_t returned_baudrate = 0;
uint16_t present_position = 0;


uint16_t angle = 0;
uint16_t value=0;
const uint8_t DXL_ID = 1;
const float DXL_PROTOCOL_VERSION = 1.0;
int idlist[6] ={};
int anlglelist[6]={};
Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);
long prevtime=0;
void set_returnPosemode()
{
    for(int id = 1; id<=6; id++)
    {
          dxl.ping(id);
       dxl.setOperatingMode(id  , OP_POSITION);

      dxl.torqueOff(id);
    }
}
void return_currentPose(int *buf)
{
    for(int id = 1; id<=6; id++)
    {
      // dxl.read(id, ID_ADDR, ID_ADDR_LEN, (uint8_t*)&returned_id, sizeof(returned_id), TIMEOUT);
      // idlist[id]=returned_id;
      dxl.read(id, PRESENT_POSITION_ADDR, PRESENT_POSITION_ADDR_LEN, (uint8_t*)&angle, sizeof(angle), TIMEOUT);
      value = round(angle * 0.06);
      buf[id] = value;
      delay(5);
    }
}
void setup() {
  // put your setup code here, to run once:
  
  // For Uno, Nano, Mini, and Mega, use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);   //Set debugging port baudrate to 115200bps
  while(!DEBUG_SERIAL);         //Wait until the serial port for terminal is opened
  
  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  dxl.begin(1000000);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);

  DEBUG_SERIAL.println("Refer to eManual for more details.");
  DEBUG_SERIAL.println("https://emanual.robotis.com/docs/en/dxl/");
  DEBUG_SERIAL.print("Read for PROTOCOL ");
  DEBUG_SERIAL.print(DXL_PROTOCOL_VERSION, 1);
  DEBUG_SERIAL.print(", ID ");
  DEBUG_SERIAL.println(DXL_ID);
  set_returnPosemode();
}

void loop() {
  // put your main code here, to run repeatedly:
  if(millis()-prevtime>=10)
  {
    prevtime=millis();
    return_currentPose(anlglelist);
    // DEBUG_SERIAL.print("ID : ");
    // for(int id = 1; id<=6; id++)
    // {
    //   DEBUG_SERIAL.print(idlist[id]);
    //   DEBUG_SERIAL.print(", ");
    // }
    DEBUG_SERIAL.print(", angle : ");
    for(int id = 1; id<=6; id++)
    {
      DEBUG_SERIAL.print(anlglelist[id]);
      DEBUG_SERIAL.print(", ");
    }
    DEBUG_SERIAL.println();
  }
}
