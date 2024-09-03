#ifndef DEFINE_H
#define DEFINE_H

#include <Arduino.h>
#include "MPU9250.h"
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include "protocol.h"

#define SSID "testsmart"
#define PSW "00000000"
#define HOST_IP "192.168.20.3"
#define HOST_PORT 5051

#define VAR_PIN A0
#define SWITCH_FOWARD_PIN D5
#define SWITCH_BACKWARD_PIN D6
#define GRIP_PIN D7
MPU9250 mpu;
IPAddress staticIP(192,168,20,100);
IPAddress gateway(192,168,20,1);
IPAddress subnet(255,255,255,0);
smartprotocol smart;
int prevVarValue = 0;
int prevMoveState = 0;
int sendFlag = 1;
int leftMotorSpeed = 0;
int rightMotorSpeed = 0;
int gripvalue=0;
int gripState = 0;
int roll_data=0;
unsigned long prevSendTime;
int return_roll(){
    String a = String(mpu.getRoll());
    Serial.print(a);
    String data = "";
    data += a[0];
    data += a[1];
    data += a[2] ;
    int roll = data.toInt();
    Serial.print(":, ");
    Serial.println(roll);
    int roll_angle = smart.varToAngle(roll);
    return roll_angle;
}

void print_calibration() {
    Serial.println("< calibration parameters >");
    Serial.println("accel bias [g]: ");
    Serial.print(mpu.getAccBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getAccBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getAccBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.println();
    Serial.println("gyro bias [deg/s]: ");
    Serial.print(mpu.getGyroBiasX() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getGyroBiasY() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getGyroBiasZ() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.println();
    Serial.println("mag bias [mG]: ");
    Serial.print(mpu.getMagBiasX());
    Serial.print(", ");
    Serial.print(mpu.getMagBiasY());
    Serial.print(", ");
    Serial.print(mpu.getMagBiasZ());
    Serial.println();
    Serial.println("mag scale []: ");
    Serial.print(mpu.getMagScaleX());
    Serial.print(", ");
    Serial.print(mpu.getMagScaleY());
    Serial.print(", ");
    Serial.print(mpu.getMagScaleZ());
    Serial.println();
}
void init_sequnce()
{
  Serial.begin(115200);
  Serial.println();
  Serial.println("Connecting to");
  Serial.println(SSID);

  pinMode(SWITCH_FOWARD_PIN, INPUT_PULLUP);
  pinMode(SWITCH_BACKWARD_PIN, INPUT_PULLUP);
  pinMode(GRIP_PIN, INPUT_PULLUP);
  
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

  Wire.begin();
  delay(2000);

  if (!mpu.setup(0x68)) {  // change to your own address
      while (1) {
          Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
          delay(5000);
      }
  }

  // calibrate anytime you want to
  Serial.println("Accel Gyro calibration will start in 5sec.");
  Serial.println("Please leave the device still on the flat plane.");
  mpu.verbose(true);
  delay(5000);
  mpu.calibrateAccelGyro();

  Serial.println("Mag calibration will start in 5sec.");
  Serial.println("Please Wave device in a figure eight until done.");
  delay(5000);
  mpu.calibrateMag();

  print_calibration();
  mpu.verbose(false);
}

void refresh_gyro()
{
   if (mpu.update()) {
        static uint32_t prev_ms = millis();
        if (millis() > prev_ms + 25) {
            roll_data=return_roll();
            prev_ms = millis();
        }
    }
}
void refresh_sensor()
{
  // int varValue = analogRead(VAR_PIN);
  int fowardValue = digitalRead(SWITCH_FOWARD_PIN);
  int backwardValue = digitalRead(SWITCH_BACKWARD_PIN);
  int gripState = digitalRead(GRIP_PIN);

  int currendMoveState = 0;
  if (fowardValue == 0)
    currendMoveState = 1;
  else if (backwardValue == 0)
    currendMoveState = 2;
  if ((fowardValue == 0) && (backwardValue == 0))
    currendMoveState = 0;
  // if (prevVarValue != varValue)
  // {
  //   prevVarValue = varValue;
  // }
  if (prevMoveState != currendMoveState)
  {
    prevMoveState = currendMoveState;
  }
  if (gripState ==0)
  {
    gripvalue= 240;
  }
  else
  {
    gripvalue=0;
  }
  
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
}
void package_data()
{
    // uint8_t idbuf[] = {0x35, 0x36, 0x3E, 0x3F};
    // int valuebuf[] = {angle, gripState, leftMotorSpeed, rightMotorSpeed};
    uint8_t idbuf[] = {0x35, 0x36};
    int valuebuf[] = {roll_data, gripvalue};
    // Serial.print(", roll : ");
    // Serial.print(roll_data);
    // Serial.print(", left spd : ");
    // Serial.print(leftMotorSpeed);
    // Serial.print(", right spd : ");
    // Serial.println(rightMotorSpeed);

    int idLen = sizeof(idbuf);
    smart.makePacket(idbuf, idLen, valuebuf, CMD_CONTROL);
}

void main_loop()
{
  WiFiClient client;
  Serial.print("Try Connecting to ");
  Serial.println(HOST_IP);
  while (client.connected())
  {
    if (millis() - prevSendTime >= 25)
    {
      prevSendTime = millis();
      refresh_sensor();
      package_data();
      for(int i = 0 ; i<=smart.currentPacketLen; i++)
      {
        client.write(smart.sendpaket[i]);
      }
    }
  }
  Serial.println("Server Closed Try again");
  delay(3000);
}
#endif
