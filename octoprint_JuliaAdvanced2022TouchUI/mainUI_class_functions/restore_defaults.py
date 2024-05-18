import dialog
from threads import octopiclient
import os

def restoreFactoryDefaults(self):
    if dialog.WarningYesNo(self, "Are you sure you want to restore machine state to factory defaults?\nWarning: Doing so will also reset printer profiles, WiFi & Ethernet config.",
                            overlay=True):
        os.system('sudo cp -f config/dhcpcd.conf /etc/dhcpcd.conf')
        os.system('sudo cp -f config/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
        os.system('sudo rm -rf /home/pi/.octoprint/users.yaml')
        os.system('sudo cp -f config/users.yaml /home/pi/.octoprint/users.yaml')
        os.system('sudo rm -rf /home/pi/.octoprint/printerProfiles/*')
        os.system('sudo rm -rf /home/pi/.octoprint/scripts/gcode')
        os.system('sudo rm -rf /home/pi/.octoprint/print_restore.json')
        os.system('sudo cp -f config/config.yaml /home/pi/.octoprint/config.yaml')
        # os.system('sudo rm -rf /home/pi/.fw_logo.dat')
        self.tellAndReboot("Settings restored. Rebooting...")

def restorePrintDefaults(self):
    if dialog.WarningYesNo(self, "Are you sure you want to restore default print settings?\nWarning: Doing so will erase offsets and bed leveling info",
                            overlay=True):
        octopiclient.gcode(command='M502')
        octopiclient.gcode(command='M500')
