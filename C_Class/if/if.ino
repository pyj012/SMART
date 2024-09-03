void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); // <- 115200 의 속도로 시리얼 통신을 초기화함
  //pinMode(7, OUTPUT);  //<- 번호에 해당하는 아두이노의 핀을 출력 모드로 설정함
  //pinMode(8, OUTPUT);  //<- 번호에 해당하는 아두이노의 핀을 출력 모드로 설정함
}

void loop() {
  // put your main code here, to run repeatedly:

  //Serial.available()  <- 시리얼 버퍼에 쌓인 데이터(byte 단위)의 양을 반환함
  //Serial.read() <- 시리얼 버퍼에 쌓인 데이터를 1byte 가져옴
  if(Serial.available())// <- 만약 시리얼 버퍼에 쌓인 데이터가 있을 경우
  {
    int readData = Serial.read(); // <- 시리얼 버퍼에 쌓인 데이터를 1Byte 가져와서 readData 변수에 저장함
    Serial.print("Read Data : ");
    Serial.println(readData); // <- readData 변수를 시리얼 모니터에 출력함

    // if(readData == 1)
    // {
    //   digitalWrite(7, HIGH);
    // }
    //else if(readData == 2)
    //{
    // digitalWrite(8, HIGH);
    //}
    // else //<- readData가 1이나 2가 아닐때 
    // {
    //   digitalWrite(7, LOW);
    // }
  }

}
