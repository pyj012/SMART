LM_A = 5
LM_B = 6
RM_A = 13
RM_B = 19

LM_SPD = 26
RM_SPD = 20
    
class protocol():
    STX = 0x02
    ETX = 0x03
    CMD_CONTROL = 0xC0
    CMD_ANSWER = 0xA0

class pages():
    main_page = None
    aimode_page= None
    techingmode_page=None
    
class database():
    tryconnect_flag= 0
    connectionState=0
    servoAngleList=[125,0,0,0,0,125]
    layoutitemlist=dict()
    currentitemcount=0