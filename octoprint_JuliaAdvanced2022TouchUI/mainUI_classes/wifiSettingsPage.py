import io
import subprocess
from PyQt5 import QtWidgets
import dialog
from threads import ThreadRestartNetworking
from network_utils import *
import time
from decorators import run_async

class wifiSettingsPage:
    def __init__(self, obj):
        self.obj = obj
        obj.wifiSettingsSSIDKeyboardButton.pressed.connect(
            lambda: obj.startKeyboard(obj.wifiSettingsComboBox.addItem))
        obj.wifiSettingsCancelButton.pressed.connect(
            lambda: obj.stackedWidget.setCurrentWidget(obj.networkSettingsPage))
        obj.wifiSettingsDoneButton.pressed.connect(self.acceptWifiSettings)

    def acceptWifiSettings(self):
        wlan0_config_file = io.open("/etc/wpa_supplicant/wpa_supplicant.conf", "r+", encoding='utf8')
        wlan0_config_file.truncate()
        ascii_ssid = self.obj.wifiSettingsComboBox.currentText()
        # unicode_ssid = ascii_ssid.decode('string_escape').decode('utf-8')
        wlan0_config_file.write(u"country=IN\n")
        wlan0_config_file.write(u"ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
        wlan0_config_file.write(u"update_config=1\n")
        wlan0_config_file.write(u"network={\n")
        wlan0_config_file.write(u'ssid="' + str(ascii_ssid) + '"\n')
        if self.obj.hiddenCheckBox.isChecked():
            wlan0_config_file.write(u'scan_ssid=1\n')
        # wlan0_config_file.write(u"scan_ssid=1\n")
        if str(self.obj.wifiPasswordLineEdit.text()) != "":
            wlan0_config_file.write(u'psk="' + str(self.obj.wifiPasswordLineEdit.text()) + '"\n')
        # wlan0_config_file.write(u"key_mgmt=WPA-PSK\n")
        wlan0_config_file.write(u'}')
        wlan0_config_file.close()
        self.obj.restartWifiThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.WLAN)
        self.obj.restartWifiThreadObject.signal.connect(self.wifiReconnectResult)
        self.obj.restartWifiThreadObject.start()
        self.obj.wifiMessageBox = dialog.dialog(self.obj,
                                                "Restarting networking, please wait...",
                                                icon="exclamation-mark.png",
                                                buttons=QtWidgets.QMessageBox.Cancel) 
        if self.obj.wifiMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
            self.obj.stackedWidget.setCurrentWidget(self.obj.networkSettingsPage)

    def wifiReconnectResult(self, x):
        self.obj.wifiMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if x is not None:
            print("Ouput from signal " + x)
            self.obj.wifiMessageBox.setLocalIcon('success.png')
            self.obj.wifiMessageBox.setText('Connected, IP: ' + x)
            self.obj.wifiMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.obj.ipStatus.setText(x) #sets the IP addr. in the status bar

        else:
            self.obj.wifiMessageBox.setText("Not able to connect to WiFi")

    def networkInfo(self):
        ipWifi = getIP(ThreadRestartNetworking.WLAN)
        ipEth = getIP(ThreadRestartNetworking.ETH)

        self.obj.hostname.setText(getHostname())
        self.obj.wifiAp.setText(getWifiAp())
        self.obj.wifiIp.setText("Not connected" if not ipWifi else ipWifi)
        self.obj.ipStatus.setText("Not connected" if not ipWifi else ipWifi)
        self.obj.lanIp.setText("Not connected" if not ipEth else ipEth)
        self.obj.wifiMac.setText(getMac(ThreadRestartNetworking.WLAN).decode('utf8'))
        self.obj.lanMac.setText(getMac(ThreadRestartNetworking.ETH).decode('utf8'))
        self.obj.stackedWidget.setCurrentWidget(self.obj.networkInfoPage)

    def wifiSettings(self):
        self.obj.stackedWidget.setCurrentWidget(self.obj.wifiSettingsPage)
        self.obj.wifiSettingsComboBox.clear()
        self.obj.wifiSettingsComboBox.addItems(self.scan_wifi())

    def scan_wifi(self):
        '''
        uses linux shell and WIFI interface to scan available networks
        :return: dictionary of the SSID and the signal strength
        '''
        # scanData = {}
        # print "Scanning available wireless signals available to wlan0"
        scan_result = \
            subprocess.Popen("iwlist wlan0 scan | grep 'ESSID'", stdout=subprocess.PIPE, shell=True).communicate()[0]
        # Processing STDOUT into a dictionary that later will be converted to a json file later
        scan_result = scan_result.decode('utf8').split('ESSID:')  # each ssid and pass from an item in a list ([ssid pass,ssid pass])
        scan_result = [s.strip() for s in scan_result]
        scan_result = [s.strip('"') for s in scan_result]
        scan_result = filter(None, scan_result)
        return scan_result

    @run_async
    def setIPStatus(self):
        '''
        Function to update IP address of printer on the status bar. Refreshes at a particular interval.
        '''
        while(True):
            try:
                if getIP("eth0"):
                    self.obj.ipStatus.setText(getIP("eth0"))
                elif getIP("wlan0"):
                    self.obj.ipStatus.setText(getIP("wlan0"))
                else:
                    self.obj.ipStatus.setText("Not connected")

            except:
                self.obj.ipStatus.setText("Not connected")
            time.sleep(60)
