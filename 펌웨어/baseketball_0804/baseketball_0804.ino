#include "function.h"
#define BLE Serial1

// 각 모터들의 동작속도는 여기서 설정함. 0~255 아마 전압이 부족하여 너무 낮은 값에서는 변화가 없을것임.
int DIRECTION_SPD = 125;
int ELV_SPD = 125;
int ROLLOR_SPD = 125;

// 블루투스에서 읽어온 문자를 저장하는 변수
char readData;

// 마지막 움직인 시간을 저장하는 변수
unsigned long prevWorkMillis = 0;
unsigned long printMillis=0;
//최소 동작 시간
int moveTime = 300;

//시리얼 모니터에 출력하는 주기
int printTime=500;

void setup() {
  // put your setup code here, to run once:
  for(int pin = 7;pin <= 13;pin++)
  {
    pinMode(pin, OUTPUT);
  }
  for(int pin = 22;pin <= 27;pin++)
  {
    pinMode(pin, OUTPUT);
  }

  Serial.begin(115200);

  // 블루투스와의 시리얼통신을 9600 으로 설정함, 블루투스 초기 설정 필요
  BLE.begin(9600);

  //하단 롤러 동작
  ROLLOR_CTRL(IN, ROLLOR_SPD); 
  //ROLLOR_CTRL(OUT, ROLLOR_SPD); 
}

void loop() {
  // put your main code here, to run repeatedly:

  //블루투스에서 데이터를 한문자 읽어옴
  if(BLE.available()>0)
  {
   readData = BLE.read();
   Serial.print("BLE : ");
   Serial.println(readData);
  }

  //전진 후진 직진 우회전 제어 쪽, 앱에서 키에 해당 문자를 배정하고 누르면 동작함.
  if(readData =='w')
    DIRECTION_CTRL(STRIGHT, DIRECTION_SPD);
  else if(readData =='s')
    DIRECTION_CTRL(BACK, DIRECTION_SPD);
  else if(readData =='a')
    DIRECTION_CTRL(LEFT, DIRECTION_SPD);
  else if(readData =='d')
    DIRECTION_CTRL(RIGHT, DIRECTION_SPD);
    
  // else if(readData =='b')
  //   DIRECTION_CTRL(STOP, 0);

  //공을 올리는 엘레베이터 방향 설정
  else if(readData =='u')
    ELV_CTRL(UP, ELV_SPD);  
  else if(readData =='n')
    ELV_CTRL(DOWN, ELV_SPD);  

  // else if(readData =='b')
  //   ELV_CTRL(STOP, 0);  

  // 수신 받은 데이터를 바로 초기화 시킨다.
  readData = '';

  // 블루투스로 입력받은 값이 없거나, 이상한 값이 받아졌을 경우 모든 동작을 중지함. 주석처리해도 되고 안해도 되고
  // else
  // {
  //   DIRECTION_CTRL(STOP, 0);  
  //   ROLLOR_CTRL(STOP, 0);  
  //   ELV_CTRL(STOP, 0);  
  // }

  // b 를 입력받으면 로봇의 움직임과 엘레베이가 정지함. 알아서 변경 및 사용 

  // 기존 방식은 블루투스로 입력받은 값이 계속 남아있어 마지막 명령을 계속 수행하게 됨.<- 무시
  // 아래의 if 문의 주석을 해제할 경우 마지막으로 전송받은 명령의 시간을 기준으로 
  // 최소 동작 시간만큼 동작하고 입력받은 값을 삭제하여, 마지막 명령을 계속 수행하지 않음.
  // if(millis() - prevWorkMillis>=moveTime)
  // {
  //   prevWorkMillis=millis();
  //   readData = '';
  // }
}
