from network_utils import getIP
import qrcode
from threads import ThreadRestartNetworking, octopiclient
from gui_elements import Image
import dialog
import os

class settingsPage:
    def __init__(self, obj):
        self.obj = obj
        obj.networkSettingsButton.pressed.connect(
            lambda: obj.stackedWidget.setCurrentWidget(obj.networkSettingsPage))
        obj.displaySettingsButton.pressed.connect(
            lambda: obj.stackedWidget.setCurrentWidget(obj.displaySettingsPage))
        obj.settingsBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.MenuPage))
        obj.pairPhoneButton.pressed.connect(self.pairPhoneApp)
        obj.OTAButton.pressed.connect(obj.softwareUpdatePageInstance.softwareUpdate)
        obj.versionButton.pressed.connect(obj.softwareUpdatePageInstance.displayVersionInfo)

        obj.restartButton.pressed.connect(obj.homePageInstance.askAndReboot)
        obj.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
        obj.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)

        obj.QRCodeBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.settingsPage))

    def pairPhoneApp(self):
        if getIP(ThreadRestartNetworking.ETH) is not None:
            qrip = getIP(ThreadRestartNetworking.ETH)
        elif getIP(ThreadRestartNetworking.WLAN) is not None:
            qrip = getIP(ThreadRestartNetworking.WLAN)
        else:
            if dialog.WarningOk(self.obj, "Network Disconnected"):
                return
        self.obj.QRCodeLabel.setPixmap(
            qrcode.make("http://"+ qrip, image_factory=Image).pixmap())
        self.stackedWidget.setCurrentWidget(self.QRCodePage)

    def restoreFactoryDefaults(self):
        if dialog.WarningYesNo(self.obj, "Are you sure you want to restore machine state to factory defaults?\nWarning: Doing so will also reset printer profiles, WiFi & Ethernet config.",
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
            self.obj.homePageInstance.tellAndReboot("Settings restored. Rebooting...")

    def restorePrintDefaults(self):
        if dialog.WarningYesNo(self.obj, "Are you sure you want to restore default print settings?\nWarning: Doing so will erase offsets and bed leveling info",
                                overlay=True):
            octopiclient.gcode(command='M502')
            octopiclient.gcode(command='M500')
