
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
    camera = None 
    tryconnect_flag= 0
    connectionState=0
    servoAngleList=[125,0,0,0,0,125]
    layoutitemlist=dict()
    currentitemcount=0