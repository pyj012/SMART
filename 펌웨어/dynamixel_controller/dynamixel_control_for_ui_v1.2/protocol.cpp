#include "protocol.h"

void smartprotocol::parsingprotocol(uint8_t readByte)
{
  //   if(Serial.available()>0)  
  //   {
      // uint8_t readByte = Serial.read();
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
              
              //   Serial.println("---------------------");
              //   Serial.print("CMD : ");
              //   Serial.write(protocol.controlByte);
              //   Serial.println();
              //   for(int i = 0; i<=4;i++)
              //   {
              //     Serial.print("ID : ");
              //     Serial.write(protocol.idList[i]);
              //     Serial.println();
              //     Serial.print("VALUE : ");
              //     for(int n =0; n<3; n++)
              //     {
              //       Serial.write(protocol.valueList[i][n]);
              //     }
              //     Serial.println();
              // }
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
  //   }
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


void smartprotocol::resetbuffer(char *buf)
{
  memset(buf, 0, sizeof(buf));
}

