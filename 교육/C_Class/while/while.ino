
void setup() {
  Serial.begin(115200);
  pinMode(7,OUTPUT);
  pinMode(8,OUTPUT);
  // put your setup code here, to run once:
}
void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available())
  {
    char readData = Serial.read();
    Serial.print("Read Data : ");
    Serial.println(readData);
    if(readData == '1')
    {
      digitalWrite(7,HIGH);
    
    }
    else if(readData == '2')
    {
      digitalWrite(8,HIGH);
    }
    else
    {
      digitalWrite(7,LOW);
      digitalWrite(8,LOW);
    }
  }

}
