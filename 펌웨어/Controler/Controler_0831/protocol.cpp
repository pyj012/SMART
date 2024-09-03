#include "protocol.h"

void smartprotocol::parsingprotocol(uint8_t readByte)
{

    if(readByte == STX)
    { 
      parsingSenq=0;
      resetbuffer(preParsingList);
      parsingFlag = 1;
    }

    if(parsingFlag)
    {
      preParsingList[parsingSenq]= readByte;
      parsingSenq++;
      if(readByte == ETX)
      {
        parsingFlag=0;

        dataLength[0]= preParsingList[1];
        dataLength[1]= preParsingList[2];

        int dataLength_10 = (dataLength[0]-'0')*10;
        int dataLength_1 = dataLength[1]-'0';
        int totalDataLength = dataLength_10+dataLength_1;

        if (parsingSenq-7 == totalDataLength)
        {
          controlByte =  preParsingList[3];

          uint16_t SUM_CRC= controlByte;

          for(int i=0; i<totalDataLength; i++)
          {
            dataList[i]=preParsingList[i+4];
            SUM_CRC += dataList[i];
          }
          SUM_CRC+=0x01;
          uint8_t CAL_CRC_H = SUM_CRC >>8;
          CAL_CRC_H = 0xff-CAL_CRC_H;

          uint8_t CAL_CRC_L = SUM_CRC & 0xFF;
          uint8_t CRC_H=preParsingList[totalDataLength+4];
          uint8_t CRC_L=preParsingList[totalDataLength+5];

          if((CAL_CRC_H == CRC_H)&&(CAL_CRC_L == CRC_L))
          {
            int idNum=0;
            int idcnt=0;
            int valueNum=0;
            debug=1;
            for(int i = 0; i<totalDataLength; i++)
            {
              if(i%4==0)
              {
                idNum= dataList[i] - 48;
                idList[idcnt] = idNum;
                idcnt++;
              }
              else
              {
                valueList[idcnt-1][valueNum]=dataList[i];
                valueNum++;
                valueNum%=3;
              } 
            }
          }
          else
          {
              debug=0;
              resetbuffer(preParsingList);
              resetbuffer(dataList);            
          }
        }
        else
        {
          debug=0;
          resetbuffer(preParsingList);
          resetbuffer(dataList);
        }
      }
    }
}
void smartprotocol::readData()
{
  if(debug)
  {
  Serial.println("---------------------");
  Serial.print("CMD : ");
  Serial.write(controlByte);
  Serial.println();
  for(int i = 0; i<=4;i++)
  {
    Serial.print("ID : ");
    Serial.write(idList[i]);
    Serial.println();
    Serial.print("VALUE : ");
    for(int n =0; n<3; n++)
    {
      Serial.write(valueList[i][n]);
    }
    Serial.println();
  }
  debug=0;
  }
}
void smartprotocol::resetbuffer(uint8_t *buf)
{
  memset(buf, 0, sizeof(buf));
}
void smartprotocol::makePacket(uint8_t *idbuf, int idsize, int *valuebuf, uint8_t cmd)
{  
    currentPacketLen = 4;
    int valuesize=0;
    char temp_value[99][3]; 
  	for(int i =0; i <idsize; i++)
    {
      int value = abs(valuebuf[i]);
      String temp = String(value);
      valuesize+=3;
      if(value < 10)
      {
        temp_value[i][0] = '0';
        temp_value[i][1] = '0';
        temp_value[i][2] = temp[0];
      }
      if(value >= 10 && value <100)
      {
        temp_value[i][0] = '0';
        temp_value[i][1] = temp[0];
        temp_value[i][2] = temp[1];
      }
      if(value >= 100)
      {
        temp_value[i][0] = temp[0];
        temp_value[i][1] = temp[1];
        temp_value[i][2] = temp[2];
      }
    }
    int totalPacketLen = idsize+valuesize;
  	uint8_t len_H = totalPacketLen/10 + 0x30;
    uint8_t len_L = totalPacketLen%10 + 0x30;
  	uint16_t checkSum = cmd;
    // Serial.print("total : ");
    // Serial.print(totalPacketLen);
    // Serial.print(", len_H : ");
    // Serial.print(len_H);
    // Serial.print(", len_L");
    // Serial.println(len_L);
    sendpaket[0]= STX;
    sendpaket[1]= len_H;
    sendpaket[2]= len_L;
    sendpaket[3]= cmd;
    for(int i =0; i<idsize; i++)
    {
      String data = String(valuebuf[i]);  
      uint8_t id = idbuf[i];
      uint8_t data1 = temp_value[i][0];
      uint8_t data2 = temp_value[i][1];
      uint8_t data3 = temp_value[i][2];
      sendpaket[currentPacketLen] = id;
      sendpaket[currentPacketLen+1] = data1;
      sendpaket[currentPacketLen+2] = data2;
      sendpaket[currentPacketLen+3] = data3;
      checkSum = checkSum+id+data1+data2+data3;
      currentPacketLen+=4;
    }
  	checkSum+=1;

  	uint8_t checkSum_H = (checkSum & 0xff00)>>8;
    checkSum_H = 0xFF - checkSum_H;
    uint8_t checkSum_L = checkSum&0x00ff;
    // Serial.print("checksum : ");
    // Serial.print(checkSum);
    // Serial.print(", checkSum_H : ");
    // Serial.print(checkSum_H);
    // Serial.print(", checkSum_L : ");
    // Serial.println(checkSum_L);

  	sendpaket[currentPacketLen] = checkSum_H;
  	sendpaket[currentPacketLen+1] = checkSum_L;
    sendpaket[currentPacketLen+2] = ETX;
    currentPacketLen+=2;
}
int smartprotocol::varToAngle(int var)
{
  return map(var, -40, 80, 0, 250);
}
String smartprotocol::bufToString(uint8_t *buf, int buflen)
{
  String sendData;
    for(int i = 0 ; i<=buflen; i++)
    {
      sendData+=buf[i];
      sendData+=',';
    }
  return sendData;
}

void smartprotocol::printSendPacket()
{
    Serial.print("send packet : ");
    for(int i = 0 ; i<=currentPacketLen; i++)
    {
      Serial.write(sendpaket[i]);
      Serial.write(',');
    }
    Serial.println();
}