from threads import octopiclient
from config import filaments

class changeFilamentRoutine:
    def __init__(self, obj):
        self.obj = obj
        obj.changeFilamentButton.pressed.connect(self.changeFilament)
        obj.changeFilamentBackButton.pressed.connect(obj.controlScreenInstance.control)
        obj.changeFilamentBackButton2.pressed.connect(self.changeFilamentCancel)
        obj.changeFilamentUnloadButton.pressed.connect(lambda: self.unloadFilament())
        obj.changeFilamentLoadButton.pressed.connect(lambda: self.loadFilament())
        obj.loadDoneButton.pressed.connect(obj.controlScreenInstance.control)
        obj.unloadDoneButton.pressed.connect(self.changeFilament)
        obj.retractFilamentButton.pressed.connect(lambda: octopiclient.extrude(-20))
        obj.ExtrudeButton.pressed.connect(lambda: octopiclient.extrude(20))

    def unloadFilament(self):
        # Update
        if self.obj.changeFilamentComboBox.findText("Loaded Filament") == -1:
            octopiclient.setToolTemperature(
                filaments[str(self.obj.changeFilamentComboBox.currentText())])
        self.obj.stackedWidget.setCurrentWidget(self.obj.changeFilamentProgressPage)
        self.obj.changeFilamentStatus.setText("Heating , Please Wait...")
        self.obj.changeFilamentNameOperation.setText("Unloading {}".format(str(self.obj.changeFilamentComboBox.currentText())))
        # This flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
        self.obj.changeFilamentHeatingFlag = True
        self.obj.loadFlag = False

    def loadFilament(self):
        # Update
        if self.obj.changeFilamentComboBox.findText("Loaded Filament") == -1:
            octopiclient.setToolTemperature(
                filaments[str(self.obj.changeFilamentComboBox.currentText())])
        self.obj.stackedWidget.setCurrentWidget(self.obj.changeFilamentProgressPage)
        self.obj.changeFilamentStatus.setText("Heating , Please Wait...")
        self.obj.changeFilamentNameOperation.setText("Loading {}".format(str(self.obj.changeFilamentComboBox.currentText())))
        # This flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
        self.obj.changeFilamentHeatingFlag = True
        self.obj.loadFlag = True

    def changeFilament(self):
        self.obj.stackedWidget.setCurrentWidget(self.obj.changeFilamentPage)
        self.obj.changeFilamentComboBox.clear()
        self.obj.changeFilamentComboBox.addItems(filaments.keys())
        # Update
        print(self.obj.tool0TargetTemperature)
        if self.obj.tool0TargetTemperature and self.obj.printerStatusText in ["Printing", "Paused"]:
            self.obj.changeFilamentComboBox.addItem("Loaded Filament")
            index = self.obj.changeFilamentComboBox.findText("Loaded Filament")
            if index >= 0:
                self.obj.changeFilamentComboBox.setCurrentIndex(index)

    def changeFilamentCancel(self):
        self.obj.changeFilamentHeatingFlag = False
        self.obj.coolDownAction()
        self.obj.controlScreenInstance.control()
