import sys
from config import *
from decorators import run_async
from network_utils import *
#from buzzer_feedback import *
from button_feedback import *
from gui_elements import *
from threads import *
from socket_qt import *


#if not Development:
    #import RPi.GPIO as GPIO
    #GPIO.setmode(GPIO.BCM)  # Use the board numbering scheme
    #GPIO.setwarnings(False)  # Disable GPIO warnings H

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Intialize the library (must be called once before other functions).
    # Creates an object of type MainUiClass
    MainWindow = MainUiClass()
    MainWindow.show()
    # MainWindow.showFullScreen()
    # MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    # Create NeoPixel object with appropriate configuration.
    # charm = FlickCharm()
    # charm.activateOn(MainWindow.FileListWidget)
    print("hi")
sys.exit(app.exec_())
