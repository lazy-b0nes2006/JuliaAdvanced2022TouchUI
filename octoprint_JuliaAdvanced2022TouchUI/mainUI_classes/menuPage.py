class menuPage:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.menuBackButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.homePage))
        self.obj.menuControlButton.pressed.connect(self.obj.controlScreenInstance.control)
        self.obj.menuPrintButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.printLocationPage))
        self.obj.menuCalibrateButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.calibratePage))
        self.obj.menuSettingsButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.settingsPage))
