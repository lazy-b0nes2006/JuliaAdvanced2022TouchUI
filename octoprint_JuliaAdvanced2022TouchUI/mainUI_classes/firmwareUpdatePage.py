import dialog
from config import ip, apiKey
import requests


class firmwareUpdatePage:
    isFirmwareUpdateInProgress = False

    def __init__(self, obj):
        self.obj = obj
        obj.firmwareUpdateBackButton.pressed.connect(self.firmwareUpdateBack)

    def firmwareUpdateCheck(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/check'.format(ip), headers=headers)

    def firmwareUpdateStart(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/start'.format(ip), headers=headers)

    def firmwareUpdateStartProgress(self):
        self.obj.stackedWidget.setCurrentWidget(self.obj.firmwareUpdateProgressPage)
        self.obj.firmwareUpdateLog.setText("<span style='color: cyan'>Julia Firmware Updater<span>")
        self.obj.firmwareUpdateLog.append("<span style='color: cyan'>---------------------------------------------------------------</span>")
        self.obj.firmwareUpdateBackButton.setEnabled(False)

    def firmwareUpdateProgress(self, text, backEnabled=False):
        self.obj.stackedWidget.setCurrentWidget(self.obj.firmwareUpdateProgressPage)
        self.obj.firmwareUpdateLog.append(str(text))
        self.obj.firmwareUpdateBackButton.setEnabled(backEnabled)

    def firmwareUpdateBack(self):
        self.isFirmwareUpdateInProgress = False
        self.obj.firmwareUpdateBackButton.setEnabled(False)
        self.obj.stackedWidget.setCurrentWidget(self.obj.homePage)

    def firmwareUpdateHandler(self, data):
        if "type" not in data or data["type"] != "status":
            return

        if "status" not in data:
            return

        status = data["status"]
        subtype = data["subtype"] if "subtype" in data else None

        if status == "update_check":    # update check
            if subtype == "error":  # notify error in ok dialog
                self.isFirmwareUpdateInProgress = False
                if "message" in data:
                    dialog.WarningOk(self.obj, "Firmware Updater Error: " + str(data["message"]), overlay=True)
            elif subtype == "success":
                if dialog.SuccessYesNo(self.obj, "Firmware update found.\nPress yes to update now!", overlay=True):
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
                if "message" in data:
                    dialog.WarningOk(self.obj, "Firmware Updater Error: " + str(data["message"]), overlay=True)
        elif status == "flasherror" or status == "progress":    # show software update dialog and update textview
            if "message" in data:
                message = "<span style='color: {}'>{}</span>".format("teal" if status == "progress" else "red", data["message"])
                self.firmwareUpdateProgress(message, backEnabled=(status == "flasherror"))
        elif status == "success":    # show ok dialog to show done
            self.isFirmwareUpdateInProgress = False
            message = data["message"] if "message" in data else "Flash successful!"
            message = "<span style='color: green'>{}</span>".format(message)
            message = message + "<br/><br/><span style='color: white'>Press back to continue...</span>"
            self.firmwareUpdateProgress(message, backEnabled=True)
