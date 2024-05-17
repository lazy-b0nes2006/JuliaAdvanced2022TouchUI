import requests
from config import apiKey, ip
import dialog
from threads import octopiclient
from PyQt5 import QtCore

isFirmwareUpdateInProgress = False

def firmwareUpdateCheck(self):
    headers = {'X-Api-Key': apiKey}
    requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/check'.format(ip), headers=headers)

def firmwareUpdateStart(self):
    headers = {'X-Api-Key': apiKey}
    requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/start'.format(ip), headers=headers)

def firmwareUpdateStartProgress(self):
    self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
    # self.firmwareUpdateLog.setTextColor(QtCore.Qt.yellow)
    self.firmwareUpdateLog.setText("<span style='color: cyan'>Julia Firmware Updater<span>")
    self.firmwareUpdateLog.append("<span style='color: cyan'>---------------------------------------------------------------</span>")
    self.firmwareUpdateBackButton.setEnabled(False)

def firmwareUpdateProgress(self, text, backEnabled=False):
    self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
    # self.firmwareUpdateLog.setTextColor(QtCore.Qt.yellow)
    self.firmwareUpdateLog.append(str(text))
    self.firmwareUpdateBackButton.setEnabled(backEnabled)

def firmwareUpdateBack(self):
    self.isFirmwareUpdateInProgress = False
    self.firmwareUpdateBackButton.setEnabled(False)
    self.stackedWidget.setCurrentWidget(self.homePage)

def firmwareUpdateHandler(self, data):
    if "type" not in data or data["type"] != "status":
        return

    if "status" not in data:
        return

    status = data["status"]
    subtype = data["subtype"] if "subtype" in data else None

    if status == "update_check":    # update check
        if subtype == "error":  # notify error in ok diag
            self.isFirmwareUpdateInProgress = False
            if "message" in data:
                dialog.WarningOk(self, "Firmware Updater Error: " + str(data["message"]), overlay=True)
        elif subtype == "success":
            if dialog.SuccessYesNo(self, "Firmware update found.\nPress yes to update now!", overlay=True):
                self.isFirmwareUpdateInProgress = True
                self.firmwareUpdateStart()
    elif status == "update_start":  # update started
        if subtype == "success":    # update progress
            self.isFirmwareUpdateInProgress = True
            self.firmwareUpdateStartProgress()
            if "message" in data:
                message = "<span style='color: yellow'>{}</span>".format(data["message"])
                self.firmwareUpdateProgress(message)
        else:   # show error
            self.isFirmwareUpdateInProgress = False
            # self.firmwareUpdateProgress(data["message"] if "message" in data else "Unknown error!", backEnabled=True)
            if "message" in data:
                dialog.WarningOk(self, "Firmware Updater Error: " + str(data["message"]), overlay=True)
    elif status == "flasherror" or status == "progress":    # show software update dialog and update textview
        if "message" in data:
            message = "<span style='color: {}'>{}</span>".format("teal" if status == "progress" else "red", data["message"])
            self.firmwareUpdateProgress(message, backEnabled=(status == "flasherror"))
    elif status == "success":    # show ok diag to show done
        self.isFirmwareUpdateInProgress = False
        message = data["message"] if "message" in data else "Flash successful!"
        message = "<span style='color: green'>{}</span>".format(message)
        message = message + "<br/><br/><span style='color: white'>Press back to continue...</span>"
        self.firmwareUpdateProgress(message, backEnabled=True)

''' +++++++++++++++++++++++++++++++++OTA Update+++++++++++++++++++++++++++++++++++ '''

def getFirmwareVersion(self):
    try:
        headers = {'X-Api-Key': apiKey}
        req = requests.get('http://{}/plugin/JuliaFirmwareUpdater/hardware/version'.format(ip), headers=headers)
        data = req.json()
        # print(data)
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
    self.updateListWidget.clear()
    updateAvailable = False
    self.performUpdateButton.setDisabled(True)

    # Firmware version on the MKS https://github.com/FracktalWorks/OctoPrint-JuliaFirmwareUpdater
    # self.updateListWidget.addItem(self.getFirmwareVersion())

    data = octopiclient.getSoftwareUpdateInfo()
    if data:
        for item in data["information"]:
            # print(item)
            plugin = data["information"][item]
            info = u'\u2713' if not plugin["updateAvailable"] else u"\u2717"    # icon
            info += plugin["displayName"] + "  " + plugin["displayVersion"] + "\n"
            info += "   Available: "
            if "information" in plugin and "remote" in plugin["information"] and plugin["information"]["remote"]["value"] is not None:
                info += plugin["information"]["remote"]["value"]
            else:
                info += "Unknown"
            self.updateListWidget.addItem(info)

            if plugin["updateAvailable"]:
                updateAvailable = True

            # if not updatable:
            #     self.updateListWidget.addItem(u'\u2713' + data["information"][item]["displayName"] +
            #                                   "  " + data["information"][item]["displayVersion"] + "\n"
            #                                   + "   Available: " +
            #                                   )
            # else:
            #     updateAvailable = True
            #     self.updateListWidget.addItem(u"\u2717" + data["information"][item]["displayName"] +
            #                                   "  " + data["information"][item]["displayVersion"] + "\n"
            #                                   + "   Available: " +
            #                                   data["information"][item]["information"]["remote"]["value"])
    if updateAvailable:
        self.performUpdateButton.setDisabled(False)
    self.stackedWidget.setCurrentWidget(self.OTAUpdatePage)

def softwareUpdateResult(self, data):
    messageText = ""
    for item in data:
        messageText += item + ": " + data[item][0] + ".\n"
    messageText += "Restart required"
    self.askAndReboot(messageText)

def softwareUpdateProgress(self, data):
    self.stackedWidget.setCurrentWidget(self.softwareUpdateProgressPage)
    self.logTextEdit.setTextColor(QtCore.Qt.red)
    self.logTextEdit.append("---------------------------------------------------------------\n"
                            "Updating " + data["name"] + " to " + data["version"] + "\n"
                                                                                    "---------------------------------------------------------------")

def softwareUpdateProgressLog(self, data):
    self.logTextEdit.setTextColor(QtCore.Qt.white)
    for line in data:
        self.logTextEdit.append(line["line"])

def updateFailed(self, data):
    self.stackedWidget.setCurrentWidget(self.settingsPage)
    messageText = (data["name"] + " failed to update\n")
    if dialog.WarningOkCancel(self, messageText, overlay=True):
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
        if dialog.SuccessYesNo(self, "Update Available! Update Now?", overlay=True):
            octopiclient.performSoftwareUpdate()

    else:
        if dialog.SuccessOk(self, "System is Up To Date!", overlay=True):
            print('Update Unavailable')
