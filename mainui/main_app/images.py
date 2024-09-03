import sys, os
class image():
    DEFAULT_IMG_PATH = os.path.join(sys.path[0]+'/image/')
    BG_IMG= ''
    EXIT_IMG= os.path.join(DEFAULT_IMG_PATH+'exit_button.png')
    CONNECTED_IMG=os.path.join(DEFAULT_IMG_PATH+'connected.png')
    DISCONNECTED_IMG=os.path.join(DEFAULT_IMG_PATH+'disconnected.png')
    TEST_IMG= os.path.join(DEFAULT_IMG_PATH+'background.png')