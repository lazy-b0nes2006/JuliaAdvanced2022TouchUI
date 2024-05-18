import requests
from PyQt5 import QtGui
from config import _fromUtf8, ip, apiKey
import dialog
from threads import octopiclient

def isFilamentSensorInstalled(self):
    success = False
    try:
        headers = {'X-Api-Key': apiKey}
        req = requests.get('http://{}/plugin/Julia2018FilamentSensor/status'.format(ip), headers=headers)
        success = req.status_code == requests.codes.ok
    except:
        pass
    self.toggleFilamentSensorButton.setEnabled(success)
    return success

def toggleFilamentSensor(self):
    headers = {'X-Api-Key': apiKey}
    # payload = {'sensor_enabled': self.toggleFilamentSensorButton.isChecked()}
    requests.get('http://{}/plugin/Julia2018FilamentSensor/toggle'.format(ip), headers=headers)   # , data=payload)

def filamentSensorHandler(self, data):
    sensor_enabled = False
    # print(data)

    if 'sensor_enabled' in data:
        sensor_enabled = data["sensor_enabled"] == 1

    icon = 'filamentSensorOn' if sensor_enabled else 'filamentSensorOff'
    self.toggleFilamentSensorButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon)))

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

    #Update
    if triggered_extruder0 and self.stackedWidget.currentWidget() not in [self.changeFilamentPage, self.changeFilamentProgressPage,
                                self.changeFilamentExtrudePage, self.changeFilamentRetractPage]:
        if dialog.WarningOk(self, "Filament outage in Extruder 0"):
            pass

    if triggered_door:
        if self.printerStatusText == "Printing":
            no_pause_pages = [self.controlPage, self.changeFilamentPage, self.changeFilamentProgressPage,
                                self.changeFilamentExtrudePage, self.changeFilamentRetractPage]
            if not pause_print or self.stackedWidget.currentWidget() in no_pause_pages:
                if dialog.WarningOk(self, "Door opened"):
                    return
            octopiclient.pausePrint()
            if dialog.WarningOk(self, "Door opened. Print paused.", overlay=True):
                return
        else:
            if dialog.WarningOk(self, "Door opened"):
                return
