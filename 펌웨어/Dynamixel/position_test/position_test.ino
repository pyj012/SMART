#include <Dynamixel2Arduino.h>

// Please modify it to suit your hardware.
#define DXL_SERIAL   Serial
#define DEBUG_SERIAL Serial3
const int DXL_DIR_PIN = 2; // DYNAMIXEL Shield DIR PIN

float f_1present_position = 0.0;
float f_2present_position = 0.0;
int max_id = 6;

float pre_positionList[6]; 
int motor_stateList[6];

const uint8_t DXL_ID = 2;
const float DXL_PROTOCOL_VERSION = 1.0;

int angle = 0;

Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

//This namespace is required to use Control table item names
using namespace ControlTableItem;

long prevDebugTime = 0;
void setup() {
  // put your setup code here, to run once:
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
  // if(millis()-prevDebugTime>=10)
  // {
  //   // DEBUG_SERIAL.println(protocol.stxflag);
  //   prevDebugTime=millis();


  // // }
  // for(int angle=0; angle<=210; angle++)
  // {
  //   for (int id=1; id<=max_id; id++)
  //   {
  //     pre_positionList[max_id]=0;
  //     motor_stateList[max_id]=0;
  //     dxl.setGoalPosition(id, angle, UNIT_DEGREE);
      
  //   }
  //   delay(1);
  // }
  // for(int angle=210; angle>0; angle--)
  // {
  //   for (int id=1; id<=max_id; id++)
  //   {
  //     pre_positionList[max_id]=0;
  //     motor_stateList[max_id]=0;
  //     dxl.setGoalPosition(id, angle, UNIT_DEGREE);
      
  //   }
  //   delay(1);
  // }

  for (int id=1; id<=max_id; id++)
  {
    pre_positionList[max_id]=0;
    motor_stateList[max_id]=0;
    dxl.setGoalPosition(id, 0, UNIT_DEGREE);

    
  }
    for (int id=1; id<=max_id; id++)
  {
    pre_positionList[max_id]=0;
    motor_stateList[max_id]=0;
  dxl.setGoalPosition(id, 200, UNIT_DEGREE);

    
  }



}

