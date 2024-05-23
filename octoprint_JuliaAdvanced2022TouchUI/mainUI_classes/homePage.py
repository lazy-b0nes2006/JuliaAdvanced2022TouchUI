import dialog
import os
from threads import octopiclient


class homePage:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.stopButton.pressed.connect(self.stopActionMessageBox)
        self.obj.menuButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.MenuPage))
        self.obj.controlButton.pressed.connect(self.obj.controlScreenInstance.control)
        self.obj.playPauseButton.clicked.connect(self.playPauseAction)

    def tellAndReboot(self, msg="Rebooting...", overlay=True):
        if dialog.WarningOk(self.obj, msg, overlay=overlay):
            os.system('sudo reboot now')
            return True
        return False

    def askAndReboot(self, msg="Are you sure you want to reboot?", overlay=True):
        if dialog.WarningYesNo(self.obj, msg, overlay=overlay):
            os.system('sudo reboot now')
            return True
        return False

    def stopActionMessageBox(self):
        '''
        Displays a message box asking if the user is sure if he wants to turn off the print
        '''
        if dialog.WarningYesNo(self.obj, "Are you sure you want to stop the print?"):
            octopiclient.cancelPrint()

    def playPauseAction(self):
        '''
        Toggles Play/Pause of a print depending on the status of the print
        '''
        if self.obj.printerStatusText == "Operational":
            if self.obj.playPauseButton.isChecked:
                octopiclient.startPrint()
        elif self.obj.printerStatusText == "Printing":
            octopiclient.pausePrint()
        elif self.obj.printerStatusText == "Paused":
            octopiclient.resumePrint()
