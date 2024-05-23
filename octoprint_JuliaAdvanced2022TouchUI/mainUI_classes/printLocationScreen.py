class printLocationScreen:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.printLocationScreenBackButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.MenuPage))
        self.obj.fromLocalButton.pressed.connect(self.obj.getFilesAndInfoInstance.fileListLocal)
        self.obj.fromUsbButton.pressed.connect(self.obj.getFilesAndInfoInstance.fileListUSB)
