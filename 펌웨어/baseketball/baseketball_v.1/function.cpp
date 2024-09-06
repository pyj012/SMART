#include "function.h"

// 각 모터들의 방향이 이상할 경우
// HIGH 와 LOW 를 반대로 적용해보며 알맞은 방향을 찾을것.

//엘레베이터 관한 함수
void ELV_CTRL(int cmd = 0, int spd = 125)
{
  digitalWrite(ELVA_PIN, HIGH);
  analogWrite(ELVSPD_PIN, spd);

  if(cmd == UP)
  {
    digitalWrite(ELV1_PIN, HIGH);
    digitalWrite(ELV2_PIN, LOW);
  }
  else if(cmd == DOWN)
  {
    digitalWrite(ELV1_PIN, LOW);
    digitalWrite(ELV2_PIN, HIGH);
  }
  else
  {
    digitalWrite(ELVA_PIN, LOW);
    digitalWrite(ELV1_PIN, LOW);
    digitalWrite(ELV2_PIN, LOW);
  }
}

// 아래 공 집는 함수
void ROLLOR_CTRL(int cmd = 0, int spd = 125)
{
  digitalWrite(ROLLORA_PIN, HIGH);
  digitalWrite(ROLLORB_PIN, HIGH);
  analogWrite(ROLLORSPD_PIN, spd);

  if(cmd == IN)
  {
    digitalWrite(ROLLOR1_PIN, HIGH);
    digitalWrite(ROLLOR2_PIN, LOW);
    digitalWrite(ROLLOR3_PIN, LOW);
    digitalWrite(ROLLOR4_PIN, HIGH);
  }
  else if(cmd == OUT)
  {
    digitalWrite(ROLLOR1_PIN, LOW);
    digitalWrite(ROLLOR2_PIN, HIGH);
    digitalWrite(ROLLOR3_PIN, HIGH);
    digitalWrite(ROLLOR4_PIN, LOW);
  }
  else
  {
    digitalWrite(ROLLORA_PIN, LOW);
    digitalWrite(ROLLORB_PIN, LOW);
    digitalWrite(ROLLOR1_PIN, LOW);
    digitalWrite(ROLLOR2_PIN, LOW);
    digitalWrite(ROLLOR3_PIN, LOW);
    digitalWrite(ROLLOR4_PIN, LOW);
  }
}

// 로봇 주행에 관한 함수
void DIRECTION_CTRL(int cmd = 0, int spd = 125)
{
  digitalWrite(LMA_PIN, HIGH);
  digitalWrite(RMB_PIN, HIGH);
  analogWrite(LRSPD_PIN, spd);

  if(cmd == STRIGHT)
  {
    digitalWrite(LM1_PIN, HIGH);
    digitalWrite(LM2_PIN, LOW);
    digitalWrite(RM3_PIN, LOW);
    digitalWrite(RM4_PIN, HIGH);
  }
  else if(cmd == BACK)
  {
    digitalWrite(LM1_PIN, LOW);
    digitalWrite(LM2_PIN, HIGH);
    digitalWrite(RM3_PIN, HIGH);
    digitalWrite(RM4_PIN, LOW);
  }
  else if(cmd == LEFT)
  {
    digitalWrite(LM1_PIN, HIGH);
    digitalWrite(LM2_PIN, LOW);
    digitalWrite(RM3_PIN, HIGH);
    digitalWrite(RM4_PIN, LOW);
  }
  else if(cmd == RIGHT)
  {
    digitalWrite(LM1_PIN, LOW);
    digitalWrite(LM2_PIN, HIGH);
    digitalWrite(RM3_PIN, LOW);
    digitalWrite(RM4_PIN, HIGH);
  }
  else
  {
    digitalWrite(LMA_PIN, LOW);
    digitalWrite(RMB_PIN, LOW);
    digitalWrite(LM1_PIN, LOW);
    digitalWrite(LM2_PIN, LOW);
    digitalWrite(RM3_PIN, LOW);
    digitalWrite(RM4_PIN, LOW);
  }
}

