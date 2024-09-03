
#include <SoftwareSerial.h>
#define STX 0x02
#define ETX 0x03
#define CMD_CONTROL 0xC0
#define CMD_ANSWER 0xA0
char preParsingList[99] = {
  0,
};
char dataLength[3] = {
  0,
};
uint8_t dataList[99] = {
  0,
};
char idList[10] = {
  0,
};
char valueList[10][4] = {
  0,
};
uint8_t controlByte = 0;
int parsingFlag = 0;
int parsingSenq = 0;
long prevDebugTime = 0;
int debug = 0;
int stxflag = 0;
int etxflag = 0;
int crcflag = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600);
  Serial3.begin(57600);
}
void resetbuffer(char *buf) {
  memset(buf, 0, sizeof(buf));
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial3.available() > 0) {
    uint8_t readByte = Serial3.read();

    if (readByte == STX) {
      parsingSenq = 0;
      resetbuffer(preParsingList);
      parsingFlag = 1;
    }

    if (parsingFlag) {
      preParsingList[parsingSenq] = readByte;
      parsingSenq++;
      if (readByte == ETX) {

        parsingFlag = 0;

        dataLength[0] = preParsingList[1];
        dataLength[1] = preParsingList[2];

        int dataLength_10 = (dataLength[0] - '0') * 10;
        int dataLength_1 = dataLength[1] - '0';
        int totalDataLength = dataLength_10 + dataLength_1;
        Serial.print(parsingSenq - 7);
        Serial.print(totalDataLength);

        if (parsingSenq - 7 == totalDataLength) {
              Serial.print("dd");

          controlByte = preParsingList[3];

          uint16_t SUM_CRC = controlByte;

          for (int i = 0; i < totalDataLength; i++) {
            dataList[i] = preParsingList[i + 4];
            SUM_CRC += dataList[i];
          }
          SUM_CRC += 0x01;
          uint8_t CAL_CRC_H = SUM_CRC >> 8;
          CAL_CRC_H = 0xff - CAL_CRC_H;

          uint8_t CAL_CRC_L = SUM_CRC & 0xFF;
          uint8_t CRC_H = preParsingList[totalDataLength + 4];
          uint8_t CRC_L = preParsingList[totalDataLength + 5];

          if ((CAL_CRC_H == CRC_H) && (CAL_CRC_L == CRC_L)) {
            Serial.print("CC");

            int idNum = 0;
            int valueNum = 0;
            debug = 1;

            for (int i = 0; i < totalDataLength; i++) {
              if (i % 4 == 0) {
                idList[idNum] = dataList[i];
                idNum++;
              } else {
                valueList[idNum - 1][valueNum] = dataList[i];
                valueNum++;
                valueNum %= 3;
              }
            }

            Serial.println("---------------------");
            Serial.print("CMD : ");
            Serial.write(controlByte);
            Serial.println();
            for (int i = 0; i <= 4; i++) {
              Serial.print("ID : ");
              Serial.write(idList[i]);
              Serial.println();
              Serial.print("VALUE : ");
              for (int n = 0; n < 3; n++) {
                Serial.write(valueList[i][n]);
              }
              Serial.println();
            }
          } else {
            debug = 0;
            resetbuffer(preParsingList);
            resetbuffer(dataList);
          }
        } else {
          debug = 0;
          resetbuffer(preParsingList);
          resetbuffer(dataList);
        }
      }
    }
    //   }
  }

}
