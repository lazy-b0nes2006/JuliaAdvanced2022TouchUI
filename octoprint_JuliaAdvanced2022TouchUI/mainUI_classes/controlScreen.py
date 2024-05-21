from threads import octopiclient
import dialog
import os

class controlScreen:
    def __init__(self, obj):
        self.obj = obj
        
    def initialise(self, obj):
        obj.moveYPButton.pressed.connect(lambda: octopiclient.jog(y=self.step, speed=1000))
        obj.moveYMButton.pressed.connect(lambda: octopiclient.jog(y=-self.step, speed=1000))
        obj.moveXMButton.pressed.connect(lambda: octopiclient.jog(x=-self.step, speed=1000))
        obj.moveXPButton.pressed.connect(lambda: octopiclient.jog(x=self.step, speed=1000))
        obj.moveZPButton.pressed.connect(lambda: octopiclient.jog(z=self.step, speed=1000))
        obj.moveZMButton.pressed.connect(lambda: octopiclient.jog(z=-self.step, speed=1000))
        obj.extruderButton.pressed.connect(lambda: octopiclient.extrude(self.step))
        obj.retractButton.pressed.connect(lambda: octopiclient.extrude(-self.step))
        obj.motorOffButton.pressed.connect(lambda: octopiclient.gcode(command='M18'))
        obj.fanOnButton.pressed.connect(lambda: octopiclient.gcode(command='M106'))
        obj.fanOffButton.pressed.connect(lambda: octopiclient.gcode(command='M107'))
        obj.cooldownButton.pressed.connect(self.coolDownAction)
        obj.step100Button.pressed.connect(lambda: self.setStep(100))
        obj.step1Button.pressed.connect(lambda: self.setStep(1))
        obj.step10Button.pressed.connect(lambda: self.setStep(10))
        obj.homeXYButton.pressed.connect(lambda: octopiclient.home(['x', 'y']))
        obj.homeZButton.pressed.connect(lambda: octopiclient.home(['z']))
        obj.controlBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.homePage))
        obj.setToolTempButton.pressed.connect(lambda: octopiclient.setToolTemperature(
            obj.toolTempSpinBox.value()))
        obj.setBedTempButton.pressed.connect(lambda: octopiclient.setBedTemperature(obj.bedTempSpinBox.value()))

        obj.setFlowRateButton.pressed.connect(lambda: octopiclient.flowrate(obj.flowRateSpinBox.value()))
        obj.setFeedRateButton.pressed.connect(lambda: octopiclient.feedrate(obj.feedRateSpinBox.value()))

        # obj.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='SET_GCODE_OFFSET Z_ADJUST=0.025 MOVE=1'))
        # obj.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='SET_GCODE_OFFSET Z_ADJUST=-0.025 MOVE=1'))
        obj.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z0.025'))
        obj.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z-0.025'))

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
