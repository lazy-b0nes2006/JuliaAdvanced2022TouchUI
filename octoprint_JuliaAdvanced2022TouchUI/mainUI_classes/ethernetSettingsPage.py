import subprocess
from PyQt5 import QtWidgets
import dialog
from threads import ThreadRestartNetworking
from network_utils import *
import re

class ethernetSettingsPage:
    def __init__(self, obj):
        obj.ethStaticCheckBox.stateChanged.connect(self.ethStaticChanged)
        obj.ethStaticCheckBox.stateChanged.connect(lambda: obj.ethStaticSettings.setVisible(obj.ethStaticCheckBox.isChecked()))
        obj.ethStaticIpKeyboardButton.pressed.connect(lambda: obj.ethShowKeyboard(obj.ethStaticIpLineEdit))
        obj.ethStaticGatewayKeyboardButton.pressed.connect(lambda: obj.ethShowKeyboard(obj.ethStaticGatewayLineEdit))
        obj.ethSettingsDoneButton.pressed.connect(self.ethSaveStaticNetworkInfo)
        obj.ethSettingsCancelButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.networkSettingsPage))

    def ethSettings(self):
        self.obj.stackedWidget.setCurrentWidget(self.obj.ethSettingsPage)
        self.ethNetworkInfo()

    def ethStaticChanged(self, state):
        self.obj.ethStaticSettings.setVisible(self.obj.ethStaticCheckBox.isChecked())
        self.obj.ethStaticSettings.setEnabled(self.obj.ethStaticCheckBox.isChecked())
        # if state == QtCore.Qt.Checked:
        #     self.obj.ethStaticSettings.setVisible(True)
        # else:
        #     self.obj.ethStaticSettings.setVisible(False)

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

        self.obj.ethStaticCheckBox.setChecked(cbStaticEnabled)
        self.obj.ethStaticSettings.setVisible(cbStaticEnabled)
        self.obj.ethStaticIpLineEdit.setText(txtEthAddress)
        self.obj.ethStaticGatewayLineEdit.setText(txtEthGateway)

    def isIpErr(self, ip):
        return (re.search(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", ip) is None)

    def showIpErr(self, var):
        return dialog.WarningOk(self.obj, "Invalid input: {0}".format(var))

    def ethSaveStaticNetworkInfo(self):
        cbStaticEnabled = self.obj.ethStaticCheckBox.isChecked()
        txtEthAddress = str(self.obj.ethStaticIpLineEdit.text())
        txtEthGateway = str(self.obj.ethStaticGatewayLineEdit.text())

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
            op = "interface eth0\nstatic ip_address={0}/24\nstatic routers={1}\nstatic domain_name_servers=8.8.8.8 8.8.4.4\n\n".format(txtEthAddress, txtEthGateway)

        res = re.sub(r"interface\s+eth0\s?(static\s+[a-z0-9./_=\s]+\n)*", op, txt)
        try:
            file = open("/etc/dhcpcd.conf", "w")
            file.write(res)
            file.close()
        except:
            if dialog.WarningOk(self.obj, "Failed to change Ethernet Interface configuration."):
                pass

        self.obj.restartEthThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.ETH)
        self.obj.restartEthThreadObject.signal.connect(self.ethReconnectResult)
        self.obj.restartEthThreadObject.start()
        self.obj.ethMessageBox = dialog.dialog(self.obj,
                                               "Restarting networking, please wait...",
                                               icon="exclamation-mark.png",
                                               buttons=QtWidgets.QMessageBox.Cancel)
        if self.obj.ethMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
            self.obj.stackedWidget.setCurrentWidget(self.obj.networkSettingsPage)

    def ethReconnectResult(self, x):
        self.obj.ethMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if x is not None:
            self.obj.ethMessageBox.setLocalIcon('success.png')
            self.obj.ethMessageBox.setText('Connected, IP: ' + x)
        else:
            self.obj.ethMessageBox.setText("Not able to connect to Ethernet")

    def ethShowKeyboard(self, textbox):
        self.obj.startKeyboard(textbox.setText, onlyNumeric=True, noSpace=True, text=str(textbox.text()))
