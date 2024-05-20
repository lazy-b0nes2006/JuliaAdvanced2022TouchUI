import keyboard
from PyQt5 import QtCore

def keyboard_connections(self):
    self.wifiSettingsSSIDKeyboardButton.pressed.connect(
        lambda: self.startKeyboard(self.wifiSettingsComboBox.addItem))

def startKeyboard(self, returnFn, onlyNumeric=False, noSpace=False, text=""):
    '''
    starts the keyboard screen for entering Password
    '''
    keyBoardobj = keyboard.Keyboard(onlyNumeric=onlyNumeric, noSpace=noSpace, text=text)
    keyBoardobj.keyboard_signal.connect(returnFn)
    keyBoardobj.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    keyBoardobj.show()
