import json
import os
from PyQt5 import QtCore

json_file_name = 'printer_name.json'
allowed_names = ["Julia Advanced", "Julia Extended", "Julia Pro Single Nozzle"]
   

class printerName:
    def __init__(self, MainUIObj):
        self.MainUIObj = MainUIObj

    def connect(self):
        self.MainUIObj.enterPrinterName.clicked.connect(self.enterPrinterName)

    def enterPrinterName(self):
        if self.MainUIObj.printerName:
            temp_printerName = self.MainUIObj.printerName
        else:
            temp_printerName = self.getPrinterName()
        if temp_printerName != self.MainUIObj.printerNameComboBox.currentText():
            self.setPrinterName(self.MainUIObj.printerNameComboBox.currentText())
            if not self.MainUIObj.homePageInstance.askAndReboot("Reboot to reflect changes?"):
                self.setPrinterName(temp_printerName)

    def getPrinterName(self):
        with open('printer_name.json', 'r') as file:
            data = json.load(file)
            return data['printer_name']
        
    def initialisePrinterNameJson(self):

        if not os.path.exists(json_file_name):
            print("fie not found")
            data = {
                'printer name': 'Julia Advanced'
            }

            with open(json_file_name, 'w') as file:
                json.dump(data, file, indent=4)
        
        else:
            with open(json_file_name, 'r') as file:
                data = json.load(file)

            if data.get('printer name') not in allowed_names:
                self.setPrinterName("Julia Advanced")

    def setPrinterName(self, name):
        data = {
            "printer name": name
        }
        with open(json_file_name, 'w') as file:
            json.dump(data, file, indent=4)

    def setPrinterNameComboBox(self):
        index = self.MainUIObj.printerNameComboBox.findText(self.getPrinterName(), QtCore.Qt.MatchFixedString)
        self.MainUIObj.printerNameComboBox.setCurrentIndex(index)