#include "protocol.h"
#include <Dynamixel2Arduino.h>

// Please modify it to suit your hardware.
#define DXL_SERIAL Serial1
#define DEBUG_SERIAL Serial

#define ID_ADDR                   3
#define ID_ADDR_LEN               1
#define BAUDRATE_ADDR             4
#define BAUDRATE_ADDR_LEN         1
#define PRESENT_POSITION_ADDR     36
#define PRESENT_POSITION_ADDR_LEN  2

#define TIMEOUT 10    //default communication timeout 10ms
#define Moving_Speed 32
#define Moving_Speed_LEN 2

uint16_t moving_speed = 300;


const int DXL_DIR_PIN = 2;  // DYNAMIXEL Shield DIR PIN
 
float f_1present_position = 0.0;
float f_2present_position = 0.0;
String data = "000";
float pre_positionList[15];
int motor_stateList[15];

const uint8_t DXL_ID = 2;
const float DXL_PROTOCOL_VERSION = 1.0;
uint16_t current_pose= 0;

Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

//This namespace is required to use Control table item names
using namespace ControlTableItem;
smartprotocol protocol;
int id = 1;
long prevDebugTime = 0;
void setup() {
  // put your setup code here, to run once:
  DEBUG_SERIAL.begin(115200);
  while (!DEBUG_SERIAL)
    ;
  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  // Serial.begin(57600);
  dxl.begin(1000000);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  // Get DYNAMIXEL information
  int max_id = 15;

  for (int i = 1; i <= max_id; i++) {
    dxl.ping(i);
    // Turn off torque when configuring items in EEPROM area
        delay(5);

    dxl.torqueOff(i);
        delay(5);

    dxl.setOperatingMode(i  , OP_POSITION);
        delay(5);

    if(dxl.write(i, Moving_Speed, (uint8_t*)&moving_speed, Moving_Speed_LEN, TIMEOUT))
        delay(5);

    dxl.torqueOn(i);
    delay(1);
    if(i == 1 || i ==4 || i ==5)
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

  }
  
  if (protocol.debug) 
  {  
    DEBUG_SERIAL.println("--------------------------");
    int state = 0;
    int max_id = sizeof(protocol.idList)/sizeof(int);

    for (id = 0; id < max_id; id++) {
      pre_positionList[max_id] = 0;
      motor_stateList[max_id] = 0;
      data = "";
      for (int n = 0; n < 3; n++) {
        data += protocol.valueList[id][n];
      }
        int movingdata = data.toInt();
        int resultdata = 0;
        if(protocol.idList[id] == 1)
        {
          resultdata = constrain(movingdata, 105, 165);
        }
        else if(protocol.idList[id] == 2)
        {
          resultdata = constrain(movingdata, 0, 45);
        }
        else if(protocol.idList[id] == 3)
        {
          resultdata = constrain(movingdata, 0, 70);
        }
        else if(protocol.idList[id] == 4)
        {
          resultdata = constrain(movingdata, 125, 170);
        }
        else if(protocol.idList[id] == 5)
        {
          resultdata = constrain(movingdata, 0, 250);
        }
        else if(protocol.idList[id] == 6)
        {
          resultdata = constrain(movingdata, 10, 75);
        }
        dxl.setGoalPosition(protocol.idList[id], resultdata, UNIT_DEGREE);
        Serial.print(char(protocol.idList[id]));
        Serial.print(" : ");
        Serial.print(resultdata);
        Serial.print(", ");

      }
       Serial.println();
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
  //}

}
