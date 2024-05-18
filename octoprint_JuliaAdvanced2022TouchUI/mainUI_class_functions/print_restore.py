import dialog
from octoprintAPI import octoprintAPI
from threads import octopiclient

def printRestoreMessageBox(self, file):
    '''
    Displays a message box alerting the user of a filament error
    '''
    if dialog.WarningYesNo(self, file + " Did not finish, would you like to restore?"):
        response = octopiclient.restore(restore=True)
        if response["status"] == "Successfully Restored":
            dialog.WarningOk(response["status"])
        else:
            dialog.WarningOk(response["status"])
    else:
        octoprintAPI.restore(restore=False)

def onServerConnected(self):
    self.isFilamentSensorInstalled()
    # if not self.__timelapse_enabled:
    #     return
    # if self.__timelapse_started:
    #     return
    try:
        response = octopiclient.isFailureDetected()
        if response["canRestore"] is True:
            self.printRestoreMessageBox(response["file"])
        else:
            self.firmwareUpdateCheck()
    except:
        print ("error on Server Connected")
        pass
