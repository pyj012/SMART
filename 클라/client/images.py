import sys, os, cv2, time,threading
from definse import *
class image():
    DEFAULT_IMG_PATH = os.path.join(sys.path[0]+'/image/')
    BG_IMG= ''
    EXIT_IMG= os.path.join(DEFAULT_IMG_PATH+'exit_button.png')
    CONNECTED_IMG=os.path.join(DEFAULT_IMG_PATH+'connected.png')
    DISCONNECTED_IMG=os.path.join(DEFAULT_IMG_PATH+'disconnected.png')
    TEST_IMG= os.path.join(DEFAULT_IMG_PATH+'background.png')
    SMART_LOGO = os.path.join(DEFAULT_IMG_PATH+'smart_logo.png')
    DONG_YANG_LOGO = os.path.join(DEFAULT_IMG_PATH+'dong_yang_logo.png')
    WHITE = os.path.join(DEFAULT_IMG_PATH+'white.png')
    INDICATOR = os.path.join(DEFAULT_IMG_PATH+'indicator.png')
    RAD_LOGO = os.path.join(DEFAULT_IMG_PATH+'rad_logo.png')