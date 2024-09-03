#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include "define.h"
#include "protocol.h"
smartprotocol smart;
IPAddress staticIP(192,168,20,100);
IPAddress gateway(192,168,20,1);
IPAddress subnet(255,255,255,0);
int prevVarValue = 0;
int prevMoveState = 0;
int sendFlag = 1;
int leftMotorSpeed = 0;
int rightMotorSpeed = 0;
unsigned long prevSendTime;

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println();
  Serial.println("Connecting to");
  Serial.println(SSID);

  pinMode(SWITCH_FOWARD_PIN, INPUT_PULLUP);
  pinMode(SWITCH_BACKWARD_PIN, INPUT_PULLUP);
  WiFi.config(staticIP, gateway, subnet);
  if (!WiFi.mode(WIFI_STA))
    Serial.println("Mode Set Fail");
  if (!WiFi.begin(SSID, PSW))
    Serial.println("WiFi Connect Fail");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print('.');
  }

  Serial.println();
  Serial.println("WiFI Connected!");
  Serial.print("My ip is : ");
  Serial.println(WiFi.localIP());
}

void loop()
{
  WiFiClient client;
  Serial.print("Try Connecting to ");
  Serial.println(HOST_IP);
  if (!client.connect(HOST_IP, HOST_PORT))
  {
    Serial.println("Host Connection Fail");
    delay(5000);
  }
  else
  {
    // client.println(ip);
    Serial.println("Server Connected");
    delay(100);
  }
  String sendValue;
  while (client.connected())
  {
    if (millis() - prevSendTime >= 50)
    {
      prevSendTime = millis();
      int varValue = analogRead(VAR_PIN);
      int fowardValue = digitalRead(SWITCH_FOWARD_PIN);
      int backwardValue = digitalRead(SWITCH_BACKWARD_PIN);
      int currendMoveState = 0;
      if (fowardValue == 0)
        currendMoveState = 1;
      else if (backwardValue == 0)
        currendMoveState = 2;
      if ((fowardValue == 0) && (backwardValue == 0))
        currendMoveState = 0;
      if (prevVarValue != varValue)
      {
        prevVarValue = varValue;
        //sendFlag = 1;
      }
      if (prevMoveState != currendMoveState)
      {
        prevMoveState = currendMoveState;
        //sendFlag = 1;
      }
      int angle = smart.varToAngle(varValue);
      if (currendMoveState == 0)
      {
        leftMotorSpeed = 0;
        rightMotorSpeed = 0;
      }
      else if (currendMoveState == 1)
      {
        leftMotorSpeed = 100;
        rightMotorSpeed = 100;
      }
      else if (currendMoveState == 2)
      {
        leftMotorSpeed = -100;
        rightMotorSpeed = -100;
      }
      // uint8_t idbuf[] = {0x35, 0x3E, 0x3F};
      // int valuebuf[] = {angle, leftMotorSpeed, rightMotorSpeed};

      uint8_t idbuf[] = {0x3F};
      int valuebuf[] = {1};
      int idLen = sizeof(idbuf);
      smart.makePacket(idbuf, idLen, valuebuf, CMD_CONTROL);
      sendValue = smart.bufToString(smart.sendpaket, smart.currentPacketLen);
      for(int i = 0 ; i<smart.currentPacketLen; i++)
      {
        client.write(smart.sendpaket[i]);
      }
      sendValue = "";
      // if (sendFlag)
      // {
      //   uint8_t idbuf[] = {0x35, 0x3E, 0x3F};
      //   int valuebuf[] = {angle, leftMotorSpeed, rightMotorSpeed};
      //   int idLen = sizeof(idbuf);
      //   smart.makePacket(idbuf, idLen, valuebuf, CMD_CONTROL);
      //   sendValue = smart.bufToString(smart.sendpaket, smart.currentPacketLen);
      //   client.print(sendValue);
      //   sendValue = "";
      //   sendFlag = 0;
      // }
    }
    delay(1);
  }
  Serial.println("Server Closed Try again");
  delay(3000);
}
