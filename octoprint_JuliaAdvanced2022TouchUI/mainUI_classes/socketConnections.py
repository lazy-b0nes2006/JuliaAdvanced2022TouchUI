from threads import octopiclient
import styles
import dialog
from PyQt5 import QtGui, QtCore
from config import _fromUtf8

class socketConnections:
    def __init__(self, obj):
        self.obj = obj
        obj.QtSocket.z_home_offset_signal.connect(self.getZHomeOffset)
        obj.QtSocket.temperatures_signal.connect(self.updateTemperature)
        obj.QtSocket.status_signal.connect(self.updateStatus)
        obj.QtSocket.print_status_signal.connect(self.updatePrintStatus)
        obj.QtSocket.update_started_signal.connect(self.softwareUpdateProgress)
        obj.QtSocket.update_log_signal.connect(self.softwareUpdateProgressLog)
        obj.QtSocket.update_log_result_signal.connect(self.softwareUpdateResult)
        obj.QtSocket.update_failed_signal.connect(self.updateFailed)
        obj.QtSocket.connected_signal.connect(self.onServerConnected)
        obj.QtSocket.filament_sensor_triggered_signal.connect(self.filamentSensorHandler)
        obj.QtSocket.firmware_updater_signal.connect(self.firmwareUpdateHandler)

    def getZHomeOffset(self, offset):
        self.obj.calibrationPageInstance.getZHomeOffset(offset)

    def updateTemperature(self, temperature):
        self.obj.printerStatusInstance.updateTemperature(temperature)
        
    def updatePrintStatus(self, file):
        self.obj.printerStatusInstance.updatePrintStatus(file)
        
    def updateStatus(self, status):
        self.obj.printerStatusInstance.updateStatus(status)

    def softwareUpdateResult(self, data):
        self.obj.softwareUpdatesInstance.softwareUpdateResult(data)

    def softwareUpdateProgress(self, data):
        self.obj.softwareUpdatesInstance.softwareUpdateProgress(data)

    def softwareUpdateProgressLog(self, data):
        self.obj.softwareUpdatesInstance.softwareUpdateProgressLog(data)

    def updateFailed(self, data):
        self.obj.softwareUpdatesInstance.UpdateFailed(data)

    def onServerConnected(self):
        self.obj.printLocationScreenInstance.onServerConnected()

    def firmwareUpdateHandler(self, data):
        self.obj.firmwareUpdatePageInstance.firmwareUpdateHandler(data)

    def filamentSensorHandler(self, data):
        self.obj.filamentSensorInstance.filamentSensorHandler(data)
        
