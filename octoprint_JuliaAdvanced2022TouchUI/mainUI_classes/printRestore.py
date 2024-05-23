from threads import octopiclient
from octoprintAPI import octoprintAPI
import dialog
from mainUI_classes.filamentSensor import filamentSensor

class printRestore:
    def __init__(self, obj):
        self.obj = obj
    
    def printRestoreMessageBox(self, file):
        '''
        Displays a message box alerting the user of a filament error
        '''
        if dialog.WarningYesNo(self.obj, file + " Did not finish, would you like to restore?"):
            response = octopiclient.restore(restore=True)
            if response["status"] == "Successfully Restored":
                dialog.WarningOk(response["status"])
            else:
                dialog.WarningOk(response["status"])
        else:
            octoprintAPI.restore(restore=False)

    def onServerConnected(self):
        self.obj.filamentSensorInstance.isFilamentSensorInstalled()
        # if not self.__timelapse_enabled:
        #     return
        # if self.__timelapse_started:
        #     return
        try:
            response = octopiclient.isFailureDetected()
            if response["canRestore"] is True:
                self.printRestoreMessageBox(response["file"])
            else:
                self.obj.firmwareUpdatePageInstance.firmwareUpdateCheck()
        except:
            print ("error on Server Connected")
            pass