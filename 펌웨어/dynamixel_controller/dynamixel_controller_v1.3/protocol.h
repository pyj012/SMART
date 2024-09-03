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
    char preParsingList[99]={};
    char dataLength[3]={0,};
    uint8_t dataList[99]={};
    char idList[6]={};
    char valueList[6][4]={};
    uint8_t controlByte= 0;
    int parsingFlag=0;
    int parsingSenq=0;
    long prevDebugTime=0;
    int debug = 0;
    void parsingprotocol(uint8_t readByte);
    void readData();
    void resetbuffer(char *buf);
};  


extern smartprotocol protocol;
#endif