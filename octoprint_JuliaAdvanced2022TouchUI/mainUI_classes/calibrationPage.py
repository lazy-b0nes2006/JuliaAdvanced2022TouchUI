from config import calibrationPosition
from PyQt5 import QtGui
from threads import octopiclient

class calibrationPage:
    def __init__(self, obj):
        self.obj = obj
        obj.QtSocket.z_home_offset_signal.connect(self.getZHomeOffset)

        obj.calibrateBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.MenuPage))
        obj.nozzleOffsetButton.pressed.connect(self.nozzleOffset)
        # the -ve sign is such that its converted to home offset and not just distance between nozzle and bed
        obj.nozzleOffsetSetButton.pressed.connect(
            lambda: obj.setZHomeOffset(self.nozzleOffsetDoubleSpinBox.value(), True))
        obj.nozzleOffsetBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.calibratePage))
        #Bypass calibration wizzard page for not using Klipper
        # self.calibrationWizardButton.clicked.connect(
        #     lambda: self.stackedWidget.setCurrentWidget(obj.calibrationWizardPage))
        obj.calibrationWizardButton.clicked.connect(self.quickStep1)

        obj.calibrationWizardBackButton.clicked.connect(
            lambda: obj.stackedWidget.setCurrentWidget(obj.calibratePage))
        #required for Klipper
        # obj.quickCalibrationButton.clicked.connect(obj.quickStep6)
        # obj.fullCalibrationButton.clicked.connect(obj.quickStep1)

        obj.quickStep1NextButton.clicked.connect(self.quickStep2)
        obj.quickStep2NextButton.clicked.connect(self.quickStep3)
        obj.quickStep3NextButton.clicked.connect(self.quickStep4)
        obj.quickStep4NextButton.clicked.connect(self.quickStep5)
        obj.quickStep5NextButton.clicked.connect(self.doneStep)
        # Required for Klipper
        # obj.quickStep5NextButton.clicked.connect(self.quickStep6)
        # obj.quickStep6NextButton.clicked.connect(self.doneStep)

        # obj.moveZPCalibrateButton.pressed.connect(lambda: octopiclient.jog(z=-0.05))
        # obj.moveZPCalibrateButton.pressed.connect(lambda: octopiclient.jog(z=0.05))
        obj.quickStep1CancelButton.pressed.connect(self.cancelStep)
        obj.quickStep2CancelButton.pressed.connect(self.cancelStep)
        obj.quickStep3CancelButton.pressed.connect(self.cancelStep)
        obj.quickStep4CancelButton.pressed.connect(self.cancelStep)
        obj.quickStep5CancelButton.pressed.connect(self.cancelStep)
        # obj.quickStep6CancelButton.pressed.connect(self.cancelStep)

    def getZHomeOffset(self, offset):
        '''
        Sets the spinbox value to have the value of the Z offset from the printer.
        the value is -ve so as to be more intuitive.
        :param offset:
        :return:
        '''
        self.obj.nozzleOffsetDoubleSpinBox.setValue(-float(offset))
        self.obj.nozzleHomeOffset = offset

    def setZHomeOffset(self, offset, setOffset=False):
        '''
        Sets the home offset after the calibration wizard is done, which is a callback to
        the response of M114 that is sent at the end of the Wizard in doneStep()
        :param offset: the value off the offset to set. is a str is coming from M114, and is float if coming from the nozzleOffsetPage
        :param setOffset: Boolean, is true if the function call is from the nozzleOffsetPage, else the current Z value sets the offset
        :return:

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''

        if self.obj.setHomeOffsetBool:
            octopiclient.gcode(command='M206 Z{}'.format(-float(offset)))
            self.obj.setHomeOffsetBool = False
            octopiclient.gcode(command='M500')
            # save in EEPROM
        if setOffset:    # When the offset needs to be set from spinbox value
            octopiclient.gcode(command='M206 Z{}'.format(-offset))
            octopiclient.gcode(command='M500')

    def nozzleOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        octopiclient.gcode(command='M503')
        self.obj.stackedWidget.setCurrentWidget(self.obj.nozzleOffsetPage)

    def quickStep1(self):
        '''
        Shows welcome message.
        Sets Z Home Offset = 0
        Homes to MAX
        goes to position where leveling screws can be opened
        :return:
        '''

        octopiclient.gcode(command='M503')
        octopiclient.gcode(command='M420 S0')
        octopiclient.gcode(command='M206 Z0')
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.jog(x=100, y=100, z=15, absolute=True, speed=1500)
        self.obj.stackedWidget.setCurrentWidget(self.obj.quickStep1Page)

    def quickStep2(self):
        '''
        Askes user to release all Leveling Screws
        :return:
        '''
        self.obj.stackedWidget.setCurrentWidget(self.obj.quickStep2Page)
        self.obj.movie1 = QtGui.QMovie("templates/img/calibration/calib1.gif")
        self.obj.calib1.setMovie(self.obj.movie1)
        self.obj.movie1.start()

    def quickStep3(self):
        '''
        leveks first position
        :return:
        '''
        self.obj.stackedWidget.setCurrentWidget(self.obj.quickStep3Page)
        octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=9000)
        octopiclient.jog(z=0, absolute=True, speed=1500)
        self.obj.movie1.stop()
        self.obj.movie2 = QtGui.QMovie("templates/img/calibration/calib2.gif")
        self.obj.calib2.setMovie(self.obj.movie2)
        self.obj.movie2.start()

    def quickStep4(self):
        '''
        levels second leveling position
        '''
        self.obj.stackedWidget.setCurrentWidget(self.obj.quickStep4Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=9000)
        octopiclient.jog(z=0, absolute=True, speed=1500)
        self.obj.movie2.stop()
        self.obj.movie3 = QtGui.QMovie("templates/img/calibration/calib3.gif")
        self.obj.calib3.setMovie(self.obj.movie3)
        self.obj.movie3.start()

    def quickStep5(self):
        '''
        levels third leveling position
        :return:
        '''
        self.obj.stackedWidget.setCurrentWidget(self.obj.quickStep5Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.jog(x=calibrationPosition['X3'], y=calibrationPosition['Y3'], absolute=True, speed=9000)
        octopiclient.jog(z=0, absolute=True, speed=1500)
        self.obj.movie3.stop()
        self.obj.movie4 = QtGui.QMovie("templates/img/calibration/calib4.gif")
        self.obj.calib4.setMovie(self.obj.movie4)
        self.obj.movie4.start()

    # def quickStep6(self):
    #     '''
    #     Performs Auto bed Leveiling, required for Klipper
    #     '''
    #     self.obj.stackedWidget.setCurrentWidget(self.obj.quickStep6Page)
    #     octopiclient.gcode(command='M190 S70')
    #     octopiclient.gcode(command='G29')

    def doneStep(self):
        '''
        decides weather to go to full calibration of return to calibration screen
        :return:
        '''

        self.obj.stackedWidget.setCurrentWidget(self.obj.calibratePage)
        self.obj.movie4.stop()
        octopiclient.gcode(command='M501')
        octopiclient.home(['x', 'y', 'z'])

    def cancelStep(self):
        octopiclient.gcode(command='M501')
        self.obj.stackedWidget.setCurrentWidget(self.obj.calibratePage)
        try:
            self.obj.movie1.stop()
            self.obj.movie2.stop()
            self.obj.movie3.stop()
            self.obj.movie4.stop()
        except:
            pass
