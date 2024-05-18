from threads import octopiclient
from PyQt5 import QtGui
from config import calibrationPosition

def getZHomeOffset(self, offset):
    '''
    Sets the spinbox value to have the value of the Z offset from the printer.
    the value is -ve so as to be more intuitive.
    :param offset:
    :return:
    '''
    self.nozzleOffsetDoubleSpinBox.setValue(-float(offset))
    self.nozzleHomeOffset = offset  # update global value of

def setZHomeOffset(self, offset, setOffset=False):
    '''
    Sets the home offset after the calibration wizard is done, which is a callback to
    the response of M114 that is sent at the end of the Wizard in doneStep()
    :param offset: the value off the offset to set. is a str is coming from M114, and is float if coming from the nozzleOffsetPage
    :param setOffset: Boolean, is true if the function call is from the nozzleOffsetPage, else the current Z value sets the offset
    :return:

    #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
    '''

    if self.setHomeOffsetBool:  # when this is true, M114 Z value will set stored as Z offset
        octopiclient.gcode(command='M206 Z{}'.format(-float(offset)))  # Convert the string to float
        self.setHomeOffsetBool = False
        octopiclient.gcode(command='M500')
        # save in EEPROM
    if setOffset:  # When the offset needs to be set from spinbox value
        octopiclient.gcode(command='M206 Z{}'.format(-offset))
        octopiclient.gcode(command='M500')

def nozzleOffset(self):
    '''
    Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
    :return:
    '''
    octopiclient.gcode(command='M503')
    self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)

def quickStep1(self):
    '''
    Shows welcome message.
    Sets Z Home Offset = 0
    Homes to MAX
    goes to position where leveling screws can be opened
    :return:
    '''

    octopiclient.gcode(
        command='M503')  # gets the value of Z offset, that would be restored later, see getZHomeOffset()
    octopiclient.gcode(command='M420 S0')  # Dissable mesh bed leveling for good measure
    octopiclient.gcode(command='M206 Z0')  # Sets Z home offset to 0
    octopiclient.home(['x', 'y', 'z'])
    octopiclient.jog(x=100, y=100, z=15, absolute=True, speed=1500)
    self.stackedWidget.setCurrentWidget(self.quickStep1Page)

def quickStep2(self):
    '''
    Askes user to release all Leveling Screws
    :return:
    '''
    self.stackedWidget.setCurrentWidget(self.quickStep2Page)
    self.movie1 = QtGui.QMovie("templates/img/calibration/calib1.gif")
    self.calib1.setMovie(self.movie1)
    self.movie1.start()

def quickStep3(self):
    '''
    leveks first position
    :return:
    '''
    self.stackedWidget.setCurrentWidget(self.quickStep3Page)
    octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=9000)
    octopiclient.jog(z=0, absolute=True, speed=1500)
    self.movie1.stop()
    self.movie2 = QtGui.QMovie("templates/img/calibration/calib2.gif")
    self.calib2.setMovie(self.movie2)
    self.movie2.start()

def quickStep4(self):
    '''
    levels second leveling position
    '''
    self.stackedWidget.setCurrentWidget(self.quickStep4Page)
    octopiclient.jog(z=10, absolute=True, speed=1500)
    octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=9000)
    octopiclient.jog(z=0, absolute=True, speed=1500)
    self.movie2.stop()
    self.movie3 = QtGui.QMovie("templates/img/calibration/calib3.gif")
    self.calib3.setMovie(self.movie3)
    self.movie3.start()

def quickStep5(self):
    '''
    levels third leveling position
    :return:
    '''
    # sent twice for some reason
    self.stackedWidget.setCurrentWidget(self.quickStep5Page)
    octopiclient.jog(z=10, absolute=True, speed=1500)
    octopiclient.jog(x=calibrationPosition['X3'], y=calibrationPosition['Y3'], absolute=True, speed=9000)
    octopiclient.jog(z=0, absolute=True, speed=1500)
    self.movie3.stop()
    self.movie4 = QtGui.QMovie("templates/img/calibration/calib4.gif")
    self.calib4.setMovie(self.movie4)
    self.movie4.start()

def quickStep6(self):
    '''
    Performs Auto bed Leveiling, required for Klipper
    '''
    self.stackedWidget.setCurrentWidget(self.quickStep6Page)
    octopiclient.gcode(command='M190 S70')
    octopiclient.gcode(command='G29')

def doneStep(self):
    '''
    decides weather to go to full calibration of return to calibration screen
    :return:
    '''

    self.stackedWidget.setCurrentWidget(self.calibratePage)
    self.movie4.stop()
    octopiclient.gcode(command='M501')  # restore eeprom settings to get Z home offset, mesh bed leveling back
    octopiclient.home(['x', 'y', 'z'])

def cancelStep(self):
    octopiclient.gcode(command='M501')  # restore eeprom settings
    self.stackedWidget.setCurrentWidget(self.calibratePage)
    try:
        self.movie1.stop()
        self.movie2.stop()
        self.movie3.stop()
        self.movie4.stop()
    except:
        pass
