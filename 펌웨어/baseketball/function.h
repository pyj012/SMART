#include <Arduino.h>

// 프로그램에 사용되는 단어.
// 모터 정지
#define STOP 0

// 엘리베이터 업, 다운
#define UP 1
#define DOWN 2

// 모터 직진, 좌회전, 우회전
#define STRIGHT 1
#define BACK 2
#define LEFT 3
#define RIGHT 4

// 롤러 안쪽, 바깥쪽 회전
#define IN 1
#define OUT 2


// <<<핀번호 설정, 핀번호를 확인하여 배선 진행>>>
//l298n 체인 엘리베이터
#define ELVSPD_PIN 13
#define ELVA_PIN 22
#define ELV1_PIN 23
#define ELV2_PIN 24

//l298n2 아래 밀어 넣어주는거
#define ROLLORSPD_PIN 12
#define ROLLORA_PIN 2
#define ROLLOR1_PIN 3
#define ROLLOR2_PIN 4

#define ROLLORB_PIN 7
#define ROLLOR3_PIN 5
#define ROLLOR4_PIN 6

//l298n3, 왼쪽 모터, 오른쪽 모터
#define LRSPD_PIN 11
#define LMA_PIN 25
#define LM1_PIN 26
#define LM2_PIN 27

#define RMB_PIN 8
#define RM3_PIN 9
#define RM4_PIN 10

void ELV_CTRL(int cmd, int spd);
void ROLLOR_CTRL(int cmd, int spd );
void DIRECTION_CTRL(int cmd, int spd);