from threads import octopiclient
import dialog
import os

class controlScreen:
    def __init__(self, obj):
        self.obj = obj
        
    def connect(self):
        self.obj.moveYPButton.pressed.connect(lambda: octopiclient.jog(y=self.step, speed=1000))
        self.obj.moveYMButton.pressed.connect(lambda: octopiclient.jog(y=-self.step, speed=1000))
        self.obj.moveXMButton.pressed.connect(lambda: octopiclient.jog(x=-self.step, speed=1000))
        self.obj.moveXPButton.pressed.connect(lambda: octopiclient.jog(x=self.step, speed=1000))
        self.obj.moveZPButton.pressed.connect(lambda: octopiclient.jog(z=self.step, speed=1000))
        self.obj.moveZMButton.pressed.connect(lambda: octopiclient.jog(z=-self.step, speed=1000))
        self.obj.extruderButton.pressed.connect(lambda: octopiclient.extrude(self.step))
        self.obj.retractButton.pressed.connect(lambda: octopiclient.extrude(-self.step))
        self.obj.motorOffButton.pressed.connect(lambda: octopiclient.gcode(command='M18'))
        self.obj.fanOnButton.pressed.connect(lambda: octopiclient.gcode(command='M106'))
        self.obj.fanOffButton.pressed.connect(lambda: octopiclient.gcode(command='M107'))
        self.obj.cooldownButton.pressed.connect(self.coolDownAction)
        self.obj.step100Button.pressed.connect(lambda: self.setStep(100))
        self.obj.step1Button.pressed.connect(lambda: self.setStep(1))
        self.obj.step10Button.pressed.connect(lambda: self.setStep(10))
        self.obj.homeXYButton.pressed.connect(lambda: octopiclient.home(['x', 'y']))
        self.obj.homeZButton.pressed.connect(lambda: octopiclient.home(['z']))
        self.obj.controlBackButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.homePage))
        self.obj.setToolTempButton.pressed.connect(lambda: octopiclient.setToolTemperature(
            self.obj.toolTempSpinBox.value()))
        self.obj.setBedTempButton.pressed.connect(lambda: octopiclient.setBedTemperature(self.obj.bedTempSpinBox.value()))

        self.obj.setFlowRateButton.pressed.connect(lambda: octopiclient.flowrate(self.obj.flowRateSpinBox.value()))
        self.obj.setFeedRateButton.pressed.connect(lambda: octopiclient.feedrate(self.obj.feedRateSpinBox.value()))

        # self.obj.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='SET_GCODE_OFFSET Z_ADJUST=0.025 MOVE=1'))
        # self.obj.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='SET_GCODE_OFFSET Z_ADJUST=-0.025 MOVE=1'))
        self.obj.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z0.025'))
        self.obj.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z-0.025'))

    def control(self):
        self.obj.stackedWidget.setCurrentWidget(self.obj.controlPage)
        self.obj.toolTempSpinBox.setProperty("value", float(self.obj.tool0TargetTemperature.text()))
        self.obj.bedTempSpinBox.setProperty("value", float(self.obj.bedTargetTemperature.text()))

    def setStep(self, stepRate):
        '''
        Sets the class variable "Step" which would be needed for movement and jogging
        :param stepRate: step multiplier for movement in the move
        :return: nothing
        '''
        
        if stepRate == 100:
            self.obj.step100Button.setFlat(True)
            self.obj.step1Button.setFlat(False)
            self.obj.step10Button.setFlat(False)
            self.step = 100
        if stepRate == 1:
            self.obj.step100Button.setFlat(False)
            self.obj.step1Button.setFlat(True)
            self.obj.step10Button.setFlat(False)
            self.step = 1
        if stepRate == 10:
            self.obj.step100Button.setFlat(False)
            self.obj.step1Button.setFlat(False)
            self.obj.step10Button.setFlat(True)
            self.step = 10

    def coolDownAction(self):
        '''
        Turns all heaters and fans off
        '''
        octopiclient.gcode(command='M107')
        octopiclient.setToolTemperature({"tool0": 0})
        octopiclient.setBedTemperature(0)
        self.obj.toolTempSpinBox.setProperty("value", 0)
        self.obj.bedTempSpinBox.setProperty("value", 0)

    def handleStartupError(self):
        print('Shutting Down. Unable to connect')
        if dialog.WarningOk(self, "Error. Contact Support. Shutting down...", overlay=True):
            os.system('sudo shutdown now')
