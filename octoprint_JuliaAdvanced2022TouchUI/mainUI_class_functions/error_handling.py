import dialog
import os

def handleStartupError(self):
    print('Shutting Down. Unable to connect')
    if dialog.WarningOk(self, "Error. Contact Support. Shutting down...", overlay=True):
        os.system('sudo shutdown now')
