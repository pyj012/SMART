#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <Arduino.h>

#define STX 0x02
#define ETX 0x03
#define CMD_CONTROL 0xC0
#define CMD_ANSWER 0xA0

class smartprotocol
{
  public:
    uint8_t preParsingList[99]={};
    uint8_t dataLength[3]={0,};
    uint8_t dataList[99]={};
    uint8_t idList[10]={};
    uint8_t valueList[10][4]={};
    uint8_t sendpaket[99]={};
    uint8_t controlByte= 0;
    int parsingFlag=0;
    int parsingSenq=0;
    int currentPacketLen = 0;
    
    long prevDebugTime=0;
    int debug = 0;
    void parsingprotocol(uint8_t readByte);
    void readData();
    void resetbuffer(uint8_t *buf);
    void makePacket(uint8_t *idbuf, int idsize, int *valuebuf, uint8_t cmd);
    int varToAngle(int var);
    void printSendPacket();
    String bufToString(uint8_t *buf, int buflen);
};  


extern smartprotocol protocol;
#endif