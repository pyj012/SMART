#include "protocol.h"
#include <Dynamixel2Arduino.h>

// Please modify it to suit your hardware.
#define DXL_SERIAL Serial1
#define DEBUG_SERIAL Serial3

#define ID_ADDR                   3
#define ID_ADDR_LEN               1
#define BAUDRATE_ADDR             4
#define BAUDRATE_ADDR_LEN         1
#define PRESENT_POSITION_ADDR     36
#define PRESENT_POSITION_ADDR_LEN  2

#define TIMEOUT 10    //default communication timeout 10ms




const int DXL_DIR_PIN = 2;  // DYNAMIXEL Shield DIR PIN
 
float f_1present_position = 0.0;
float f_2present_position = 0.0;
String data = "000";
float pre_positionList[6];
int motor_stateList[6];

const uint8_t DXL_ID = 2;
const float DXL_PROTOCOL_VERSION = 1.0;
uint16_t current_pose= 0;

Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

//This namespace is required to use Control table item names
using namespace ControlTableItem;
smartprotocol protocol;
int id = 1;
int max_id = 6;

long prevDebugTime = 0;
void setup() {
  // put your setup code here, to run once:
  DEBUG_SERIAL.begin(115200);
  while (!DEBUG_SERIAL);
  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  Serial.begin(115200);
  dxl.begin(1000000);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  // Get DYNAMIXEL information

  for (int i = 1; i <= max_id; i++) {
    dxl.ping(i);

    // Turn off torque when configuring items in EEPROM area
    dxl.torqueOff(i);
    dxl.setOperatingMode(i  , OP_POSITION);
    dxl.torqueOn(i);

    // Limit the maximum velocity in Position Control Mode. Use 0 for Max speed
    dxl.writeControlTableItem(PROFILE_VELOCITY, i, 30);
    delay(1);

    if(i == 1||i==4 || i==5)
    {
      dxl.setGoalPosition(i, 125, UNIT_DEGREE);
    }
    else
    {
      dxl.setGoalPosition(i, 0, UNIT_DEGREE);
    }
    DEBUG_SERIAL.print(i);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  if (DEBUG_SERIAL.available() > 0) {
    uint8_t readByte = DEBUG_SERIAL.read();
    protocol.parsingprotocol(readByte);
  }
  if(millis()-prevDebugTime>=1000)
  {
    prevDebugTime=millis();
    // dxl.read(1, PRESENT_POSITION_ADDR, PRESENT_POSITION_ADDR_LEN, (uint8_t*)&current_pose, sizeof(current_pose), TIMEOUT);
    // Serial.print("current_pose : ");
    // Serial.println(current_pose);

  }
  
  if (protocol.debug) 
  {  
    Serial.println("--------------------------");
    int state = 0;

    for (id = 0; id < max_id; id++) {
      pre_positionList[max_id] = 0;
      motor_stateList[max_id] = 0;
      data = "";
      for (int n = 0; n < 3; n++) {
        data += protocol.valueList[id][n];
      }
      // DEBUG_SERIAL.print(protocol.idList[id]);
      // DEBUG_SERIAL.print(" : ");
      // DEBUG_SERIAL.println(data);
      dxl.setGoalPosition(protocol.idList[id], data.toInt(), UNIT_DEGREE);
    }
    
    protocol.debug = 0;
  //     while (1)
  //     {
  //         if (DEBUG_SERIAL.available() > 0) {
  //     uint8_t readByte = DEBUG_SERIAL.read();
  //     protocol.parsingprotocol(readByte);
  // }
  //       for (int id = 1; id<=max_id;id++)
  //       {
  //         if(abs(5.7 - pre_positionList[id]) > 2.0)
  //         {
  //           motor_stateList[id]=1;
  //         }

  //         else
  //         {
  //           pre_positionList[id]=dxl.getPresentPosition(1, UNIT_DEGREE);
  //           DEBUG_SERIAL.print("Present_Position(degree) : ");
  //           DEBUG_SERIAL.println(pre_positionList[id]);
  //         }
  //         state += motor_stateList[id];
  //       }
  //       if(state == max_id)
  //       {
  //         state=0;
  //         break;
  //       }
  //     }
  }
}
