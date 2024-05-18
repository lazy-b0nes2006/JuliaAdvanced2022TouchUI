from threads import octopiclient
from config import filaments

def unloadFilament(self):
    #Update
    if self.changeFilamentComboBox.findText("Loaded Filament") == -1:
        octopiclient.setToolTemperature(
            filaments[str(self.changeFilamentComboBox.currentText())])
    self.stackedWidget.setCurrentWidget(self.changeFilamentProgressPage)
    self.changeFilamentStatus.setText("Heating , Please Wait...")
    self.changeFilamentNameOperation.setText("Unloading {}".format(str(self.changeFilamentComboBox.currentText())))
    # this flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
    self.changeFilamentHeatingFlag = True
    self.loadFlag = False

def loadFilament(self):
    #Update
    if self.changeFilamentComboBox.findText("Loaded Filament") == -1:
        octopiclient.setToolTemperature(
            filaments[str(self.changeFilamentComboBox.currentText())])
    self.stackedWidget.setCurrentWidget(self.changeFilamentProgressPage)
    self.changeFilamentStatus.setText("Heating , Please Wait...")
    self.changeFilamentNameOperation.setText("Loading {}".format(str(self.changeFilamentComboBox.currentText())))
    # this flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
    self.changeFilamentHeatingFlag = True
    self.loadFlag = True

def changeFilament(self):
    self.stackedWidget.setCurrentWidget(self.changeFilamentPage)
    self.changeFilamentComboBox.clear()
    self.changeFilamentComboBox.addItems(filaments.keys())
    #Update
    print(self.tool0TargetTemperature)
    if self.tool0TargetTemperature  and self.printerStatusText in ["Printing","Paused"]:
        self.changeFilamentComboBox.addItem("Loaded Filament")
        index = self.changeFilamentComboBox.findText("Loaded Filament")
        if index >= 0 :
            self.changeFilamentComboBox.setCurrentIndex(index)

def changeFilamentCancel(self):
    self.changeFilamentHeatingFlag = False
    self.coolDownAction()
    self.control()
