from MainUIClass.threads import octopiclient
from MainUIClass.config import calibrationPosition

class idexConfig:

    def __init__(self, MainUIObj):
        self.MainUIObj = MainUIObj

    def connect(self):
        self.MainUIObj.idexCalibrationWizardButton.clicked.connect(self.idexConfigStep1)
        self.MainUIObj.idexConfigStep1NextButton.clicked.connect(self.idexConfigStep2)
        self.MainUIObj.idexConfigStep2NextButton.clicked.connect(self.idexConfigStep3)
        self.MainUIObj.idexConfigStep3NextButton.clicked.connect(self.idexConfigStep4)
        self.MainUIObj.idexConfigStep4NextButton.clicked.connect(self.idexConfigStep5)
        self.MainUIObj.idexConfigStep5NextButton.clicked.connect(self.idexDoneStep)
        self.MainUIObj.idexConfigStep1CancelButton.pressed.connect(self.idexCancelStep)
        self.MainUIObj.idexConfigStep2CancelButton.pressed.connect(self.idexCancelStep)
        self.MainUIObj.idexConfigStep3CancelButton.pressed.connect(self.idexCancelStep)
        self.MainUIObj.idexConfigStep4CancelButton.pressed.connect(self.idexCancelStep)
        self.MainUIObj.idexConfigStep5CancelButton.pressed.connect(self.idexCancelStep)
        self.MainUIObj.moveZMIdexButton.pressed.connect(lambda: octopiclient.jog(z=-0.1))
        self.MainUIObj.moveZPIdexButton.pressed.connect(lambda: octopiclient.jog(z=0.1))
        
        self.MainUIObj.toolOffsetXSetButton.pressed.connect(self.MainUIObj.calibrationPageInstance.setToolOffsetX)
        self.MainUIObj.toolOffsetYSetButton.pressed.connect(self.MainUIObj.calibrationPageInstance.setToolOffsetY)
        self.MainUIObj.toolOffsetZSetButton.pressed.connect(self.MainUIObj.calibrationPageInstance.setToolOffsetZ)
        self.MainUIObj.toolOffsetXYBackButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.calibratePage))
        self.MainUIObj.toolOffsetZBackButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.calibratePage))
        self.MainUIObj.toolOffsetXYButton.pressed.connect(self.MainUIObj.calibrationPageInstance.updateToolOffsetXY)
        self.MainUIObj.toolOffsetZButton.pressed.connect(self.MainUIObj.calibrationPageInstance.updateToolOffsetZ)

        self.MainUIObj.testPrintsButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.testPrintsPage1_6))
        self.MainUIObj.testPrintsNextButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.testPrintsPage2_6))
        self.MainUIObj.testPrintsBackButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.calibratePage))
        self.MainUIObj.testPrintsCancelButton.pressed.connect(lambda: self.MainUIObj.stackedWidget.setCurrentWidget(self.MainUIObj.calibratePage))
        self.MainUIObj.dualCaliberationPrintButton.pressed.connect(
            lambda: self.MainUIObj.calibrationPageInstance.testPrint(str(self.MainUIObj.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.MainUIObj.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'dualCalibration'))
        self.MainUIObj.bedLevelPrintButton.pressed.connect(
            lambda: self.MainUIObj.calibrationPageInstance.testPrint(str(self.MainUIObj.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.MainUIObj.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'bedLevel'))
        self.MainUIObj.movementTestPrintButton.pressed.connect(
            lambda: self.MainUIObj.calibrationPageInstance.testPrint(str(self.MainUIObj.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.MainUIObj.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'movementTest'))
        self.MainUIObj.singleNozzlePrintButton.pressed.connect(
            lambda: self.MainUIObj.calibrationPageInstance.testPrint(str(self.MainUIObj.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.MainUIObj.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'dualTest'))
        self.MainUIObj.dualNozzlePrintButton.pressed.connect(
            lambda: self.MainUIObj.calibrationPageInstance.testPrint(str(self.MainUIObj.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.MainUIObj.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'singleTest'))


    def idexConfigStep1(self):
        '''
        Shows welcome message.
        Welcome Page, Give Info. Unlock nozzle and push down
        :return:
        '''
        octopiclient.gcode(command='M503')  # Gets old tool offset position
        octopiclient.gcode(command='M218 T1 Z0')  # set nozzle tool offsets to 0
        octopiclient.gcode(command='M104 S200')
        octopiclient.gcode(command='M104 T1 S200')
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.gcode(command='G1 X10 Y10 Z20 F5000')
        octopiclient.gcode(command='T0')  # Set active tool to t0
        octopiclient.gcode(command='M420 S0')  # Dissable mesh bed leveling for good measure
        self.stackedWidget.setCurrentWidget(self.MainUIObj.idexConfigStep1Page)

    def idexConfigStep2(self):
        '''
        levels first position (RIGHT)
        :return:
        '''
        self.stackedWidget.setCurrentWidget(self.idexConfigStep2Page)
        octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    def idexConfigStep3(self):
        '''
        levels second leveling position (LEFT)
        '''
        self.stackedWidget.setCurrentWidget(self.idexConfigStep3Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    def idexConfigStep4(self):
        '''
        Set to Mirror mode and asks to loosen the carriage, push both doen to max
        :return:
        '''
        # sent twice for some reason
        self.stackedWidget.setCurrentWidget(self.idexConfigStep4Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.gcode(command='M605 S3')
        octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=10000)

    def idexConfigStep5(self):
        '''
        take bed up until both nozzles touch the bed. ASk to take nozzle up and down till nozzle just rests on the bed and tighten
        :return:
        '''
        # sent twice for some reason
        self.stackedWidget.setCurrentWidget(self.idexConfigStep5Page)
        octopiclient.jog(z=1, absolute=True, speed=10000)


    def idexDoneStep(self):
        '''
        Exits leveling
        :return:
        '''
        octopiclient.jog(z=4, absolute=True, speed=1500)
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        octopiclient.home(['z'])
        octopiclient.home(['x', 'y'])
        octopiclient.gcode(command='M104 S0')
        octopiclient.gcode(command='M104 T1 S0')
        octopiclient.gcode(command='M605 S1')
        octopiclient.gcode(command='M218 T1 Z0') #set nozzle offsets to 0
        octopiclient.gcode(command='M84')
        octopiclient.gcode(command='M500')  # store eeprom settings to get Z home offset, mesh bed leveling back

    def idexCancelStep(self):
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        octopiclient.gcode(command='M605 S1')
        octopiclient.home(['z'])
        octopiclient.home(['x', 'y'])
        octopiclient.gcode(command='M104 S0')
        octopiclient.gcode(command='M104 T1 S0')
        octopiclient.gcode(command='M218 T1 Z{}'.format(self.idexToolOffsetRestoreValue))
        octopiclient.gcode(command='M84')
    