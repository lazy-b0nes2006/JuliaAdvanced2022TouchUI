class printLocationScreen:
    def __init__(self, obj):
        obj.printLocationScreenBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.MenuPage))
        obj.fromLocalButton.pressed.connect(obj.getFilesAndInfoInstance.fileListLocal)
        obj.fromUsbButton.pressed.connect(obj.getFilesAndInfoInstance.fileListUSB)

