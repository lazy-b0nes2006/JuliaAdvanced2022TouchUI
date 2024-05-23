import dialog
import requests
from config import apiKey, _fromUtf8, ip
from PyQt5 import QtGui
from threads import octopiclient

class filamentSensor:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.toggleFilamentSensorButton.clicked.connect(self.toggleFilamentSensor)

    def isFilamentSensorInstalled(self):
        success = False
        try:
            headers = {'X-Api-Key': apiKey}
            req = requests.get('http://{}/plugin/Julia2018FilamentSensor/status'.format(ip), headers=headers)
            success = req.status_code == requests.codes.ok
        except:
            pass
        self.obj.toggleFilamentSensorButton.setEnabled(success)
        return success

    def toggleFilamentSensor(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/Julia2018FilamentSensor/toggle'.format(ip), headers=headers)

    def filamentSensorHandler(self, data):
        sensor_enabled = False

        if 'sensor_enabled' in data:
            sensor_enabled = data["sensor_enabled"] == 1

        icon = 'filamentSensorOn' if sensor_enabled else 'filamentSensorOff'
        self.obj.toggleFilamentSensorButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon)))

        if not sensor_enabled:
            return

        triggered_extruder0 = False
        triggered_door = False
        pause_print = False

        if 'filament' in data:
            triggered_extruder0 = data["filament"] == 0
        elif 'extruder0' in data:
            triggered_extruder0 = data["extruder0"] == 0

        if 'door' in data:
            triggered_door = data["door"] == 0
        if 'pause_print' in data:
            pause_print = data["pause_print"]

        if triggered_extruder0 and self.obj.stackedWidget.currentWidget() not in [self.obj.changeFilamentPage, self.obj.changeFilamentProgressPage,
                                  self.obj.changeFilamentExtrudePage, self.obj.changeFilamentRetractPage]:
            if dialog.WarningOk(self.obj, "Filament outage in Extruder 0"):
                pass

        if triggered_door:
            if self.obj.printerStatusText == "Printing":
                no_pause_pages = [self.obj.controlPage, self.obj.changeFilamentPage, self.obj.changeFilamentProgressPage,
                                  self.obj.changeFilamentExtrudePage, self.obj.changeFilamentRetractPage]
                if not pause_print or self.obj.stackedWidget.currentWidget() in no_pause_pages:
                    if dialog.WarningOk(self.obj, "Door opened"):
                        return
                octopiclient.pausePrint()
                if dialog.WarningOk(self.obj, "Door opened. Print paused.", overlay=True):
                    return
            else:
                if dialog.WarningOk(self.obj, "Door opened"):
                    return
