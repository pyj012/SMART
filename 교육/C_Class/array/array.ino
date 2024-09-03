int arry_int[5]={};
char arry_char[5]={};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); // <- 115200 의 속도로 시리얼 통신을 초기화함

  for(int num = 0; num<5; num++)
  {
    arry_int[num]= num;
    arry_char[num]=num;
  }

  Serial.print("int arry : ");
  for(int num = 0; num<5; num++)
  {
    Serial.println(arry_int[num]);
  }
  Serial.print("char arry : ");
  for(int num = 0; num<5; num++)
  {
    Serial.println(arry_char[num]);
  }
}

void loop() {
  // put your main code here, to run repeatedly:



}
