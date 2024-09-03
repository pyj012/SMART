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
#define Moving_Speed 32
#define Moving_Speed_LEN 2
#define TIMEOUT 10    //default communication timeout 10ms

uint16_t moving_speed = 300;


uint16_t angle = 0;
uint16_t value=0;
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
void set_torqueonMode()
{
  for (int i = 1; i <= max_id; i++) {
    // Turn off torque when configuring items in EEPROM area
    dxl.torqueOn(i);
    // Limit the maximum velocity in Position Control Mode. Use 0 for Max speed
    delay(1);
  }
}
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
      if(id == 1)
      {
        value = round(angle * 0.06);
      }
      else
      {
        value = round(angle * 0.29);
      }
      buf[id-1] = value;
      delay(5);
    }
}
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
    if(dxl.write(i, Moving_Speed, (uint8_t*)&moving_speed, Moving_Speed_LEN, TIMEOUT))
    dxl.torqueOn(i);

    // Limit the maximum velocity in Position Control Mode. Use 0 for Max speed
    // dxl.writeControlTableItem(PROFILE_VELOCITY, i, 30);
    delay(1);

    if(i == 1||i==4 || i==5)
    {
      dxl.setGoalPosition(i, 125, UNIT_DEGREE);
    }
    else if(i == 6)
    {
      dxl.setGoalPosition(i, 0, UNIT_DEGREE);
    }
    else
    {
      dxl.setGoalPosition(i, 0, UNIT_DEGREE);
    }
    DEBUG_SERIAL.print(i);
  }
  delay(100);
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
    if (protocol.controlByte == CMD_ANSWER)
    {
      int anglelist[6]={};
      return_currentPose(anglelist);
      for(int id = 0; id<6; id++)
      {
        Serial.print(anglelist[id]);
        Serial.print(",");
        DEBUG_SERIAL.print(anglelist[id]);
        DEBUG_SERIAL.print(",");
      }
      DEBUG_SERIAL.println(",");
      Serial.println();
    }   
    else if (protocol.controlByte == CMD_TORQUEOFF)
    {
      set_returnPosemode();
      Serial.println("SET TOROFF");
    }
    else if(protocol.controlByte == CMD_TORQUEON)
    {
      set_torqueonMode();
      Serial.println("SET TORQUE");
    }
    else if(protocol.controlByte == CMD_CONTROL)
    {
      Serial.println("--------------------------");
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
          resultdata = constrain(movingdata, 0, 25);
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
        Serial.print(id);
        Serial.print(" : ");
        Serial.print(resultdata);
        Serial.print(", ");

      }
       Serial.println();
    }
    protocol.debug = 0;
  }
  // else if (protocol.answerdebug) 
  // {  
  //   if(protocol.answeronce)
  //   {
  //     protocol.answeronce=0;
  //     protocol.debugonce=1;
  //     Serial.println("SET POSE MODE");
  //     delay(1000);
  //   }    
  //   int anlglelist[6]={};
  //   return_currentPose(anlglelist);
  //   for(int id = 1; id<=6; id++)
  //   {
  //     DEBUG_SERIAL.print(anlglelist[id]);
  //     DEBUG_SERIAL.print(", ");
  //     Serial.print(anlglelist[id]);
  //     Serial.print(", ");
  //   }
  //   DEBUG_SERIAL.println();
  //   Serial.println();
  //   protocol.answerdebug = 0;
  // }
}
