#define DIR_1_PIN 26
#define DIR_2_PIN 27
#define SPEED_PIN 7
#define ENCODER_A_PIN 22
#define ENCODER_B_PIN 23
#define ENCODER_C_PIN 24
#define ENCODER_D_PIN 25

void setup() {
  // put your setup code here, to run once:

  pinMode(DIR_1_PIN, OUTPUT);
  pinMode(DIR_2_PIN, OUTPUT);
  pinMode(SPEED_PIN, OUTPUT);
  pinMode(ENCODER_A_PIN, INPUT);
  pinMode(ENCODER_B_PIN, INPUT);
  pinMode(ENCODER_C_PIN, INPUT);
  pinMode(ENCODER_D_PIN, INPUT);

  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(DIR_1_PIN, HIGH);
  digitalWrite(DIR_2_PIN, LOW);
  for(int speed=0; speed<=255; speed+=10)
  {
    analogWrite(SPEED_PIN, speed);
    Serial.print("LEFT SPEED : ");
    Serial.println(speed);
    delay(100);
  }
  analogWrite(SPEED_PIN, 0);
  delay(1000);

  digitalWrite(DIR_1_PIN, LOW);
  digitalWrite(DIR_2_PIN, HIGH);
  for(int speed=0; speed<=255; speed+=10)
  {
    analogWrite(SPEED_PIN, speed);
    Serial.print("RIGHT SPEED : ");
    Serial.println(speed);
    delay(100);
  }
  analogWrite(SPEED_PIN, 0);
  delay(1000);
}
