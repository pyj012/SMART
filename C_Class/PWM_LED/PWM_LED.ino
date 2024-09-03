#include <Servo.h>
#define servoPin 11
Servo servo;
long prevTime;
int angle = 0 ;
int flag = 1;
void setup()
{
  servo.attach(servoPin);
  Serial.begin(115200);
}
void loop()
{
  if(flag)
  {
    if(millis()-prevTime>=5)
    {
      prevTime=millis();
      Serial.print("angle : ");
      Serial.println(angle);
      angle++;
      if(angle>=180)
      {
        flag=0;
        angle = 180;
      }
    }
  }
  else
  {
    if(millis()-prevTime>=5)
    {
      prevTime=millis();
      Serial.print("angle : ");
      Serial.println(angle);
      angle--;
      if(angle<=0)
      {
        flag=1;
        angle = 0;
      }
    }
  }
  servo.write(angle);
}