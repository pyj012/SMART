import RPi.GPIO as GPIO
import time
from defines import *
GPIO.setmode(GPIO.BCM)

GPIO.setup(LM_A, GPIO.OUT)
GPIO.setup(LM_B, GPIO.OUT)
GPIO.setup(RM_A, GPIO.OUT)
GPIO.setup(RM_B, GPIO.OUT)
GPIO.setup(LM_SPD, GPIO.OUT)
GPIO.setup(RM_SPD, GPIO.OUT)

LM_PWM = GPIO.PWM(LM_SPD, 100)
RM_PWM = GPIO.PWM(RM_SPD, 100)

LM_PWM.start(0)
RM_PWM.start(0)

def foward(l_spd = 0, r_spd=0):
    GPIO.output(LM_A, 0)
    GPIO.output(LM_B, 1)
    LM_PWM.ChangeDutyCycle(l_spd)

    GPIO.output(RM_A, 1)
    GPIO.output(RM_B, 0)
    RM_PWM.ChangeDutyCycle(r_spd)

def backward(l_spd = 0, r_spd=0):
    GPIO.output(LM_A, 1)
    GPIO.output(LM_B, 0)
    LM_PWM.ChangeDutyCycle(l_spd)

    GPIO.output(RM_A, 0)
    GPIO.output(RM_B, 1)
    RM_PWM.ChangeDutyCycle(r_spd)

def stop():
    LM_PWM.ChangeDutyCycle(0)
    RM_PWM.ChangeDutyCycle(0)
    GPIO.output(RM_A, 0)
    GPIO.output(RM_B, 0)
    GPIO.output(LM_A, 0)
    GPIO.output(LM_B, 0)

while(1):
    try:
        foward(50, 50)
        time.sleep(1)

        stop()
        time.sleep(1)

        backward(50, 50)

        time.sleep(1)

        stop()  
        time.sleep(1)
        
    # except Exception as e:
    #     print(e)

    except:
        GPIO.cleanup()

