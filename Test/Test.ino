// void makep(String idbuf, char cmd, String databuf)
// {
//     char sendpaket[99]={};
//     sendpaket[0]= STX;
//     sendpaket[1]= len_h;
//     sendpaket[2]= len_l;
//     sendpaket[3]= cmd;
    
//     for(int id_num = 0; id_num<idbuf.length; id_num++)
//     {   
//         if(idbuf[id_num] == ',');

//     }
// }
#define STX 'A' 
#define ETX 'B'
#define CONTROL 'C'
void makep(int *idbuf, int *valuebuf, char cmd)
{
    char sendpaket[99]={};

    sendpaket[0]= STX;
    Serial.print("send packet : ");
    Serial.println(sendpaket);
    sendpaket[1]= '0';
    sendpaket[2]= '1';
    sendpaket[3]= cmd;
    int packetLen = 4;

    int idLen = sizeof(idbuf);
	int valueLen = sizeof(valuebuf);
  
    for(int i =0; i<=idLen; i++)
    {

     String data = String(valuebuf[i]);  
      String idtemp = String(idbuf[i]);
      char id = idtemp[0];
      char data1 = data[0];
      char data2 = data[1];
      char data3 = data[2];
      sendpaket[packetLen] = id;
      sendpaket[packetLen+1] = data1;
      sendpaket[packetLen+2] = data2;
      sendpaket[packetLen+3] = data3;
      // Serial.print("value : ");
      // Serial.println(sendpaket[packetLen]);
      packetLen+=4;
      
    }
    sendpaket[packetLen] = ETX;
    Serial.print("send packet : ");
    for(int i = 0 ; i<=packetLen; i++)
    {
      Serial.write(sendpaket[i]);
      Serial.write(', ');
    }

    // Serial.print("idbuf: ");
    // Serial.println(idbuf);  
    // Serial.print("databuf : ");
    // Serial.println(databuf);
    // Serial.print("packet : ");
    // Serial.println(sendpaket);
    // int sizeV = sizeof(databuf)/sizeof(databuf[0]);
    // for(int i =0; i<sizeV; i++)
    // {
    //   Serial.println(databuf[i]);
    // }
    
    // for(int i = 0 ;idbuf<sizeof(idbuf); i++)
    // {
    //   sendpaket[i]=idbuf[i]
    // }
}
int idbuf[] = {1,2,3};
int valuebuf[] = {123,456,789};
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  delay(1000);
  makep(idbuf, valuebuf, CONTROL);

}

void loop() {
  // put your main code here, to run repeatedly:
  // Serial.println();
  delay(1000);
}
