from MainUIClass.config import calibrationPosition
from PyQt5 import QtGui
from MainUIClass.threads import octopiclient, ThreadFileUpload
import dialog

class calibrationPage:
    def __init__(self, MainUIObj):
        self.MainUIObj = MainUIObj

        if MainUIObj.idex:
            self.setNewToolZOffsetFromCurrentZBool = False


    def connect(self):
        self.MainUIObj.QtSocket.z_home_offset_signal.connect(self.getZHomeOffset)

        self.MainUIObj.calibrateBackButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.MenuPage))
        self.MainUIObj.nozzleOffsetButton.pressed.connect(self.nozzleOffset)
        # the -ve sign is such that its converted to home offset and not just distance between nozzle and bed
        self.MainUIObj.nozzleOffsetSetButton.pressed.connect(
            lambda: self.setZHomeOffset(self.MainUIObj.nozzleOffsetDoubleSpinBox.value(), True))
        self.MainUIObj.nozzleOffsetBackButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.calibratePage))
        # Bypass calibration wizzard page for not using Klipper
        # self.MainUIObj.calibrationWizardButton.clicked.connect(
        #     lambda: self.stackedWidget.setCurrentWidget(self.MainUIObj.calibrationWizardPage))
        self.MainUIObj.calibrationWizardButton.clicked.connect(self.quickStep1)

        self.MainUIObj.calibrationWizardBackButton.clicked.connect(
            lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.calibratePage))
        # required for Klipper
        # self.MainUIObj.quickCalibrationButton.clicked.connect(self.MainUIObj.quickStep6)
        # self.MainUIObj.fullCalibrationButton.clicked.connect(self.quickStep1)

        self.MainUIObj.quickStep1NextButton.clicked.connect(self.quickStep2)
        self.MainUIObj.quickStep2NextButton.clicked.connect(self.quickStep3)
        self.MainUIObj.quickStep3NextButton.clicked.connect(self.quickStep4)
        self.MainUIObj.quickStep4NextButton.clicked.connect(self.quickStep5)
        self.MainUIObj.quickStep5NextButton.clicked.connect(self.doneStep)
        # Required for Klipper
        # self.MainUIObj.quickStep5NextButton.clicked.connect(self.quickStep6)
        # self.MainUIObj.quickStep6NextButton.clicked.connect(self.doneStep)

        # self.MainUIObj.moveZPCalibrateButton.pressed.connect(lambda: octopiclient.jog(z=-0.05))
        # self.MainUIObj.moveZPCalibrateButton.pressed.connect(lambda: octopiclient.jog(z=0.05))
        self.MainUIObj.quickStep1CancelButton.pressed.connect(self.cancelStep)
        self.MainUIObj.quickStep2CancelButton.pressed.connect(self.cancelStep)
        self.MainUIObj.quickStep3CancelButton.pressed.connect(self.cancelStep)
        self.MainUIObj.quickStep4CancelButton.pressed.connect(self.cancelStep)
        self.MainUIObj.quickStep5CancelButton.pressed.connect(self.cancelStep)
        # self.MainUIObj.quickStep6CancelButton.pressed.connect(self.cancelStep)

    def getZHomeOffset(self, offset):
        '''
        Sets the spinbox value to have the value of the Z offset from the printer.
        the value is -ve so as to be more intuitive.
        :param offset:
        :return:
        '''
        self.MainUIObj.nozzleOffsetDoubleSpinBox.setValue(-float(offset))
        self.MainUIObj.nozzleHomeOffset = offset

    def setZHomeOffset(self, offset, setOffset=False):
        '''
        Sets the home offset after the calibration wizard is done, which is a callback to
        the response of M114 that is sent at the end of the Wizard in doneStep()
        :param offset: the value off the offset to set. is a str is coming from M114, and is float if coming from the nozzleOffsetPage
        :param setOffset: Boolean, is true if the function call is from the nozzleOffsetPage, else the current Z value sets the offset
        :return:

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''

        if self.MainUIObj.setHomeOffsetBool:
            octopiclient.gcode(command='M206 Z{}'.format(-float(offset)))
            self.MainUIObj.setHomeOffsetBool = False
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
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.nozzleOffsetPage)

    def quickStep1(self):
        '''
        Shows welcome message.
        Sets Z Home Offset = 0
        Homes to MAX
        goes to position where leveling screws can be opened
        :return:
        '''

        if self.MainUIObj.idex:
            self.toolZOffsetCaliberationPageCount = 0
            octopiclient.gcode(command='M104 S200')
            octopiclient.gcode(command='M104 T1 S200')
            #octopiclient.gcode(command='M211 S0')  # Disable software endstop
            octopiclient.gcode(command='T0')  # Set active tool to t0

        octopiclient.gcode(command='M503')
        octopiclient.gcode(command='M420 S0')
        if not self.MainUIObj.idex:
            octopiclient.gcode(command='M206 Z0')
        octopiclient.home(['x', 'y', 'z'])

        if self.MainUIObj.idex:
            octopiclient.gcode(command='T0')
            octopiclient.jog(x=40, y=40, absolute=True, speed=2000)
        else:
            octopiclient.jog(x=100, y=100, z=15, absolute=True, speed=1500)
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.quickStep1Page)

    def quickStep2(self):

        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.quickStep2Page)

        if self.MainUIObj.idex:
            '''
            levels first position (RIGHT)
            :return:
            '''
            self.stackedWidget.setCurrentWidget(self.quickStep2Page)
            octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=10000)
            octopiclient.jog(z=0, absolute=True, speed=1500)
        
        else:
            '''
            Askes user to release all Leveling Screws
            :return:
            '''
            self.MainUIObj.movie1 = QtGui.QMovie("templates/img/calibration/calib1.gif")
            self.MainUIObj.calib1.setMovie(self.MainUIObj.movie1)
            self.MainUIObj.movie1.start()

    def quickStep3(self):
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.quickStep3Page)

        if self.MainUIObj.idex:
            '''
            levels second leveling position (LEFT)
            '''
            octopiclient.jog(z=10, absolute=True, speed=1500)
            octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=10000)
            octopiclient.jog(z=0, absolute=True, speed=1500)

        else:
            '''
            leveks first position
            :return:
            '''
            octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=9000)
            octopiclient.jog(z=0, absolute=True, speed=1500)
            self.MainUIObj.movie1.stop()
            self.MainUIObj.movie2 = QtGui.QMovie("templates/img/calibration/calib2.gif")
            self.MainUIObj.calib2.setMovie(self.MainUIObj.movie2)
            self.MainUIObj.movie2.start()

    def quickStep4(self):
        
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.quickStep4Page)

        if self.MainUIObj.idex:
            '''
            levels third leveling position  (BACK)
            :return:
            '''
            # sent twice for some reason
            octopiclient.jog(z=10, absolute=True, speed=1500)
            octopiclient.jog(x=calibrationPosition['X3'], y=calibrationPosition['Y3'], absolute=True, speed=10000)
            octopiclient.jog(z=0, absolute=True, speed=1500)
        
        else:    
            '''
            levels second leveling position
            '''
            octopiclient.jog(z=10, absolute=True, speed=1500)
            octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=9000)
            octopiclient.jog(z=0, absolute=True, speed=1500)
            self.MainUIObj.movie2.stop()
            self.MainUIObj.movie3 = QtGui.QMovie("templates/img/calibration/calib3.gif")
            self.MainUIObj.calib3.setMovie(self.MainUIObj.movie3)
            self.MainUIObj.movie3.start()

    def quickStep5(self):
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.quickStep5Page)

        if self.MainUIObj.idex:
            '''
            Nozzle Z offset calc
            '''
            octopiclient.jog(z=15, absolute=True, speed=1500)
            octopiclient.gcode(command='M272 S')

        else:
            '''
            levels third leveling position
            :return:
            '''
            octopiclient.jog(z=10, absolute=True, speed=1500)
            octopiclient.jog(x=calibrationPosition['X3'], y=calibrationPosition['Y3'], absolute=True, speed=9000)
            octopiclient.jog(z=0, absolute=True, speed=1500)
            self.MainUIObj.movie3.stop()
            self.MainUIObj.movie4 = QtGui.QMovie("templates/img/calibration/calib4.gif")
            self.MainUIObj.calib4.setMovie(self.MainUIObj.movie4)
            self.MainUIObj.movie4.start()

    # def quickStep6(self):
    #     '''
    #     Performs Auto bed Leveiling, required for Klipper
    #     '''
    #     self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.quickStep6Page)
    #     octopiclient.gcode(command='M190 S70')
    #     octopiclient.gcode(command='G29')

    def doneStep(self):

        if self.MainUIObj.idex:
            '''
            Exits leveling
            :return:
            '''
            self.setNewToolZOffsetFromCurrentZBool = True
            octopiclient.gcode(command='M114')
            octopiclient.jog(z=4, absolute=True, speed=1500)
            octopiclient.gcode(command='T0')
            #octopiclient.gcode(command='M211 S1')  # Disable software endstop            octopiclient.home(['x', 'y', 'z'])
            octopiclient.gcode(command='M104 S0')
            octopiclient.gcode(command='M104 T1 S0')
            octopiclient.gcode(command='M84')
            octopiclient.gcode(command='M500')  # store eeprom settings to get Z home offset, mesh bed leveling back

        else:  
            '''
            decides weather to go to full calibration of return to calibration screen
            :return:
            '''
            self.MainUIObj.movie4.stop()
            octopiclient.gcode(command='M501')
            octopiclient.home(['x', 'y', 'z'])
        
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.calibratePage)


    def cancelStep(self):

        if self.MainUIObj.idex:
            octopiclient.home(['x', 'y', 'z'])
            octopiclient.gcode(command='M104 S0')
            octopiclient.gcode(command='M104 T1 S0')
            octopiclient.gcode(command='M84') 

        else:           
            octopiclient.gcode(command='M501')
            try:
                self.MainUIObj.movie1.stop()
                self.MainUIObj.movie2.stop()
                self.MainUIObj.movie3.stop()
                self.MainUIObj.movie4.stop()
            except:
                pass
        
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.calibratePage)


    def setZToolOffset(self, offset, setOffset=False):
        '''
        Sets the home offset after the caliberation wizard is done, which is a callback to
        the response of M114 that is sent at the end of the Wizard in doneStep()
        :param offset: the value off the offset to set. is a str is coming from M114, and is float if coming from the nozzleOffsetPage
        :param setOffset: Boolean, is true if the function call is from the nozzleOFfsetPage
        :return:

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''
        self.currentZPosition = offset #gets the current z position, used to set new tool offsets.
        # clean this shit up.
        #fuck you past vijay for not cleaning this up
        try:
            if self.setNewToolZOffsetFromCurrentZBool:
                print(self.toolOffsetZ)
                print(self.currentZPosition)
                newToolOffsetZ = (float(self.toolOffsetZ) + float(self.currentZPosition))
                octopiclient.gcode(command='M218 T1 Z{}'.format(newToolOffsetZ))  # restore eeprom settings to get Z home offset, mesh bed leveling back
                self.setNewToolZOffsetFromCurrentZBool =False
                octopiclient.gcode(command='SAVE_CONFIG')  # store eeprom settings to get Z home offset, mesh bed leveling back
        except Exception as e:
                    print("error: " + str(e))

    def showProbingFailed(self,msg='Probing Failed, Calibrate bed again or check for hardware issue',overlay=True):
        if dialog.WarningOk(self.MainUIObj, msg, overlay=overlay):
            octopiclient.cancelPrint()
            return True
        return False

    def showPrinterError(self,msg='Printer error, Check Terminal',overlay=False): #True
        if dialog.WarningOk(self.MainUIObj, msg, overlay=overlay):
            pass
            return True
        return False

    def updateEEPROMProbeOffset(self, offset):
        '''
        Sets the spinbox value to have the value of the Z offset from the printer.
        the value is -ve so as to be more intuitive.
        :param offset:
        :return:
        '''
        self.currentNozzleOffset.setText(str(float(offset)))
        self.MainUIObj.nozzleOffsetDoubleSpinBox.setValue(0)

    def setZProbeOffset(self, offset):
        '''
        Sets Z Probe offset from spinbox

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''

        octopiclient.gcode(command='M851 Z{}'.format(round(float(offset),2))) #M851 only ajusts nozzle offset
        self.MainUIObj.nozzleOffsetDoubleSpinBox.setValue(0)
        _offset=float(self.currentNozzleOffset.text())+float(offset)
        self.currentNozzleOffset.setText(str(float(self.currentNozzleOffset.text())-float(offset))) # show nozzle offset after adjustment
        octopiclient.gcode(command='M500')

    def requestEEPROMProbeOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        octopiclient.gcode(command='M503')
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.nozzleOffsetPage)

    def updateToolOffsetZ(self):
        octopiclient.gcode(command='M503')
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.toolOffsetZpage)

    def setToolOffsetX(self):
        octopiclient.gcode(command='M218 T1 X{}'.format(round(self.MainUIObj.toolOffsetXDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        octopiclient.gcode(command='M500')

    def setToolOffsetY(self):
        octopiclient.gcode(command='M218 T1 Y{}'.format(round(self.MainUIObj.toolOffsetYDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        octopiclient.gcode(command='M500')
        octopiclient.gcode(command='M500')

    def setToolOffsetZ(self):
        octopiclient.gcode(command='M218 T1 Z{}'.format(round(self.MainUIObj.toolOffsetZDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        octopiclient.gcode(command='M500')

    def getToolOffset(self, M218Data):

        #if float(M218Data[M218Data.index('X') + 1:].split(' ', 1)[0] ) > 0:
        self.toolOffsetZ = M218Data[M218Data.index('Z') + 1:].split(' ', 1)[0]
        self.toolOffsetX = M218Data[M218Data.index('X') + 1:].split(' ', 1)[0]
        self.toolOffsetY = M218Data[M218Data.index('Y') + 1:].split(' ', 1)[0]
        self.MainUIObj.toolOffsetXDoubleSpinBox.setValue(float(self.toolOffsetX))
        self.MainUIObj.toolOffsetYDoubleSpinBox.setValue(float(self.toolOffsetY))
        self.MainUIObj.toolOffsetZDoubleSpinBox.setValue(float(self.toolOffsetZ))
        self.idexToolOffsetRestoreValue = float(self.toolOffsetZ)

    def updateToolOffsetXY(self):
        octopiclient.gcode(command='M503')
        self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.toolOffsetXYPage)

    def testPrint(self,tool0Diameter,tool1Diameter,gcode):
        '''
        Prints a test print
        :param tool0Diameter: Diameter of tool 0 nozzle.04,06 or 08
        :param tool1Diameter: Diameter of tool 1 nozzle.40,06 or 08
        :param gcode: type of gcode to print, dual nozzle calibration, bed leveling, movement or samaple prints in
        single and dual. bedLevel, dualCalibration, movementTest, dualTest, singleTest
        :return:
        '''
        try:
            if gcode is 'bedLevel':
                self.printFromPath('gcode/' + tool0Diameter + '_BedLeveling.gcode', True)
            elif gcode is 'dualCalibration':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_dual_extruder_calibration_Idex.gcode',
                    True)
            elif gcode is 'movementTest':
                self.printFromPath('gcode/movementTest.gcode', True)
            elif gcode is 'dualTest':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_Fracktal_logo_Idex.gcode',
                    True)
            elif gcode is 'singleTest':
                self.printFromPath('gcode/' + tool0Diameter + '_Fracktal_logo_Idex.gcode',True)

            else:
                print("gcode not found")
        except Exception as e:
            print("Eror:" + e)

    def printFromPath(self,path,prnt=True):
        '''
        Transfers a file from a specific to octoprint's watched folder so that it gets automatically detected by Octoprint.
        Warning: If the file is read-only, octoprint API for reading the file crashes.
        '''

        self.MainUIObj.uploadThread = ThreadFileUpload(path, prnt=prnt)
        self.MainUIObj.uploadThread.start()
        if prnt:
            self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.homePage)
