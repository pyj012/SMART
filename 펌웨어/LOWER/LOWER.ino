
// VRH |    VRM      |    VRL     | GND    |   SPEED   |   ALARM
//           30           GND                    A0
// NC  | ALARM_RESET |(INT.VR/EXT)|(CW/CCW)|(RUN/BREAK)|(STOP/START)
//                                    31       32            33
// if you control to motor, turn on signal one by one, with 10ms delay
// RUN and START pin alwasy need to HIGH signal 
#define SPEED_PIN 30
#define CW_CCW_PIN 31
#define RUN_BREAK_PIN 32
#define STOP_START_PIN 33
unsigned int currentSpeed = 200;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  for(int pin = 30; pin<34;pin++)
  {
    pinMode(pin, OUTPUT);
  }
  pinMode(7, OUTPUT);

  digitalWrite(RUN_BREAK_PIN, HIGH);
  delay(20);
  digitalWrite(STOP_START_PIN, HIGH);
  delay(20);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println();
  analogWrite(7, currentSpeed);
}
