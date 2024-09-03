#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include "define.h"
#include "protocol.h"
#include "MPU9250.h"
MPU9250 mpu;
smartprotocol smart;
IPAddress staticIP(192,168,218,100);
IPAddress gateway(192,168,218,1);
IPAddress subnet(255,255,255,0);

int prevVarValue = 0;
int prevMoveState = 0;
int sendFlag = 1;
int leftMotorSpeed = 0;
int rightMotorSpeed = 0;
int gripvalue=0;
int gripState = 0;
unsigned long prevSendTime;

int return_pitch(){
    String a = String(mpu.getPitch());
    // Serial.print(a);
    String data = "";
    data += a[0];
    data += a[1];
    data += a[2] ;
    int pitch = constrain(data.toInt(),-40,80);
    // Serial.print(":, ");
    // Serial.println(pitch); 

    int pitch_angle = smart.varToAngle(pitch);
    return pitch_angle;
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

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);

  Serial.println();
  Serial.println("Connecting to");
  Serial.println(SSID);

  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  digitalWrite(RED_LED_PIN, HIGH);
  digitalWrite(GREEN_LED_PIN, HIGH);
  pinMode(LM_PIN, INPUT_PULLUP);
  pinMode(RM_PIN, INPUT_PULLUP);

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
  digitalWrite(RED_LED_PIN, HIGH);
  digitalWrite(GREEN_LED_PIN, LOW);

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
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);
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
  int pitch_data = 0;
  while (client.connected())
  {
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, HIGH);

    if (mpu.update()) {
        static uint32_t prev_ms = millis();
        if (millis() > prev_ms + 25) {
            pitch_data=return_pitch();
            prev_ms = millis();
        }
    }
    if (millis() - prevSendTime >= 25)
    {
      prevSendTime = millis();
      // int varValue = analogRead(VAR_PIN);
      int LMValue = digitalRead(LM_PIN);
      int RMValue = digitalRead(RM_PIN);
      // int gripState = digitalRead(GRIP_PIN);

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
      // uint8_t idbuf[] = {0x35, 0x36, 0x3E, 0x3F};
      // int valuebuf[] = {angle, gripState, leftMotorSpeed, rightMotorSpeed};
      uint8_t idbuf[] = {0x35};
      int valuebuf[] = {pitch_data};
      // uint8_t idbuf[] = {0x35};
      // int valuebuf[] = {pitch_data};
      // Serial.print(", pitch : ");
      // Serial.print(pitch_data);
      // Serial.print(", left spd : ");
      // Serial.print(leftMotorSpeed);
      // Serial.print(", right spd : ");
      // Serial.println(rightMotorSpeed);

      int idLen = sizeof(idbuf);
      smart.makePacket(idbuf, idLen, valuebuf, CMD_CONTROL);
      for(int i = 0 ; i<=smart.currentPacketLen; i++)
      {
        client.write(smart.sendpaket[i]);
      }
    }
    delay(1);
  }
  Serial.println("Server Closed Try again");
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  delay(1500);
  digitalWrite(RED_LED_PIN, HIGH);
  delay(1500);
  digitalWrite(RED_LED_PIN, LOW);
}
