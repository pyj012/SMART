#include "protocol.h"
#define DXL_SERIAL Serial
#define DEBUG_SERIAL Serial3
smartprotocol protocol;
float f_1present_position = 0.0;
float f_2present_position = 0.0;
int max_id = 6;
String data = "000";
float pre_positionList[6];
int motor_stateList[6];
int id = 1;
long prevDebugTime = 0;
void setup() {
  // put your setup code here, to run once:
  DXL_SERIAL.begin(115200);
  DEBUG_SERIAL.begin(115200);
  DXL_SERIAL.print("GG");
}

void loop() {
  // put your main code here, to run repeatedly:
// if (DEBUG_SERIAL.available() > 0) {
//     uint8_t readByte = DEBUG_SERIAL.read();
//     protocol.parsingprotocol(readByte);
//   }
//   if(millis()-prevDebugTime>=1000)
//   {
//     prevDebugTime=millis();
//   }
  
//   if (protocol.debug) 
//   {  
//     DEBUG_SERIAL.println("--------------------------");
//     int state = 0;
//     for (id = 0; id < max_id; id++) {
//       pre_positionList[max_id] = 0;
//       motor_stateList[max_id] = 0;
//       data = "";
//       for (int n = 0; n < 3; n++) {
//         data += protocol.valueList[id][n];
//       }
//       DEBUG_SERIAL.print(protocol.idList[id]);
//       DEBUG_SERIAL.print(" : ");
//       DEBUG_SERIAL.println(data);
//     }
//     protocol.debug = 0;
//   }
if (DEBUG_SERIAL.available() > 0) {
    char readByte = DEBUG_SERIAL.read();
    DXL_SERIAL.print(readByte);
  }
}
