import io
import subprocess
import os
from PyQt5 import QtWidgets
import dialog
from threads import ThreadRestartNetworking
from network_utils import *
import time
from decorators import run_async

def network_connections(self):
    self.wifiPasswordLineEdit.clicked_signal.connect(lambda: self.startKeyboard(self.wifiPasswordLineEdit.setText))
    self.ethStaticIpLineEdit.clicked_signal.connect(lambda: self.ethShowKeyboard(self.ethStaticIpLineEdit))
    self.ethStaticGatewayLineEdit.clicked_signal.connect(lambda: self.ethShowKeyboard(self.ethStaticGatewayLineEdit))

    self.networkInfoButton.pressed.connect(self.networkInfo)
    self.configureWifiButton.pressed.connect(self.wifiSettings)
    self.configureEthButton.pressed.connect(self.ethSettings)
    
def acceptWifiSettings(self):
    wlan0_config_file = io.open("/etc/wpa_supplicant/wpa_supplicant.conf", "r+", encoding='utf8')
    wlan0_config_file.truncate()
    ascii_ssid = self.wifiSettingsComboBox.currentText()
    # unicode_ssid = ascii_ssid.decode('string_escape').decode('utf-8')
    wlan0_config_file.write(u"country=IN\n")
    wlan0_config_file.write(u"ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
    wlan0_config_file.write(u"update_config=1\n")
    wlan0_config_file.write(u"network={\n")
    wlan0_config_file.write(u'ssid="' + str(ascii_ssid) + '"\n')
    if self.hiddenCheckBox.isChecked():
        wlan0_config_file.write(u'scan_ssid=1\n')
    # wlan0_config_file.write(u"scan_ssid=1\n")
    if str(self.wifiPasswordLineEdit.text()) != "":
        wlan0_config_file.write(u'psk="' + str(self.wifiPasswordLineEdit.text()) + '"\n')
    # wlan0_config_file.write(u"key_mgmt=WPA-PSK\n")
    wlan0_config_file.write(u'}')
    wlan0_config_file.close()
    self.restartWifiThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.WLAN)
    self.restartWifiThreadObject.signal.connect(self.wifiReconnectResult)
    self.restartWifiThreadObject.start()
    self.wifiMessageBox = dialog.dialog(self,
                                        "Restarting networking, please wait...",
                                        icon="exclamation-mark.png",
                                        buttons=QtWidgets.QMessageBox.Cancel) 
    if self.wifiMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
        self.stackedWidget.setCurrentWidget(self.networkSettingsPage)

def wifiReconnectResult(self, x):
    self.wifiMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    if x is not None:
        print("Ouput from signal " + x)
        self.wifiMessageBox.setLocalIcon('success.png')
        self.wifiMessageBox.setText('Connected, IP: ' + x)
        self.wifiMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.ipStatus.setText(x) #sets the IP addr. in the status bar

    else:
        self.wifiMessageBox.setText("Not able to connect to WiFi")

def networkInfo(self):
    ipWifi = getIP(ThreadRestartNetworking.WLAN)
    ipEth = getIP(ThreadRestartNetworking.ETH)

    self.hostname.setText(getHostname())
    self.wifiAp.setText(getWifiAp())
    self.wifiIp.setText("Not connected" if not ipWifi else ipWifi)
    self.ipStatus.setText("Not connected" if not ipWifi else ipWifi)
    self.lanIp.setText("Not connected" if not ipEth else ipEth)
    self.wifiMac.setText(getMac(ThreadRestartNetworking.WLAN).decode('utf8'))
    self.lanMac.setText(getMac(ThreadRestartNetworking.ETH).decode('utf8'))
    self.stackedWidget.setCurrentWidget(self.networkInfoPage)

def wifiSettings(self):
    self.stackedWidget.setCurrentWidget(self.wifiSettingsPage)
    self.wifiSettingsComboBox.clear()
    self.wifiSettingsComboBox.addItems(self.scan_wifi())

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
    scan_result = scan_result.decode('utf8').split('ESSID:')  # each ssid and pass from an item in a list ([ssid pass,ssid paas])
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
                self.ipStatus.setText(getIP("eth0"))
            elif getIP("wlan0"):
                self.ipStatus.setText(getIP("wlan0"))
            else:
                self.ipStatus.setText("Not connected")

        except:
            self.ipStatus.setText("Not connected")
        time.sleep(60)


''' +++++++++++++++++++++++++++++++++Ethernet Settings+++++++++++++++++++++++++++++ '''

def ethSettings(self):
    self.stackedWidget.setCurrentWidget(self.ethSettingsPage)
    # self.ethStaticCheckBox.setChecked(True)
    self.ethNetworkInfo()

def ethStaticChanged(self, state):
    self.ethStaticSettings.setVisible(self.ethStaticCheckBox.isChecked())
    self.ethStaticSettings.setEnabled(self.ethStaticCheckBox.isChecked())
    # if state == QtCore.Qt.Checked:
    #     self.ethStaticSettings.setVisible(True)
    # else:
    #     self.ethStaticSettings.setVisible(False)

def ethNetworkInfo(self):
    txt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[0]

    reEthGlobal = b"interface\s+eth0\s?(static\s+[a-z0-9./_=\s]+\n)*"
    reEthAddress = b"static\s+ip_address=([\d.]+)(/[\d]{1,2})?"
    reEthGateway = b"static\s+routers=([\d.]+)(/[\d]{1,2})?"

    mtEthGlobal = re.search(reEthGlobal, txt)

    cbStaticEnabled = False
    txtEthAddress = ""
    txtEthGateway = ""

    if mtEthGlobal:
        sz = len(mtEthGlobal.groups())
        cbStaticEnabled = (sz == 1)

        if sz == 1:
            mtEthAddress = re.search(reEthAddress, mtEthGlobal.group(0))
            if mtEthAddress and len(mtEthAddress.groups()) == 2:
                txtEthAddress = mtEthAddress.group(1)
            mtEthGateway = re.search(reEthGateway, mtEthGlobal.group(0))
            if mtEthGateway and len(mtEthGateway.groups()) == 2:
                txtEthGateway = mtEthGateway.group(1)

    self.ethStaticCheckBox.setChecked(cbStaticEnabled)
    self.ethStaticSettings.setVisible(cbStaticEnabled)
    self.ethStaticIpLineEdit.setText(txtEthAddress)
    self.ethStaticGatewayLineEdit.setText(txtEthGateway)

def isIpErr(self, ip):
    return (re.search(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", ip) is None)

def showIpErr(self, var):
    return dialog.WarningOk(self, "Invalid input: {0}".format(var))

def ethSaveStaticNetworkInfo(self):
    cbStaticEnabled = self.ethStaticCheckBox.isChecked()
    txtEthAddress = str(self.ethStaticIpLineEdit.text())
    txtEthGateway = str(self.ethStaticGatewayLineEdit.text())

    if cbStaticEnabled:
        if self.isIpErr(txtEthAddress):
            return self.showIpErr("IP Address")
        if self.isIpErr(txtEthGateway):
            return self.showIpErr("Gateway")

    txt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[0]
    op = ""

    reEthGlobal = r"interface\s+eth0"
    mtEthGlobal = re.search(reEthGlobal, txt)

    if cbStaticEnabled:
        if not mtEthGlobal:
            txt = txt + "\n" + "interface eth0" + "\n"
        op = "interface eth0\nstatic ip_address={0}/24\nstatic routers={1}\nstatic domain_name_servers=8.8.8.8 8.8.4.4\n\n".format(
            txtEthAddress, txtEthGateway)

    res = re.sub(r"interface\s+eth0\s?(static\s+[a-z0-9./_=\s]+\n)*", op, txt)
    try:
        file = open("/etc/dhcpcd.conf", "w")
        file.write(res)
        file.close()
    except:
        if dialog.WarningOk(self, "Failed to change Ethernet Interface configuration."):
            pass

    # signal = 'ETH_RECONNECT_RESULT'
    # self.restartEthThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.ETH, signal)
    self.restartEthThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.ETH)
    self.restartEthThreadObject.signal.connect(self.ethReconnectResult)
    self.restartEthThreadObject.start()
    # self.connect(self.restartEthThreadObject, QtCore.SIGNAL(signal), self.ethReconnectResult)
    self.ethMessageBox = dialog.dialog(self,
                                        "Restarting networking, please wait...",
                                        icon="exclamation-mark.png",
                                        buttons=QtWidgets.QMessageBox.Cancel)
    if self.ethMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
        self.stackedWidget.setCurrentWidget(self.networkSettingsPage)

def ethReconnectResult(self, x):
    self.ethMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    if x is not None:
        self.ethMessageBox.setLocalIcon('success.png')
        self.ethMessageBox.setText('Connected, IP: ' + x)
    else:

        self.ethMessageBox.setText("Not able to connect to Ethernet")

def ethShowKeyboard(self, textbox):
    self.startKeyboard(textbox.setText, onlyNumeric=True, noSpace=True, text=str(textbox.text()))
