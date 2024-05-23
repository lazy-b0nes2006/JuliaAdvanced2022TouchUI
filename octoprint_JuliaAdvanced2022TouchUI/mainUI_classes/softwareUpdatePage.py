import dialog
import requests
from config import apiKey, ip
from PyQt5 import QtCore
from threads import octopiclient

class softwareUpdatePage:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.softwareUpdateBackButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.settingsPage))
        self.obj.performUpdateButton.pressed.connect(lambda: octopiclient.performSoftwareUpdate())

    ''' +++++++++++++++++++++++++++++++++OTA Update+++++++++++++++++++++++++++++++++++ '''

    def getFirmwareVersion(self):
        try:
            headers = {'X-Api-Key': apiKey}
            req = requests.get('http://{}/plugin/JuliaFirmwareUpdater/hardware/version'.format(ip), headers=headers)
            data = req.json()
            if req.status_code == requests.codes.ok:
                info = u'\u2713' if not data["update_available"] else u"\u2717"    # icon
                info += " Firmware: "
                info += "Unknown" if not data["variant_name"] else data["variant_name"]
                info += "\n"
                if data["variant_name"]:
                    info += "   Installed: "
                    info += "Unknown" if not data["version_board"] else data["version_board"]
                info += "\n"
                info += "" if not data["version_repo"] else "   Available: " + data["version_repo"]
                return info
        except:
            print("Error accessing /plugin/JuliaFirmwareUpdater/hardware/version")
            pass
        return u'\u2713' + "Firmware: Unknown\n"

    def displayVersionInfo(self):
        self.obj.updateListWidget.clear()
        updateAvailable = False
        self.obj.performUpdateButton.setDisabled(True)

        # Firmware version on the MKS https://github.com/FracktalWorks/OctoPrint-JuliaFirmwareUpdater
        self.obj.updateListWidget.addItem(self.getFirmwareVersion())

        data = octopiclient.getSoftwareUpdateInfo()
        if data:
            for item in data["information"]:
                plugin = data["information"][item]
                info = u'\u2713' if not plugin["updateAvailable"] else u'\u2717'
                info += plugin["displayName"] + "  " + plugin["displayVersion"] + "\n"
                info += "   Available: "
                if "information" in plugin and "remote" in plugin["information"] and plugin["information"]["remote"]["value"] is not None:
                    info += plugin["information"]["remote"]["value"]
                else:
                    info += "Unknown"
                self.obj.updateListWidget.addItem(info)

                if plugin["updateAvailable"]:
                    updateAvailable = True

                # if not updatable:
                #     self.obj.updateListWidget.addItem(u'\u2713' + data["information"][item]["displayName"] +
                #                                   "  " + data["information"][item]["displayVersion"] + "\n"
                #                                   + "   Available: " +
                #                                   )
                # else:
                #     updateAvailable = True
                #     self.obj.updateListWidget.addItem(u"\u2717" + data["information"][item]["displayName"] +
                #                                   "  " + data["information"][item]["displayVersion"] + "\n"
                #                                   + "   Available: " +
                #                                   data["information"][item]["information"]["remote"]["value"])

        if updateAvailable:
            self.obj.performUpdateButton.setDisabled(False)
        self.obj.stackedWidget.setCurrentWidget(self.obj.OTAUpdatePage)

    def softwareUpdateResult(self, data):
        messageText = ""
        for item in data:
            messageText += item + ": " + data[item][0] + ".\n"
        messageText += "Restart required"
        self.obj.homePageInstance.askAndReboot(messageText)

    def softwareUpdateProgress(self, data):
        self.obj.stackedWidget.setCurrentWidget(self.obj.softwareUpdateProgressPage)
        self.obj.logTextEdit.setTextColor(QtCore.Qt.red)
        self.obj.logTextEdit.append("---------------------------------------------------------------\n"
                                     "Updating " + data["name"] + " to " + data["version"] + "\n"
                                     "---------------------------------------------------------------")

    def softwareUpdateProgressLog(self, data):
        self.obj.logTextEdit.setTextColor(QtCore.Qt.white)
        for line in data:
            self.obj.logTextEdit.append(line["line"])

    def updateFailed(self, data):
        self.obj.stackedWidget.setCurrentWidget(self.obj.settingsPage)
        messageText = (data["name"] + " failed to update\n")
        if dialog.WarningOkCancel(self.obj, messageText, overlay=True):
            pass

    def softwareUpdate(self):
        data = octopiclient.getSoftwareUpdateInfo()
        updateAvailable = False
        if data:
            for item in data["information"]:
                if data["information"][item]["updateAvailable"]:
                    updateAvailable = True
        if updateAvailable:
            print('Update Available')
            if dialog.SuccessYesNo(self.obj, "Update Available! Update Now?", overlay=True):
                octopiclient.performSoftwareUpdate()
        else:
            if dialog.SuccessOk(self.obj, "System is Up To Date!", overlay=True):
                print('Update Unavailable')
