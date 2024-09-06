#include <WiFiNINA.h>
#include <Arduino_LSM6DS3.h>
#include <PubSubClient.h>
#include "define.h"

IPAddress staticIP(192,168,20,100);
const char* mqtt_server = "192.168.20.2";

int prevVarValue = 0;
int prevMoveState = 0;
int sendFlag = 1;
int leftMotorSpeed = 0;
int rightMotorSpeed = 0;
int gripvalue=0;
int gripState = 0;
unsigned long prevrefreshTime;
int server_err=1;

float gyro_x, gyro_y, gyro_z;

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

  WiFi.config(staticIP);
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

  if (!IMU.begin()) 
  {
  Serial.println("LSM6DS3센서 오류!");
  while (1);
  }
  Serial.print(IMU.accelerationSampleRate());
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);
}

void loop()
{
  WiFiClient wificlient;
  PubSubClient client(mqtt_server, HOST_PORT, wificlient);
  Serial.print("Try Connecting to ");
  Serial.println(HOST_IP);

  if (!client.connect("ARDUNINO"))
  {
    Serial.println("Host Connection Fail");
    delay(1000);
  }
  else
  {
    Serial.println("Server Connected");
    delay(100);
  }
  int pitch_data = 0;
  int speed_data = 0;
  
  String databuffer;

  while (client.connected())
  {
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, HIGH);
    if(millis() - prevrefreshTime >= 10)
    {
      prevrefreshTime= millis();
      if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(gyro_x, gyro_y, gyro_z);
      }
    // int varValue = analogRead(VAR_PIN);
    int LMValue = digitalRead(LM_PIN);
    int RMValue = digitalRead(RM_PIN);

    pitch_data = constrain(int(map(round(gyro_x*100), 100, -100,0,250)),0,250); 
    uint8_t idbuf[] = {0x35, 0x3E, 0x3F};
    int valuebuf[] = {pitch_data, speed_data, speed_data};
    databuffer+='{';
    for(int i =0; i<3; i++)
    {
      databuffer += idbuf[i];
      databuffer +=':';
      databuffer += valuebuf[i];
      databuffer +=',';
    }
    databuffer.remove(databuffer.length()-1);
    databuffer+='}';
    int databufferlen = databuffer.length()+1;
    char send_value[databufferlen]={};
    databuffer.toCharArray(send_value, databufferlen);
    client.publish("leftController", send_value);
    speed_data+=1;
    speed_data%=255;
    databuffer = "";
    }
  delay(1);
  }
  Serial.println("Server Closed Try again");
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  delay(500);
  digitalWrite(RED_LED_PIN, HIGH);
  delay(500);
  digitalWrite(RED_LED_PIN, LOW);
  server_err=1;
}
