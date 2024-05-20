from threads import octopiclient

def control_connections(self):
    self.controlButton.pressed.connect(self.control)
    self.menuControlButton.pressed.connect(self.control)

    self.cooldownButton.pressed.connect(self.coolDownAction)
    self.step100Button.pressed.connect(lambda: self.setStep(100))
    self.step1Button.pressed.connect(lambda: self.setStep(1))
    self.step10Button.pressed.connect(lambda: self.setStep(10))

def control(self):
    self.stackedWidget.setCurrentWidget(self.controlPage)
    self.toolTempSpinBox.setProperty("value", float(self.tool0TargetTemperature.text()))
    self.bedTempSpinBox.setProperty("value", float(self.bedTargetTemperature.text()))

def setStep(self, stepRate):
    '''
    Sets the class variable "Step" which would be needed for movement and joging
    :param step: step multiplier for movement in the move
    :return: nothing
    '''

    if stepRate == 100:
        self.step100Button.setFlat(True)
        self.step1Button.setFlat(False)
        self.step10Button.setFlat(False)
        self.step = 100
    if stepRate == 1:
        self.step100Button.setFlat(False)
        self.step1Button.setFlat(True)
        self.step10Button.setFlat(False)
        self.step = 1
    if stepRate == 10:
        self.step100Button.setFlat(False)
        self.step1Button.setFlat(False)
        self.step10Button.setFlat(True)
        self.step = 10

def coolDownAction(self):
    ''''
    Turns all heaters and fans off
    '''
    octopiclient.gcode(command='M107')
    octopiclient.setToolTemperature({"tool0": 0})
    # octopiclient.setToolTemperature({"tool0": 0})
    octopiclient.setBedTemperature(0)
    self.toolTempSpinBox.setProperty("value", 0)
    self.bedTempSpinBox.setProperty("value", 0)
