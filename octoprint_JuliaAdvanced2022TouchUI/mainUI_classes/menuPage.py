class menuPage:
    def __init__(self, obj):
        obj.menuBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.homePage))
        obj.menuControlButton.pressed.connect(obj.controlScreenInstance.control)
        obj.menuPrintButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.printLocationPage))
        obj.menuCalibrateButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.calibratePage))
        obj.menuSettingsButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.settingsPage))
