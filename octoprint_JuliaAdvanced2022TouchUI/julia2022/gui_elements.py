import qrcode
import io
import requests
import re
import logging
import os
import subprocess
import time

import mainGUI
import keyboard
import dialog
import styles
import glob

from PyQt5 import QtWidgets, QtGui, QtCore
import mainGUI  # Ensure this is available in your Python path
from decorators import run_async  # Ensure this is available in your Python path
from config import Development 
from hurry.filesize import size
from datetime import datetime

from config import *
from config import _fromUtf8
from threads import *
from socket_qt import QtWebsocket
from network_utils import *
import base64

class Image(qrcode.image.base.BaseImage):
    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        size = (width + border * 2) * box_size
        self._image = QtGui.QImage(
            size, size, QtGui.QImage.Format_RGB16)
        self._image.fill(QtCore.Qt.white)

    def pixmap(self):
        return QtGui.QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        painter = QtGui.QPainter(self._image)
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size, self.box_size,
            QtCore.Qt.black)

    def save(self, stream, kind=None):
        pass

class ClickableLineEdit(QtWidgets.QLineEdit):
    clicked_signal = QtCore.pyqtSignal()
    def __init__(self, parent):
        QtWidgets.QLineEdit.__init__(self, parent)
    def mousePressEvent(self, QMouseEvent):
        #buzzer.buzz()
        self.clicked_signal.emit()


class MainUiClass(QtWidgets.QMainWindow, mainGUI.Ui_MainWindow):
    '''
    Main GUI Workhorse, all slots and events defined within
    The main implementation class that inherits methods, variables etc from mainGUI_pro_dual_abl.py and QMainWindow
    '''

    def setupUi(self, MainWindow):
        super(MainUiClass, self).setupUi(MainWindow)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Gotham"))
        font.setPointSize(15)

        self.wifiPasswordLineEdit = ClickableLineEdit(self.wifiSettingsPage)
        self.wifiPasswordLineEdit.setGeometry(QtCore.QRect(300, 170, 400, 60))
        self.wifiPasswordLineEdit.setFont(font)
        self.wifiPasswordLineEdit.setStyleSheet(styles.textedit)
        self.wifiPasswordLineEdit.setObjectName(_fromUtf8("wifiPasswordLineEdit"))

        font.setPointSize(11)
        self.staticIPLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.staticIPLineEdit.setGeometry(QtCore.QRect(200, 15, 450, 40))
        self.staticIPLineEdit.setFont(font)
        self.staticIPLineEdit.setStyleSheet(styles.textedit)
        self.staticIPLineEdit.setObjectName(_fromUtf8("staticIPLineEdit"))

        self.staticIPGatewayLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.staticIPGatewayLineEdit.setGeometry(QtCore.QRect(200, 85, 450, 40))
        self.staticIPGatewayLineEdit.setFont(font)
        self.staticIPGatewayLineEdit.setStyleSheet(styles.textedit)
        self.staticIPGatewayLineEdit.setObjectName(_fromUtf8("staticIPGatewayLineEdit"))

        self.staticIPNameServerLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.staticIPNameServerLineEdit.setGeometry(QtCore.QRect(200, 155, 450, 40))
        self.staticIPNameServerLineEdit.setFont(font)
        self.staticIPNameServerLineEdit.setStyleSheet(styles.textedit)
        self.staticIPNameServerLineEdit.setObjectName(_fromUtf8("staticIPNameServerLineEdit"))

        self.menuCartButton.setDisabled(True)
        self.testPrintsButton.setDisabled(True)

        self.movie = QtGui.QMovie("templates/img/loading-90.gif")
        self.loadingGif.setMovie(self.movie)
        self.movie.start()

    def __init__(self):
        '''
        This method gets called when an object of type MainUIClass is defined
        '''
        super(MainUiClass, self).__init__()
        if not Development:
            formatter = logging.Formatter("%(asctime)s %(message)s")
            self._logger = logging.getLogger("TouchUI")
            
            #file_handler = logging.FileHandler("/home/pi/ui.log")

            file_handler = logging.FileHandler("/home/arnav/Fracktal_works/refactor_touchUI/pi/ui.log")

            # script_dir = os.path.dirname(os.path.abspath(__file__))

            # # Define the path for the log file
            # log_file_path = os.path.join(script_dir, "ui.log")

            # # Create a file handler for logging
            # file_handler = logging.FileHandler(log_file_path)

            # # Set up logging configuration
            # logging.basicConfig(
            #     level=logging.INFO,
            #     format="%(asctime)s - %(levelname)s - %(message)s",
            #     handlers=[file_handler]
            # )

            file_handler.setFormatter(formatter)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self._logger.addHandler(file_handler)
            self._logger.addHandler(stream_handler)
        try:
            # if not Development:
                # self.__packager = asset_bundle.AssetBundle()
                # self.__packager.save_time()
                # self.__timelapse_enabled = self.__packager.read_match() if self.__packager.time_delta() else True
                # self.__timelapse_started = not self.__packager.time_delta()

                # self._logger.info("Hardware ID = {}, Unlocked = {}".format(self.__packager.hc(), self.__timelapse_enabled))
                # print("Hardware ID = {}, Unlocked = {}".format(self.__packager.hc(), self.__timelapse_enabled))
                # self._logger.info("File time = {}, Demo = {}".format(self.__packager.read_time(), self.__timelapse_started))
                # print("File time = {}, Demo = {}".format(self.__packager.read_time(), self.__timelapse_started))
            self.setupUi(self)
            self.stackedWidget.setCurrentWidget(self.loadingPage)
            self.setStep(10)
            self.keyboardWindow = None
            self.changeFilamentHeatingFlag = False
            self.setHomeOffsetBool = False
            self.currentImage = None
            self.currentFile = None
            # if not Development:
            #     self.sanityCheck = ThreadSanityCheck(self._logger, virtual=not self.__timelapse_enabled)
            # else:
            self.sanityCheck = ThreadSanityCheck(virtual=False)
            self.sanityCheck.start()
            self.sanityCheck.loaded_signal.connect(self.proceed)
            self.sanityCheck.startup_error_signal.connect(self.handleStartupError)
            self.setNewToolZOffsetFromCurrentZBool = False
            self.setActiveExtruder(0)

            self.dialog_doorlock = None
            self.dialog_filamentsensor = None

            for spinbox in self.findChildren(QtWidgets.QSpinBox):
                lineEdit = spinbox.lineEdit()
                lineEdit.setReadOnly(True)
                lineEdit.setDisabled(True)
                p = lineEdit.palette()
                p.setColor(QtGui.QPalette.Highlight, QtGui.QColor(40, 40, 40))
                lineEdit.setPalette(p)


        except Exception as e:
            self._logger.error(e)


    def safeProceed(self):
        '''
        When Octoprint server cannot connect for whatever reason, still show the home screen to conduct diagnostics
        '''
        self.movie.stop()
        if not Development:
            self.stackedWidget.setCurrentWidget(self.homePage)
            # self.Lock_showLock()
            self.setIPStatus()
        else:
            self.stackedWidget.setCurrentWidget(self.homePage)

        # Text Input events
        self.wifiPasswordLineEdit.clicked_signal.connect(lambda: self.startKeyboard(self.wifiPasswordLineEdit.setText))
        self.staticIPLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))
        self.staticIPGatewayLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
        self.staticIPNameServerLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))

        # Button Events:

        # Home Screen:
        self.stopButton.setDisabled(True)
        # self.menuButton.pressed.connect(self.keyboardButton)
        self.menuButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.controlButton.setDisabled(True)
        self.playPauseButton.setDisabled(True)

        # MenuScreen
        self.menuBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
        self.menuControlButton.setDisabled(True)
        self.menuPrintButton.setDisabled(True)
        self.menuCalibrateButton.setDisabled(True)
        self.menuSettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))


        # Settings Page
        self.networkSettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.displaySettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))
        self.settingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.pairPhoneButton.pressed.connect(self.pairPhoneApp)
        self.OTAButton.setDisabled(True)
        self.versionButton.setDisabled(True)

        self.restartButton.pressed.connect(self.askAndReboot)
        self.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
        self.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)

        # Network settings page
        self.networkInfoButton.pressed.connect(self.networkInfo)
        self.configureWifiButton.pressed.connect(self.wifiSettings)
        self.configureStaticIPButton.pressed.connect(self.staticIPSettings)
        self.networkSettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # Network Info Page
        self.networkInfoBackButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

        # WifiSetings page
        self.wifiSettingsSSIDKeyboardButton.pressed.connect(
            lambda: self.startKeyboard(self.wifiSettingsComboBox.addItem))
        self.wifiSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.wifiSettingsDoneButton.pressed.connect(self.acceptWifiSettings)

        # Static IP settings page
        self.staticIPKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))
        self.staticIPGatewayKeyboardButton.pressed.connect(
            lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
        self.staticIPNameServerKeyboardButton.pressed.connect(
            lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))
        self.staticIPSettingsDoneButton.pressed.connect(self.staticIPSaveStaticNetworkInfo)
        self.staticIPSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.deleteStaticIPSettingsButton.pressed.connect(self.deleteStaticIPSettings)

        # # Display settings
        # self.rotateDisplay.pressed.connect(self.showRotateDisplaySettingsPage)
        # self.calibrateTouch.pressed.connect(self.touchCalibration)
        self.displaySettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        #
        # # Rotate Display Settings
        # self.rotateDisplaySettingsDoneButton.pressed.connect(self.saveRotateDisplaySettings)
        # self.rotateDisplaySettingsCancelButton.pressed.connect(
        #     lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))

        # QR Code
        self.QRCodeBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # SoftwareUpdatePage
        self.softwareUpdateBackButton.setDisabled(True)
        self.performUpdateButton.setDisabled(True)

        # Firmware update page
        self.firmwareUpdateBackButton.setDisabled(True)

        # Filament sensor toggle
        self.toggleFilamentSensorButton.setDisabled(True)


    def handleStartupError(self):
        '''
        Error Handler when Octoprint gives up
        '''

        print('Unable to connect to Octoprint Server')
        if dialog.WarningYesNo(self,  "Server Error, Restore failsafe settings?", overlay=True):
            os.system('sudo rm -rf /home/pi/.octoprint/users.yaml')
            os.system('sudo rm -rf /home/pi/.octoprint/config.yaml')
            os.system('sudo cp -f config/users.yaml /home/pi/.octoprint/users.yaml')
            os.system('sudo cp -f config/config.yaml /home/pi/.octoprint/config.yaml')
            subprocess.call(["sudo", "systemctl", "restart", "octoprint"])
            self.sanityCheck.start()
        else:
            self.safeProceed()


    def proceed(self):
        '''
        Startes websocket, as well as initialises button actions and callbacks. THis is done in such a manner so that the callbacks that depend on websockets
        load only after the socket is available which in turn is dependent on the server being available which is checked in the sanity check thread
        '''
        self.QtSocket = QtWebsocket()
        self.QtSocket.start()
        self.setActions()
        self.movie.stop()
        if not Development:
            self.stackedWidget.setCurrentWidget(self.homePage)
            # self.Lock_showLock()
            self.setIPStatus()
        else:
            self.stackedWidget.setCurrentWidget(self.homePage)
        self.isFilamentSensorInstalled()
        self.onServerConnected()
        self.checkKlipperPrinterCFG()

    def setActions(self):

        '''
        defines all the Slots and Button events.
        '''

        #--Dual Caliberation Addition--
        self.QtSocket.set_z_tool_offset_signal.connect(self.setZToolOffset)
        self.QtSocket.z_probe_offset_signal.connect(self.updateEEPROMProbeOffset)
        self.QtSocket.temperatures_signal.connect(self.updateTemperature)
        self.QtSocket.status_signal.connect(self.updateStatus)
        self.QtSocket.print_status_signal.connect(self.updatePrintStatus)
        self.QtSocket.update_started_signal.connect(self.softwareUpdateProgress)
        self.QtSocket.update_log_signal.connect(self.softwareUpdateProgressLog)
        self.QtSocket.update_log_result_signal.connect(self.softwareUpdateResult)
        self.QtSocket.update_failed_signal.connect(self.updateFailed)
        self.QtSocket.connected_signal.connect(self.onServerConnected)
        self.QtSocket.filament_sensor_triggered_signal.connect(self.filamentSensorHandler)
        self.QtSocket.firmware_updater_signal.connect(self.firmwareUpdateHandler)
        #self.QtSocket.z_home_offset_signal.connect(self.getZHomeOffset)  Deprecated, uses probe offset to set initial height instead
        self.QtSocket.active_extruder_signal.connect(self.setActiveExtruder)
        self.QtSocket.z_probing_failed_signal.connect(self.showProbingFailed)
        self.QtSocket.tool_offset_signal.connect(self.getToolOffset)
        self.QtSocket.printer_error_signal.connect(self.showPrinterError)

        # Text Input events
        self.wifiPasswordLineEdit.clicked_signal.connect(lambda: self.startKeyboard(self.wifiPasswordLineEdit.setText))
        self.staticIPLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))
        self.staticIPGatewayLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
        self.staticIPNameServerLineEdit.clicked_signal.connect(lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))

        # Button Events:

        # Home Screen:
        self.stopButton.pressed.connect(self.stopActionMessageBox)
        # self.menuButton.pressed.connect(self.keyboardButton)
        self.menuButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.controlButton.pressed.connect(self.control)
        self.playPauseButton.clicked.connect(self.playPauseAction)
        self.doorLockButton.clicked.connect(self.doorLock)

        # MenuScreen
        self.menuBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
        self.menuControlButton.pressed.connect(self.control)
        self.menuPrintButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
        self.menuCalibrateButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        self.menuSettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # Calibrate Page
        self.calibrateBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.nozzleOffsetButton.pressed.connect(self.requestEEPROMProbeOffset)
        # the -ve sign is such that its converted to home offset and not just distance between nozzle and bed
        self.nozzleOffsetSetButton.pressed.connect(
            lambda: self.setZProbeOffset(self.nozzleOffsetDoubleSpinBox.value()))
        self.nozzleOffsetBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))

        # --Dual Caliberation Addition--
        self.moveZMT1CaliberateButton.pressed.connect(lambda: octopiclient.jog(z=-0.025))
        self.moveZPT1CaliberateButton.pressed.connect(lambda: octopiclient.jog(z=0.025))

        self.calibrationWizardButton.clicked.connect(self.quickStep1)
        self.quickStep1NextButton.clicked.connect(self.quickStep2)
        self.quickStep2NextButton.clicked.connect(self.quickStep3)
        self.quickStep3NextButton.clicked.connect(self.quickStep4)
        self.quickStep4NextButton.clicked.connect(self.nozzleHeightStep1)
        self.nozzleHeightStep1NextButton.clicked.connect(self.nozzleHeightStep1)
        self.quickStep1CancelButton.pressed.connect(self.cancelStep)
        self.quickStep2CancelButton.pressed.connect(self.cancelStep)
        self.quickStep3CancelButton.pressed.connect(self.cancelStep)
        self.quickStep4CancelButton.pressed.connect(self.cancelStep)
        self.nozzleHeightStep1CancelButton.pressed.connect(self.cancelStep)

        # --IDEX Caliberation Addition--

        self.idexCalibrationWizardButton.clicked.connect(self.idexConfigStep1)
        self.idexConfigStep1NextButton.clicked.connect(self.idexConfigStep2)
        self.idexConfigStep2NextButton.clicked.connect(self.idexConfigStep3)
        self.idexConfigStep3NextButton.clicked.connect(self.idexConfigStep4)
        self.idexConfigStep4NextButton.clicked.connect(self.idexConfigStep5)
        self.idexConfigStep5NextButton.clicked.connect(self.idexDoneStep)
        self.idexConfigStep1CancelButton.pressed.connect(self.idexCancelStep)
        self.idexConfigStep2CancelButton.pressed.connect(self.idexCancelStep)
        self.idexConfigStep3CancelButton.pressed.connect(self.idexCancelStep)
        self.idexConfigStep4CancelButton.pressed.connect(self.idexCancelStep)
        self.idexConfigStep5CancelButton.pressed.connect(self.idexCancelStep)
        self.moveZMIdexButton.pressed.connect(lambda: octopiclient.jog(z=-0.1))
        self.moveZPIdexButton.pressed.connect(lambda: octopiclient.jog(z=0.1))
        
        self.toolOffsetXSetButton.pressed.connect(self.setToolOffsetX)
        self.toolOffsetYSetButton.pressed.connect(self.setToolOffsetY)
        self.toolOffsetZSetButton.pressed.connect(self.setToolOffsetZ)
        self.toolOffsetXYBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        self.toolOffsetZBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        self.toolOffsetXYButton.pressed.connect(self.updateToolOffsetXY)
        self.toolOffsetZButton.pressed.connect(self.updateToolOffsetZ)

        self.testPrintsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.testPrintsPage1_6))
        self.testPrintsNextButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.testPrintsPage2_6))
        self.testPrintsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        self.testPrintsCancelButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        self.dualCaliberationPrintButton.pressed.connect(
            lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'dualCalibration'))
        self.bedLevelPrintButton.pressed.connect(
            lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'bedLevel'))
        self.movementTestPrintButton.pressed.connect(
            lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'movementTest'))
        self.singleNozzlePrintButton.pressed.connect(
            lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'dualTest'))
        self.dualNozzlePrintButton.pressed.connect(
            lambda: self.testPrint(str(self.testPrintsTool0SizeComboBox.currentText()).replace('.', ''),
                                   str(self.testPrintsTool1SizeComboBox.currentText()).replace('.', ''), 'singleTest'))

        # PrintLocationScreen
        self.printLocationScreenBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.fromLocalButton.pressed.connect(self.fileListLocal)
        self.fromUsbButton.pressed.connect(self.fileListUSB)

        # fileListLocalScreen
        self.localStorageBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
        self.localStorageScrollUp.pressed.connect(
            lambda: self.fileListWidget.setCurrentRow(self.fileListWidget.currentRow() - 1))
        self.localStorageScrollDown.pressed.connect(
            lambda: self.fileListWidget.setCurrentRow(self.fileListWidget.currentRow() + 1))
        self.localStorageSelectButton.pressed.connect(self.printSelectedLocal)
        self.localStorageDeleteButton.pressed.connect(self.deleteItem)

        # selectedFile Local Screen
        self.fileSelectedBackButton.pressed.connect(self.fileListLocal)
        self.fileSelectedPrintButton.pressed.connect(self.printFile)

        # filelistUSBPage
        self.USBStorageBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
        self.USBStorageScrollUp.pressed.connect(
            lambda: self.fileListWidgetUSB.setCurrentRow(self.fileListWidgetUSB.currentRow() - 1))
        self.USBStorageScrollDown.pressed.connect(
            lambda: self.fileListWidgetUSB.setCurrentRow(self.fileListWidgetUSB.currentRow() + 1))
        self.USBStorageSelectButton.pressed.connect(self.printSelectedUSB)
        self.USBStorageSaveButton.pressed.connect(lambda: self.transferToLocal(prnt=False))

        # selectedFile USB Screen
        self.fileSelectedUSBBackButton.pressed.connect(self.fileListUSB)
        self.fileSelectedUSBTransferButton.pressed.connect(lambda: self.transferToLocal(prnt=False))
        self.fileSelectedUSBPrintButton.pressed.connect(lambda: self.transferToLocal(prnt=True))

        # ControlScreen
        self.moveYPButton.pressed.connect(lambda: octopiclient.jog(y=self.step, speed=2000))
        self.moveYMButton.pressed.connect(lambda: octopiclient.jog(y=-self.step, speed=2000))
        self.moveXMButton.pressed.connect(lambda: octopiclient.jog(x=-self.step, speed=2000))
        self.moveXPButton.pressed.connect(lambda: octopiclient.jog(x=self.step, speed=2000))
        self.moveZPButton.pressed.connect(lambda: octopiclient.jog(z=self.step, speed=2000))
        self.moveZMButton.pressed.connect(lambda: octopiclient.jog(z=-self.step, speed=2000))
        self.extruderButton.pressed.connect(lambda: octopiclient.extrude(self.step))
        self.retractButton.pressed.connect(lambda: octopiclient.extrude(-self.step))
        self.motorOffButton.pressed.connect(lambda: octopiclient.gcode(command='M18'))
        self.fanOnButton.pressed.connect(lambda: octopiclient.gcode(command='M106 S255'))
        self.fanOffButton.pressed.connect(lambda: octopiclient.gcode(command='M107'))
        self.cooldownButton.pressed.connect(self.coolDownAction)
        self.step100Button.pressed.connect(lambda: self.setStep(100))
        self.step1Button.pressed.connect(lambda: self.setStep(1))
        self.step10Button.pressed.connect(lambda: self.setStep(10))
        self.homeXYButton.pressed.connect(lambda: octopiclient.home(['x', 'y']))
        self.homeZButton.pressed.connect(lambda: octopiclient.home(['z']))
        self.toolToggleTemperatureButton.clicked.connect(self.selectToolTemperature)
        self.toolToggleMotionButton.clicked.connect(self.selectToolMotion)
        self.controlBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
        self.setToolTempButton.pressed.connect(self.setToolTemp)
        self.tool180PreheatButton.pressed.connect(lambda: octopiclient.gcode(command='M104 T1 S180') if self.toolToggleTemperatureButton.isChecked() else octopiclient.gcode(command='M104 T0 S180'))
        self.tool250PreheatButton.pressed.connect(lambda: octopiclient.gcode(command='M104 T1 S250') if self.toolToggleTemperatureButton.isChecked() else octopiclient.gcode(command='M104 T0 S250'))
        self.tool180PreheatButton.pressed.connect(lambda: self.preheatToolTemp(180))
        self.tool250PreheatButton.pressed.connect(lambda: self.preheatToolTemp(250))
        self.setBedTempButton.pressed.connect(lambda: octopiclient.setBedTemperature(self.bedTempSpinBox.value()))
        self.bed60PreheatButton.pressed.connect(lambda: self.preheatBedTemp(60))
        self.bed100PreheatButton.pressed.connect(lambda: self.preheatBedTemp(100))
        #self.chamber40PreheatButton.pressed.connect(lambda: self.preheatChamberTemp(40))
        #self.chamber70PreheatButton.pressed.connect(lambda: self.preheatChamberTemp(70))
        #self.setChamberTempButton.pressed.connect(lambda: octopiclient.gcode(command='M141 S{}'.format(self.chamberTempSpinBox.value())))
        self.setFlowRateButton.pressed.connect(lambda: octopiclient.flowrate(self.flowRateSpinBox.value()))
        self.setFeedRateButton.pressed.connect(lambda: octopiclient.feedrate(self.feedRateSpinBox.value()))

        self.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z0.025'))
        self.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z-0.025'))

        # ChangeFilament rutien
        self.changeFilamentButton.pressed.connect(self.changeFilament)
        self.toolToggleChangeFilamentButton.clicked.connect(self.selectToolChangeFilament)
        self.changeFilamentBackButton.pressed.connect(self.control)
        self.changeFilamentBackButton2.pressed.connect(self.changeFilamentCancel)
        self.changeFilamentBackButton3.pressed.connect(self.changeFilamentCancel)
        self.changeFilamentUnloadButton.pressed.connect(self.unloadFilament)
        self.changeFilamentLoadButton.pressed.connect(self.loadFilament)
        self.loadedTillExtruderButton.pressed.connect(self.changeFilamentExtrudePageFunction)
        self.loadDoneButton.pressed.connect(self.control)
        self.unloadDoneButton.pressed.connect(self.changeFilament)
        # self.retractFilamentButton.pressed.connect(lambda: octopiclient.extrude(-20))
        # self.ExtrudeButton.pressed.connect(lambda: octopiclient.extrude(20))

        # Settings Page
        self.settingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        self.networkSettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.displaySettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))
        self.pairPhoneButton.pressed.connect(self.pairPhoneApp)
        self.OTAButton.pressed.connect(self.softwareUpdate)
        self.versionButton.pressed.connect(self.displayVersionInfo)
        self.restartButton.pressed.connect(self.askAndReboot)
        self.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
        self.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)

        # Network settings page
        self.networkInfoButton.pressed.connect(self.networkInfo)
        self.configureWifiButton.pressed.connect(self.wifiSettings)
        self.configureStaticIPButton.pressed.connect(self.staticIPSettings)
        self.networkSettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # Network Info Page
        self.networkInfoBackButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

        # WifiSetings page
        self.wifiSettingsSSIDKeyboardButton.pressed.connect(
            lambda: self.startKeyboard(self.wifiSettingsComboBox.addItem))
        self.wifiSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.wifiSettingsDoneButton.pressed.connect(self.acceptWifiSettings)

        # Static IP settings page
        self.staticIPKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPLineEdit))                                                                            
        self.staticIPGatewayKeyboardButton.pressed.connect(lambda: self.staticIPShowKeyboard(self.staticIPGatewayLineEdit))
        self.staticIPNameServerKeyboardButton.pressed.connect(
            lambda: self.staticIPShowKeyboard(self.staticIPNameServerLineEdit))
        self.staticIPSettingsDoneButton.pressed.connect(self.staticIPSaveStaticNetworkInfo)
        self.staticIPSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.deleteStaticIPSettingsButton.pressed.connect(self.deleteStaticIPSettings)

        # # Display settings
        # self.rotateDisplay.pressed.connect(self.showRotateDisplaySettingsPage)
        # self.calibrateTouch.pressed.connect(self.touchCalibration)
        self.displaySettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        #
        # # Rotate Display Settings
        # self.rotateDisplaySettingsDoneButton.pressed.connect(self.saveRotateDisplaySettings)
        # self.rotateDisplaySettingsCancelButton.pressed.connect(
        #     lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))

        # QR Code
        self.QRCodeBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # SoftwareUpdatePage
        self.softwareUpdateBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        self.performUpdateButton.pressed.connect(lambda: octopiclient.performSoftwareUpdate())

        # Firmware update page
        self.firmwareUpdateBackButton.pressed.connect(self.firmwareUpdateBack)

        # Filament sensor toggle
        self.toggleFilamentSensorButton.clicked.connect(self.toggleFilamentSensor)

    ''' +++++++++++++++++++++++++Print Restore+++++++++++++++++++++++++++++++++++ '''

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

    ''' +++++++++++++++++++++++++Filament Sensor++++++++++++++++++++++++++++++++++++++ '''

    def isFilamentSensorInstalled(self):
        success = False
        try:
            headers = {'X-Api-Key': apiKey}
            req = requests.get('http://{}/plugin/Julia2018FilamentSensor/status'.format(ip), headers=headers)
            success = req.status_code == requests.codes.ok
        except:
            pass
        # self.toggleFilamentSensorButton.setEnabled(success)
        return success

    def toggleFilamentSensor(self):
        # headers = {'X-Api-Key': apiKey}
        # # payload = {'sensor_enabled': self.toggleFilamentSensorButton.isChecked()}
        # requests.get('http://{}/plugin/Julia2018FilamentSensor/toggle'.format(ip), headers=headers)   # , data=payload)
        icon = 'filamentSensorOn' if self.toggleFilamentSensorButton.isChecked() else 'filamentSensorOff'
        self.toggleFilamentSensorButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon)))
        #octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=SFS_T0 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
        #octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=SFS_T1 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
        octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=switch_sensor_T0 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
        octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=encoder_sensor_T0 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
        octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=switch_sensor_T1 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
        octopiclient.gcode(command="SET_FILAMENT_SENSOR SENSOR=encoder_sensor_T1 ENABLE={}".format(int(self.toggleFilamentSensorButton.isChecked())))
    def filamentSensorHandler(self, data):
        try:
            # sensor_enabled = False
            # # print(data)
            #
            # if 'sensor_enabled' in data:
            #     sensor_enabled = data["sensor_enabled"] == 1
            print(data)

            icon = 'filamentSensorOn' if self.toggleFilamentSensorButton.isChecked() else 'filamentSensorOff'
            self.toggleFilamentSensorButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon)))

            if not self.toggleFilamentSensorButton.isChecked():  
                return

            triggered_extruder0 = False
            triggered_extruder1 = False
            # triggered_door = False
            # pause_print = False
            # triggered_door = False
            # pause_print = False

            if '0' in data:
                triggered_extruder0 = True

            if '1' in data:
                triggered_extruder1 = True

            # if 'door' in data:
            #     triggered_door = data["door"] == 0
            # if 'pause_print' in data:
            #     pause_print = data["pause_print"]
                
            # if 'door' in data:
            #     triggered_door = data["door"] == 0
            # if 'pause_print' in data:
            #     pause_print = data["pause_print"]

            if triggered_extruder0 and self.stackedWidget.currentWidget() not in [self.changeFilamentPage, self.changeFilamentProgressPage,
                                    self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage]:
                octopiclient.gcode(command='PAUSE')
                if dialog.WarningOk(self, "Filament outage or clog detected in Extruder 0. Please check the external motors. Print paused"):
                    pass

            if triggered_extruder1 and self.stackedWidget.currentWidget() not in [self.changeFilamentPage, self.changeFilamentProgressPage,
                                    self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage]:
                octopiclient.gcode(command='PAUSE')
                if dialog.WarningOk(self, "Filament outage or clog detected in Extruder 1. Please check the external motors. Print paused"):
                    pass

            # if triggered_door:
            #     if self.printerStatusText == "Printing":
            #         no_pause_pages = [self.controlPage, self.changeFilamentPage, self.changeFilamentProgressPage,
            #                           self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage,]
            #         if not pause_print or self.stackedWidget.currentWidget() in no_pause_pages:
            #             if dialog.WarningOk(self, "Door opened"):
            #                 return
            #         octopiclient.pausePrint()
            #         if dialog.WarningOk(self, "Door opened. Print paused.", overlay=True):
            #             return
            #     else:
            #         if dialog.WarningOk(self, "Door opened"):
            #             return
            # if triggered_door:
            #     if self.printerStatusText == "Printing":
            #         no_pause_pages = [self.controlPage, self.changeFilamentPage, self.changeFilamentProgressPage,
            #                           self.changeFilamentExtrudePage, self.changeFilamentRetractPage,self.changeFilamentLoadPage,]
            #         if not pause_print or self.stackedWidget.currentWidget() in no_pause_pages:
            #             if dialog.WarningOk(self, "Door opened"):
            #                 return
            #         octopiclient.pausePrint()
            #         if dialog.WarningOk(self, "Door opened. Print paused.", overlay=True):
            #             return
            #     else:
            #         if dialog.WarningOk(self, "Door opened"):
            #             return
        except Exception as e:
            print(e)

																			  

    ''' +++++++++++++++++++++++++++ Door Lock +++++++++++++++++++++++++++++++++++++ '''

    def doorLock(self):
        '''
        function that toggles locking and unlocking the front door
        :return:
        '''
        octopiclient.gcode(command='DoorToggle')

    def doorLockMsg(self, data):
        if "msg" not in data:
            return

        msg = data["msg"]

        if self.dialog_doorlock:
            self.dialog_doorlock.close()
            self.dialog_doorlock = None

        if msg is not None:
            self.dialog_doorlock = dialog.dialog(self, msg, icon="exclamation-mark.png")
            if self.dialog_doorlock.exec_() == QtGui.QMessageBox.Ok:
                self.dialog_doorlock = None
                return

    def doorLockHandler(self, data):
        door_lock_disabled = False
        door_lock = False
        # door_sensor = False
        # door_lock_override = False

        if 'door_lock' in data:
            door_lock_disabled = data["door_lock"] == "disabled"
            door_lock = data["door_lock"] == 1
        # if 'door_sensor' in data:
        #     door_sensor = data["door_sensor"] == 1
        # if 'door_lock_override' in data:
        #     door_lock_override = data["door_lock_override"] == 1

        # if self.dialog_doorlock:
        #     self.dialog_doorlock.close()
        #     self.dialog_doorlock = None

        self.doorLockButton.setVisible(not door_lock_disabled)
        if not door_lock_disabled:
            # self.doorLockButton.setChecked(not door_lock)
            self.doorLockButton.setText('Lock Door' if not door_lock else 'Unlock Door')

            icon = 'doorLock' if not door_lock else 'doorUnlock'
            self.doorLockButton.setIcon(QtGui.QIcon(_fromUtf8("templates/img/" + icon + ".png")))
        else:
            return

    ''' +++++++++++++++++++++++++++ Firmware Update+++++++++++++++++++++++++++++++++++ '''

    isFirmwareUpdateInProgress = False

    def firmwareUpdateCheck(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/check'.format(ip), headers=headers)

    def firmwareUpdateStart(self):
        headers = {'X-Api-Key': apiKey}
        requests.get('http://{}/plugin/JuliaFirmwareUpdater/update/start'.format(ip), headers=headers)

    def firmwareUpdateStartProgress(self):
        self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
        # self.firmwareUpdateLog.setTextColor(QtCore.Qt.yellow)
        self.firmwareUpdateLog.setText("<span style='color: cyan'>Julia Firmware Updater<span>")
        self.firmwareUpdateLog.append("<span style='color: cyan'>---------------------------------------------------------------</span>")
        self.firmwareUpdateBackButton.setEnabled(False)

    def firmwareUpdateProgress(self, text, backEnabled=False):
        self.stackedWidget.setCurrentWidget(self.firmwareUpdateProgressPage)
        # self.firmwareUpdateLog.setTextColor(QtCore.Qt.yellow)
        self.firmwareUpdateLog.append(str(text))
        self.firmwareUpdateBackButton.setEnabled(backEnabled)

    def firmwareUpdateBack(self):
        self.isFirmwareUpdateInProgress = False
        self.firmwareUpdateBackButton.setEnabled(False)
        self.stackedWidget.setCurrentWidget(self.homePage)

    def firmwareUpdateHandler(self, data):
        if "type" not in data or data["type"] != "status":
            return

        if "status" not in data:
            return

        status = data["status"]
        subtype = data["subtype"] if "subtype" in data else None

        if status == "update_check":    # update check
            if subtype == "error":  # notify error in ok diag
                self.isFirmwareUpdateInProgress = False
                if "message" in data:
                    dialog.WarningOk(self, "Firmware Updater Error: " + str(data["message"]), overlay=True)
            elif subtype == "success":
                if dialog.SuccessYesNo(self, "Firmware update found.\nPress yes to update now!", overlay=True):
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
                # self.firmwareUpdateProgress(data["message"] if "message" in data else "Unknown error!", backEnabled=True)
                if "message" in data:
                    dialog.WarningOk(self, "Firmware Updater Error: " + str(data["message"]), overlay=True)
        elif status == "flasherror" or status == "progress":    # show software update dialog and update textview
            if "message" in data:
                message = "<span style='color: {}'>{}</span>".format("teal" if status == "progress" else "red", data["message"])
                self.firmwareUpdateProgress(message, backEnabled=(status == "flasherror"))
        elif status == "success":    # show ok diag to show done
            self.isFirmwareUpdateInProgress = False
            message = data["message"] if "message" in data else "Flash successful!"
            message = "<span style='color: green'>{}</span>".format(message)
            message = message + "<br/><br/><span style='color: white'>Press back to continue...</span>"
            self.firmwareUpdateProgress(message, backEnabled=True)


    ''' +++++++++++++++++++++++++++++++++OTA Update+++++++++++++++++++++++++++++++++++ '''

    def getFirmwareVersion(self):
        try:
            headers = {'X-Api-Key': apiKey}
            req = requests.get('http://{}/plugin/JuliaFirmwareUpdater/hardware/version'.format(ip), headers=headers)
            data = req.json()
            # print(data)
            if req.status_code == requests.codes.ok:
                info = u'\u2713' if not data["update_available"] else u"\u2717"    # icon
                info += " Firmware: "
                info += "Unknown" if not data["variant_name"] else data["variant_name"]
                info += "\n"
                if data["variant_name"]:
                    info += "   Installed: "
                    info += "Unknown" if not data["version_board"] else data["version_board"]
                info += "\n"
                info += "" if not data["version_repo"] else "   Available: " + data["version_repo"]
                return info
        except:
            print("Error accessing /plugin/JuliaFirmwareUpdater/hardware/version")
            pass
        return u'\u2713' + "Firmware: Unknown\n"

    def displayVersionInfo(self):
        self.updateListWidget.clear()
        updateAvailable = False
        self.performUpdateButton.setDisabled(True)

        # Firmware version on the MKS https://github.com/FracktalWorks/OctoPrint-JuliaFirmwareUpdater
        # self.updateListWidget.addItem(self.getFirmwareVersion())

        data = octopiclient.getSoftwareUpdateInfo()
        if data:
            for item in data["information"]:
                # print(item)
                plugin = data["information"][item]
                info = u'\u2713' if not plugin["updateAvailable"] else u"\u2717"    # icon
                info += plugin["displayName"] + "  " + plugin["displayVersion"] + "\n"
                info += "   Available: "
                if "information" in plugin and "remote" in plugin["information"] and plugin["information"]["remote"]["value"] is not None:
                    info += plugin["information"]["remote"]["value"]
                else:
                    info += "Unknown"
                self.updateListWidget.addItem(info)

                if plugin["updateAvailable"]:
                    updateAvailable = True

                # if not updatable:
                #     self.updateListWidget.addItem(u'\u2713' + data["information"][item]["displayName"] +
                #                                   "  " + data["information"][item]["displayVersion"] + "\n"
                #                                   + "   Available: " +
                #                                   )
                # else:
                #     updateAvailable = True
                #     self.updateListWidget.addItem(u"\u2717" + data["information"][item]["displayName"] +
                #                                   "  " + data["information"][item]["displayVersion"] + "\n"
                #                                   + "   Available: " +
                #                                   data["information"][item]["information"]["remote"]["value"])
        if updateAvailable:
            self.performUpdateButton.setDisabled(False)
        self.stackedWidget.setCurrentWidget(self.OTAUpdatePage)

    def softwareUpdateResult(self, data):
        messageText = ""
        for item in data:
            messageText += item + ": " + data[item][0] + ".\n"
        messageText += "Restart required"
        self.askAndReboot(messageText)

    def softwareUpdateProgress(self, data):
        self.stackedWidget.setCurrentWidget(self.softwareUpdateProgressPage)
        self.logTextEdit.setTextColor(QtCore.Qt.red)
        self.logTextEdit.append("---------------------------------------------------------------\n"
                                "Updating " + data["name"] + " to " + data["version"] + "\n"
                                                                                        "---------------------------------------------------------------")

    def softwareUpdateProgressLog(self, data):
        self.logTextEdit.setTextColor(QtCore.Qt.white)
        for line in data:
            self.logTextEdit.append(line["line"])

    def updateFailed(self, data):
        self.stackedWidget.setCurrentWidget(self.settingsPage)
        messageText = (data["name"] + " failed to update\n")
        if dialog.WarningOkCancel(self, messageText, overlay=True):
            pass

    def softwareUpdate(self):
        data = octopiclient.getSoftwareUpdateInfo()
        updateAvailable = False
        if data:
            for item in data["information"]:
                if data["information"][item]["updateAvailable"]:
                    updateAvailable = True
        if updateAvailable:
            print('Update Available')
            if dialog.SuccessYesNo(self, "Update Available! Update Now?", overlay=True):
                octopiclient.performSoftwareUpdate()

        else:
            if dialog.SuccessOk(self, "System is Up To Date!", overlay=True):
                print('Update Unavailable')

    ''' +++++++++++++++++++++++++++++++++Wifi Config+++++++++++++++++++++++++++++++++++ '''

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


    ''' +++++++++++++++++++++++++++++++++Static IP Settings+++++++++++++++++++++++++++++ '''

    def staticIPSettings(self):
        self.stackedWidget.setCurrentWidget(self.staticIPSettingsPage)
        #add "eth0" and "wlan0" to staticIPComboBox:
        self.staticIPComboBox.clear()
        self.staticIPComboBox.addItems(["eth0", "wlan0"])

    def isIpErr(self, ip):
        return (re.search(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", ip) is None)

    def showIpErr(self, var):
        return dialog.WarningOk(self, "Invalid input: {0}".format(var))

    def staticIPSaveStaticNetworkInfo(self):
        txtStaticIPInterface = self.staticIPComboBox.currentText()
        txtStaticIPAddress = str(self.staticIPLineEdit.text())
        txtStaticIPGateway = str(self.staticIPGatewayLineEdit.text())
        txtStaticIPNameServer = str(self.staticIPNameServerLineEdit.text())
        if self.isIpErr(txtStaticIPAddress):
            return self.showIpErr("IP Address")
        if self.isIpErr(txtStaticIPGateway):
            return self.showIpErr("Gateway")
        if txtStaticIPNameServer != "":
            if self.isIpErr(txtStaticIPNameServer):
                return self.showIpErr("NameServer")
        Globaltxt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[
            0].decode('utf8')
        staticIPConfig = ""
        # using regex remove all lines staring with "interface" and "static" from txt
        Globaltxt = re.sub(r"interface.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"static.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"^\s+", "", Globaltxt)                                                 
        staticIPConfig = "\ninterface {0}\nstatic ip_address={1}/24\nstatic routers={2}\nstatic domain_name_servers=8.8.8.8 8.8.4.4 {3}\n\n".format(
            txtStaticIPInterface, txtStaticIPAddress, txtStaticIPGateway, txtStaticIPNameServer)
        Globaltxt = staticIPConfig + Globaltxt
        with open("/etc/dhcpcd.conf", "w") as f:
            f.write(Globaltxt)

        if txtStaticIPInterface == 'eth0':
            print("Restarting networking for eth0")
            self.restartStaticIPThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.ETH)
            self.restartStaticIPThreadObject.signal.connect(self.staticIPReconnectResult)
            self.restartStaticIPThreadObject.start()
            # self.connect(self.restartStaticIPThreadObject, QtCore.SIGNAL(signal), self.staticIPReconnectResult)
            self.staticIPMessageBox = dialog.dialog(self,
                                                    "Restarting networking, please wait...",
                                                    icon="exclamation-mark.png",
                                                    buttons=QtWidgets.QMessageBox.Cancel)
            if self.staticIPMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                self.stackedWidget.setCurrentWidget(self.networkSettingsPage)
        elif txtStaticIPInterface == 'wlan0':
            print("Restarting networking for wlan0")
            self.restartWifiThreadObject = ThreadRestartNetworking(ThreadRestartNetworking.WLAN)
            self.restartWifiThreadObject.signal.connect(self.wifiReconnectResult)
            self.restartWifiThreadObject.start()
            self.wifiMessageBox = dialog.dialog(self,
                                                "Restarting networking, please wait...",
                                                icon="exclamation-mark.png",
                                                buttons=QtWidgets.QMessageBox.Cancel)
            if self.wifiMessageBox.exec_() in {QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel}:
                self.stackedWidget.setCurrentWidget(self.networkSettingsPage)

    def deleteStaticIPSettings(self):
        Globaltxt = subprocess.Popen("cat /etc/dhcpcd.conf", stdout=subprocess.PIPE, shell=True).communicate()[
            0].decode('utf8')
        # using regex remove all lines staring with "interface" and "static" from txt
        Globaltxt = re.sub(r"interface.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"static.*\n", "", Globaltxt)
        Globaltxt = re.sub(r"^\s+", "", Globaltxt)
        with open("/etc/dhcpcd.conf", "w") as f:
            f.write(Globaltxt)
        self.stackedWidget.setCurrentWidget(self.networkSettingsPage)                                                  
                                                                                                  
    def staticIPReconnectResult(self, x):
        self.staticIPMessageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if x is not None:
            self.staticIPMessageBox.setLocalIcon('success.png')
            self.staticIPMessageBox.setText('Connected, IP: ' + x)
        else:

            self.staticIPMessageBox.setText("Not able to set Static IP")

    def staticIPShowKeyboard(self, textbox):
        self.startKeyboard(textbox.setText, onlyNumeric=True, noSpace=True, text=str(textbox.text()))
    ''' ++++++++++++++++++++++++++++++++Display Settings+++++++++++++++++++++++++++++++ '''

    def touchCalibration(self):
        #os.system('sudo /home/pi/setenv.sh')
        os.system('sudo su')
        os.system('export TSLIB_TSDEVICE=/dev/input/event0')
        os.system('export TSLIB_FBDEVICE=/dev/fb0')
        os.system('ts_calibrate')


    # def showRotateDisplaySettingsPage(self):
    #
    #     txt = (subprocess.Popen("cat /boot/config.txt", stdout=subprocess.PIPE, shell=True).communicate()[0]).decode("utf-8")
    #
    #     reRot = r"dtoverlay\s*=\s*waveshare35a(\s*:\s*rotate\s*=\s*([0-9]{1,3})){0,1}"
    #     mtRot = re.search(reRot, txt)
    #     # print(mtRot.group(0))
    #
    #     if mtRot and len(mtRot.groups()) == 2 and str(mtRot.group(2)) == "270":
    #         self.rotateDisplaySettingsComboBox.setCurrentIndex(1)
    #     else:
    #         self.rotateDisplaySettingsComboBox.setCurrentIndex(0)
    #
    #     self.stackedWidget.setCurrentWidget(self.rotateDisplaySettingsPage)

    # def saveRotateDisplaySettings(self):
    #     txt1 = (subprocess.Popen("cat /boot/config.txt", stdout=subprocess.PIPE, shell=True).communicate()[0]).decode("utf-8")
    #
    #     reRot = r"dtoverlay\s*=\s*waveshare35a(\s*:\s*rotate\s*=\s*([0-9]{1,3})){0,1}"
    #     if self.rotateDisplaySettingsComboBox.currentIndex() == 1:
    #         op1 = "dtoverlay=waveshare35a,rotate=270,fps=12,speed=16000000"
    #     else:
    #         op1 = "dtoverlay=waveshare35a,fps=12,speed=16000000"
    #     res1 = re.sub(reRot, op1, txt1)
    #
    #     try:
    #         file1 = open("/boot/config.txt", "w")
    #         file1.write(res1)
    #         file1.close()
    #     except:
    #         if dialog.WarningOk(self, "Failed to change rotation settings", overlay=True):
    #             return
    #
    #     txt2 = (subprocess.Popen("cat /usr/share/X11/xorg.conf.d/99-calibration.conf", stdout=subprocess.PIPE,
    #                             shell=True).communicate()[0]).decode("utf-8")
    #
    #     reTouch = r"Option\s+\"Calibration\"\s+\"([\d\s-]+)\""
    #     if self.rotateDisplaySettingsComboBox.currentIndex() == 1:
    #         op2 = "Option \"Calibration\"  \"3919 208 236 3913\""
    #     else:
    #         op2 = "Option \"Calibration\"  \"300 3932 3801 294\""
    #     res2 = re.sub(reTouch, op2, txt2, flags=re.I)
    #
    #     try:
    #         file2 = open("/usr/share/X11/xorg.conf.d/99-calibration.conf", "w")
    #         file2.write(res2)
    #         file2.close()
    #     except:
    #         if dialog.WarningOk(self, "Failed to change touch settings", overlay=True):
    #             return
    #
    #     self.askAndReboot()
    #     self.stackedWidget.setCurrentWidget(self.displaySettingsPage)

    # def saveRotateDisplaySettings(self):
    #     txt1 = (subprocess.Popen("cat /boot/config.txt", stdout=subprocess.PIPE, shell=True).communicate()[0]).decode("utf-8")
    #
    #     try:
    #         if self.rotateDisplaySettingsComboBox.currentIndex() == 1:
    #             os.system('sudo cp -f config/config.txt /boot/config.txt')
    #         else:
    #             os.system('sudo cp -f config/config_rot.txt /boot/config.txt')
    #     except:
    #         if dialog.WarningOk(self, "Failed to change rotation settings", overlay=True):
    #             return
    #     try:
    #         if self.rotateDisplaySettingsComboBox.currentIndex() == 1:
    #             os.system('sudo cp -f config/99-calibration.conf /usr/share/X11/xorg.conf.d/99-calibration.conf')
    #         else:
    #             os.system('sudo cp -f config/99-calibration_rot.conf /usr/share/X11/xorg.conf.d/99-calibration.conf')
    #     except:
    #         if dialog.WarningOk(self, "Failed to change touch settings", overlay=True):
    #             return
    #
    #     self.askAndReboot()
    #     self.stackedWidget.setCurrentWidget(self.displaySettingsPage)
    #

    ''' +++++++++++++++++++++++++++++++++Change Filament+++++++++++++++++++++++++++++++ '''

    def calcExtrudeTime(self, length, speed):
        '''
        Calculate the time it takes to extrude a certain length of filament at a certain speed
        :param length: length of filament to extrude
        :param speed: speed at which to extrude
        :return: time in seconds
        '''
        return length / (speed/60)

    def unloadFilament(self):
        #Update
        if self.printerStatusText not in ["Printing","Paused"]:
            if self.activeExtruder == 1:
                octopiclient.jog(tool1PurgePosition['X'],tool1PurgePosition["Y"] ,absolute=True, speed=10000)
                
            else:
                octopiclient.jog(tool0PurgePosition['X'],tool0PurgePosition["Y"] ,absolute=True, speed=10000)
                
        if self.changeFilamentComboBox.findText("Loaded Filament") == -1:
            octopiclient.setToolTemperature({"tool1": filaments[str(
                self.changeFilamentComboBox.currentText())]}) if self.activeExtruder == 1 else octopiclient.setToolTemperature(
                {"tool0": filaments[str(self.changeFilamentComboBox.currentText())]})
        self.stackedWidget.setCurrentWidget(self.changeFilamentProgressPage)
        self.changeFilamentStatus.setText("Heating Tool {}, Please Wait...".format(str(self.activeExtruder)))
        self.changeFilamentNameOperation.setText("Unloading {}".format(str(self.changeFilamentComboBox.currentText())))
        # this flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
        self.changeFilamentHeatingFlag = True
        self.loadFlag = False

    def loadFilament(self):
        #Update
        if self.printerStatusText not in ["Printing","Paused"]:
            if self.activeExtruder == 1:
                octopiclient.jog(tool1PurgePosition['X'],tool1PurgePosition["Y"] ,absolute=True, speed=10000)
                
            else:
                octopiclient.jog(tool0PurgePosition['X'],tool0PurgePosition["Y"] ,absolute=True, speed=10000)

        if self.changeFilamentComboBox.findText("Loaded Filament") == -1:
            octopiclient.setToolTemperature({"tool1": filaments[str(
                self.changeFilamentComboBox.currentText())]}) if self.activeExtruder == 1 else octopiclient.setToolTemperature(
                {"tool0": filaments[str(self.changeFilamentComboBox.currentText())]})
        self.stackedWidget.setCurrentWidget(self.changeFilamentProgressPage)
        self.changeFilamentStatus.setText("Heating Tool {}, Please Wait...".format(str(self.activeExtruder)))
        self.changeFilamentNameOperation.setText("Loading {}".format(str(self.changeFilamentComboBox.currentText())))
        # this flag tells the updateTemperature function that runs every second to update the filament change progress bar as well, and to load or unload after heating done
        self.changeFilamentHeatingFlag = True
        self.loadFlag = True


    @run_async
    def changeFilamentLoadFunction(self):
        '''
        This function is called once the heating is done, which slowly moves the extruder so that it starts pulling filament
        '''
        self.stackedWidget.setCurrentWidget(self.changeFilamentLoadPage)
        while self.stackedWidget.currentWidget() == self.changeFilamentLoadPage:
            octopiclient.gcode("G91")
            octopiclient.gcode("G1 E5 F500")
            octopiclient.gcode("G90")
            time.sleep(self.calcExtrudeTime(5, 500))

    @run_async
    def changeFilamentExtrudePageFunction(self):
        '''
        once filament is loaded, this function is called to extrude filament till the toolhead
        '''
        self.stackedWidget.setCurrentWidget(self.changeFilamentExtrudePage)
        for i in range(int(ptfeTubeLength/150)):
            octopiclient.gcode("G91")
            octopiclient.gcode("G1 E150 F1500")
            octopiclient.gcode("G90")
            time.sleep(self.calcExtrudeTime(150, 1500))
            if self.stackedWidget.currentWidget() is not self.changeFilamentExtrudePage:
                break

        while self.stackedWidget.currentWidget() == self.changeFilamentExtrudePage:
            octopiclient.gcode("G91")
            octopiclient.gcode("G1 E20 F600")
            octopiclient.gcode("G90")
            time.sleep(self.calcExtrudeTime(20, 600))
    @run_async
    def changeFilamentRetractFunction(self):
        '''
        Remove the filament from the toolhead
        '''
        self.stackedWidget.setCurrentWidget(self.changeFilamentRetractPage)
        # Tip Shaping to prevent filament jamming in nozzle
        octopiclient.gcode("G91")
        octopiclient.gcode("G1 E10 F600")
        time.sleep(self.calcExtrudeTime(10, 600))
        octopiclient.gcode("G1 E-20 F2400")
        time.sleep(self.calcExtrudeTime(20, 2400))
        time.sleep(10) #wait for filament to cool inside the nozzle
        octopiclient.gcode("G1 E-150 F2400")
        time.sleep(self.calcExtrudeTime(150, 2400))
        octopiclient.gcode("G90")
        for i in range(int(ptfeTubeLength/150)):
            octopiclient.gcode("G91")
            octopiclient.gcode("G1 E-150 F1500")
            octopiclient.gcode("G90")
            time.sleep(self.calcExtrudeTime(150, 1500))
            if self.stackedWidget.currentWidget() is not self.changeFilamentRetractPage:
                break
											
        while self.stackedWidget.currentWidget() == self.changeFilamentRetractPage:
            octopiclient.gcode("G91")
            octopiclient.gcode("G1 E-5 F1000")
            octopiclient.gcode("G90")
            time.sleep(self.calcExtrudeTime(5, 1000))

    def changeFilament(self):
        time.sleep(1)
        if self.printerStatusText not in ["Printing","Paused"]:
            octopiclient.gcode("G28")

        self.stackedWidget.setCurrentWidget(self.changeFilamentPage)
        self.changeFilamentComboBox.clear()
        self.changeFilamentComboBox.addItems(filaments.keys())
        #Update
        print(self.tool0TargetTemperature)
        if self.tool0TargetTemperature  and self.printerStatusText in ["Printing","Paused"]:
            self.changeFilamentComboBox.addItem("Loaded Filament")
            index = self.changeFilamentComboBox.findText("Loaded Filament")
            if index >= 0 :
                self.changeFilamentComboBox.setCurrentIndex(index)

    def changeFilamentCancel(self):
        self.changeFilamentHeatingFlag = False
        self.firmwareUpdateCheck()
        self.coolDownAction()
        self.control()

    ''' +++++++++++++++++++++++++++++++++Job Operations+++++++++++++++++++++++++++++++ '''

    def stopActionMessageBox(self):
        '''
        Displays a message box asking if the user is sure if he wants to turn off the print
        '''
        if dialog.WarningYesNo(self, "Are you sure you want to stop the print?"):
            octopiclient.cancelPrint()

    def playPauseAction(self):
        '''
        Toggles Play/Pause of a print depending on the status of the print
        '''
        if self.printerStatusText == "Operational":
            if self.playPauseButton.isChecked:
                self.checkKlipperPrinterCFG()
                octopiclient.startPrint()
        elif self.printerStatusText == "Printing":
            octopiclient.pausePrint()
        elif self.printerStatusText == "Paused":
            octopiclient.pausePrint()

    def fileListLocal(self):
        '''
        Gets the file list from octoprint server, displays it on the list, as well as
        sets the stacked widget page to the file list page
        '''
        self.stackedWidget.setCurrentWidget(self.fileListLocalPage)
        files = []
        for file in octopiclient.retrieveFileInformation()['files']:
            if file["type"] == "machinecode":
                files.append(file)

        self.fileListWidget.clear()
        files.sort(key=lambda d: d['date'], reverse=True)
        # for item in [f['name'] for f in files] :
        #     self.fileListWidget.addItem(item)
        self.fileListWidget.addItems([f['name'] for f in files])
        self.fileListWidget.setCurrentRow(0)

    def fileListUSB(self):
        '''
        Gets the file list from octoprint server, displays it on the list, as well as
        sets the stacked widget page to the file list page
        ToDO: Add deapth of folders recursively get all gcodes
        '''
        self.stackedWidget.setCurrentWidget(self.fileListUSBPage)
        self.fileListWidgetUSB.clear()
        files = subprocess.Popen("ls /media/usb0 | grep gcode", stdout=subprocess.PIPE, shell=True).communicate()[0]
        files = files.decode('utf-8').split('\n')
        files = filter(None, files)
        # for item in files:
        #     self.fileListWidgetUSB.addItem(item)
        self.fileListWidgetUSB.addItems(files)
        self.fileListWidgetUSB.setCurrentRow(0)


    def printSelectedLocal(self):

        '''
        gets information about the selected file from octoprint server,
        as well as sets the current page to the print selected page.
        This function also selects the file to print from octoprint
        '''
        try:
            self.fileSelected.setText(self.fileListWidget.currentItem().text())
            self.stackedWidget.setCurrentWidget(self.printSelectedLocalPage)
            file = octopiclient.retrieveFileInformation(self.fileListWidget.currentItem().text())
            try:
                self.fileSizeSelected.setText(size(file['size']))
            except KeyError:
                self.fileSizeSelected.setText('-')
            try:
                self.fileDateSelected.setText(datetime.fromtimestamp(file['date']).strftime('%d/%m/%Y %H:%M:%S'))
            except KeyError:
                self.fileDateSelected.setText('-')
            try:
                m, s = divmod(file['gcodeAnalysis']['estimatedPrintTime'], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                self.filePrintTimeSelected.setText("%dd:%dh:%02dm:%02ds" % (d, h, m, s))
            except KeyError:
                self.filePrintTimeSelected.setText('-')
            try:
                self.filamentVolumeSelected.setText(
                    ("%.2f cm" % file['gcodeAnalysis']['filament']['tool0']['volume']) + chr(179))
            except KeyError:
                self.filamentVolumeSelected.setText('-')

            try:
                self.filamentLengthFileSelected.setText(
                    "%.2f mm" % file['gcodeAnalysis']['filament']['tool0']['length'])
            except KeyError:
                self.filamentLengthFileSelected.setText('-')
            # uncomment to select the file when selectedd in list
            # octopiclient.selectFile(self.fileListWidget.currentItem().text(), False)
            self.stackedWidget.setCurrentWidget(self.printSelectedLocalPage)

            '''
            If image is available from server, set it, otherwise display default image
            '''
            self.displayThumbnail(self.printPreviewSelected, str(self.fileListWidget.currentItem().text()), usb=False)

        except:
            print ("Log: Nothing Selected")
            # Set image fot print preview:
            # self.printPreviewSelected.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))
            # print self.fileListWidget.currentItem().text().replace(".gcode","")
            # self.printPreviewSelected.setPixmap(QtGui.QPixmap(_fromUtf8("/home/pi/.octoprint/uploads/{}.png".format(self.FileListWidget.currentItem().text().replace(".gcode","")))))

            # Check if the PNG file exists, and if it does display it, or diplay a default picture.

    def printSelectedUSB(self):
        '''
        Sets the screen to the print selected screen for USB, on which you can transfer to local drive and view preview image.
        :return:
        '''
        try:
            self.fileSelectedUSBName.setText(self.fileListWidgetUSB.currentItem().text())
            self.stackedWidget.setCurrentWidget(self.printSelectedUSBPage)
            self.displayThumbnail(self.printPreviewSelectedUSB, '/media/usb0/' + str(self.fileListWidgetUSB.currentItem().text()), usb=True)
        except:
            print ("Log: Nothing Selected")

            # Set Image from USB

    def transferToLocal(self, prnt=False):
        '''
        Transfers a file from USB mounted at /media/usb0 to octoprint's watched folder so that it gets automatically detected bu Octoprint.
        Warning: If the file is read-only, octoprint API for reading the file crashes.
        '''

        file = '/media/usb0/' + str(self.fileListWidgetUSB.currentItem().text())

        self.uploadThread = ThreadFileUpload(file, prnt=prnt)
        self.uploadThread.start()
        if prnt:
            self.stackedWidget.setCurrentWidget(self.homePage)

    def printFile(self):
        '''
        Prints the file selected from printSelected()
        '''
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.selectFile(self.fileListWidget.currentItem().text(), True)
        # octopiclient.startPrint()
        self.checkKlipperPrinterCFG()
        self.stackedWidget.setCurrentWidget(self.homePage)


    def deleteItem(self):
        '''
        Deletes a gcode file, and if associates, its image file from the memory
        '''
        octopiclient.deleteFile(self.fileListWidget.currentItem().text())
        octopiclient.deleteFile(self.fileListWidget.currentItem().text().replace(".gcode", ".png"))
        # delete PNG also
        self.fileListLocal()


    def getImageFromGcode(self,gcodeLocation):
        '''
        Gets the image from the gcode text file
        '''
        with open(gcodeLocation, 'rb') as f:
            content = f.readlines()[:500]
            content = b''.join(content)
        start = content.find(b'; thumbnail begin')
        end = content.find(b'; thumbnail end')
        if start != -1 and end != -1:
            thumbnail = content[start:end]
            thumbnail = base64.b64decode(thumbnail[thumbnail.find(b'\n') + 1:].replace(b'; ', b'').replace(b'\r\n', b''))
            return thumbnail
        else:
            return False

    @run_async
    def displayThumbnail(self,labelObject,fileLocation, usb=False):
        '''
        Displays the image on the label object
        :param labelObject: QLabel object to display the image
        :param img: image to display
        '''
        try:
            pixmap = QtGui.QPixmap()
            if usb:
                img = self.getImageFromGcode(fileLocation)
            else:
                img = octopiclient.getImage(fileLocation)
            if img:
                pixmap.loadFromData(img)
                labelObject.setPixmap(pixmap)
            else:
                labelObject.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))
        except:
            labelObject.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))

    ''' +++++++++++++++++++++++++++++++++Printer Status+++++++++++++++++++++++++++++++ '''

    def updateTemperature(self, temperature):
        '''
        Slot that gets a signal originating from the thread that keeps polling for printer status
        runs at 1HZ, so do things that need to be constantly updated only. This also controls the cooling fan depending on the temperatures
        :param temperature: dict containing key:value pairs with keys being the tools, bed and their values being their corresponding temperratures
        '''
        try:
            if temperature['tool0Target'] == 0:
                self.tool0TempBar.setMaximum(300)
                self.tool0TempBar.setStyleSheet(styles.bar_heater_cold)
            elif temperature['tool0Actual'] <= temperature['tool0Target']:
                self.tool0TempBar.setMaximum(temperature['tool0Target'])
                self.tool0TempBar.setStyleSheet(styles.bar_heater_heating)
            else:
                self.tool0TempBar.setMaximum(temperature['tool0Actual'])
            self.tool0TempBar.setValue(temperature['tool0Actual'])
            self.tool0ActualTemperature.setText(str(int(temperature['tool0Actual'])))  # + unichr(176)
            self.tool0TargetTemperature.setText(str(int(temperature['tool0Target'])))

            if temperature['tool1Target'] == 0:
                self.tool1TempBar.setMaximum(300)
                self.tool1TempBar.setStyleSheet(styles.bar_heater_cold)
            elif temperature['tool1Actual'] <= temperature['tool1Target']:
                self.tool1TempBar.setMaximum(temperature['tool1Target'])
                self.tool1TempBar.setStyleSheet(styles.bar_heater_heating)
            else:
                self.tool1TempBar.setMaximum(temperature['tool1Actual'])
            self.tool1TempBar.setValue(temperature['tool1Actual'])
            self.tool1ActualTemperature.setText(str(int(temperature['tool1Actual'])))  # + unichr(176)
            self.tool1TargetTemperature.setText(str(int(temperature['tool1Target'])))

            if temperature['bedTarget'] == 0:
                self.bedTempBar.setMaximum(150)
                self.bedTempBar.setStyleSheet(styles.bar_heater_cold)
            elif temperature['bedActual'] <= temperature['bedTarget']:
                self.bedTempBar.setMaximum(temperature['bedTarget'])
                self.bedTempBar.setStyleSheet(styles.bar_heater_heating)
            else:
                self.bedTempBar.setMaximum(temperature['bedActual'])
            self.bedTempBar.setValue(temperature['bedActual'])
            self.bedActualTemperatute.setText(str(int(temperature['bedActual'])))  # + unichr(176))
            self.bedTargetTemperature.setText(str(int(temperature['bedTarget'])))  # + unichr(176))

        except:
            pass

        # updates the progress bar on the change filament screen
        if self.changeFilamentHeatingFlag:
            if self.activeExtruder == 0:
                if temperature['tool0Target'] == 0:
                    self.changeFilamentProgress.setMaximum(300)
                elif temperature['tool0Target'] - temperature['tool0Actual'] > 1:
                    self.changeFilamentProgress.setMaximum(temperature['tool0Target'])
                else:
                    self.changeFilamentProgress.setMaximum(temperature['tool0Actual'])
                    self.changeFilamentHeatingFlag = False
                    if self.loadFlag:
                        self.changeFilamentLoadFunction()
                        #self.stackedWidget.setCurrentWidget(self.changeFilamentExtrudePage)
                    else:
                        #self.stackedWidget.setCurrentWidget(self.changeFilamentRetractPage)
                        octopiclient.extrude(5)     # extrudes some amount of filament to prevent plugging
                        self.changeFilamentRetractFunction()

                self.changeFilamentProgress.setValue(temperature['tool0Actual'])
            elif self.activeExtruder == 1:
                if temperature['tool1Target'] == 0:
                    self.changeFilamentProgress.setMaximum(300)
                elif temperature['tool1Target'] - temperature['tool1Actual'] > 1:
                    self.changeFilamentProgress.setMaximum(temperature['tool1Target'])
                else:
                    self.changeFilamentProgress.setMaximum(temperature['tool1Actual'])
                    self.changeFilamentHeatingFlag = False
                    if self.loadFlag:
                        self.changeFilamentLoadFunction()
                        #self.stackedWidget.setCurrentWidget(self.changeFilamentExtrudePage)
                    else:
                        #self.stackedWidget.setCurrentWidget(self.changeFilamentRetractPage)
                        octopiclient.extrude(5)     # extrudes some amount of filament to prevent plugging
                        self.changeFilamentRetractFunction()

                self.changeFilamentProgress.setValue(temperature['tool1Actual'])

    def updatePrintStatus(self, file):
        '''
        displays infromation of a particular file on the home page,is a slot for the signal emited from the thread that keeps pooling for printer status
        runs at 1HZ, so do things that need to be constantly updated only
        :param file: dict of all the attributes of a particualr file
        '''
        if file is None:
            self.currentFile = None
            self.currentImage = None
            self.timeLeft.setText("-")
            self.fileName.setText("-")
            self.printProgressBar.setValue(0)
            self.printTime.setText("-")
            self.playPauseButton.setDisabled(True)  # if file available, make play buttom visible

        else:
            self.playPauseButton.setDisabled(False)  # if file available, make play buttom visible
            self.fileName.setText(file['job']['file']['name'])
            self.currentFile = file['job']['file']['name']
            if file['progress']['printTime'] is None:
                self.printTime.setText("-")
            else:
                m, s = divmod(file['progress']['printTime'], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                self.printTime.setText("%d:%d:%02d:%02d" % (d, h, m, s))

            if file['progress']['printTimeLeft'] is None:
                self.timeLeft.setText("-")
            else:
                m, s = divmod(file['progress']['printTimeLeft'], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                self.timeLeft.setText("%d:%d:%02d:%02d" % (d, h, m, s))

            if file['progress']['completion'] is None:
                self.printProgressBar.setValue(0)
            else:
                self.printProgressBar.setValue(file['progress']['completion'])

            '''
            If image is available from server, set it, otherwise display default image.
            If the image was already loaded, dont load it again.
            '''
            if self.currentImage != self.currentFile:
                self.currentImage = self.currentFile
                self.displayThumbnail(self.printPreviewMain, self.currentFile, usb=False)

    def updateStatus(self, status):
        '''
        Updates the status bar, is a slot for the signal emited from the thread that constantly polls for printer status
        this function updates the status bar, as well as enables/disables relavent buttons
        :param status: String of the status text
        '''

        self.printerStatusText = status
        self.printerStatus.setText(status)

        if status == "Printing":  # Green
            self.printerStatusColour.setStyleSheet(styles.printer_status_green)
        elif status == "Offline":  # Red
            self.printerStatusColour.setStyleSheet(styles.printer_status_red)
        elif status == "Paused":  # Amber
            self.printerStatusColour.setStyleSheet(styles.printer_status_amber)
        elif status == "Operational":  # Amber
            self.printerStatusColour.setStyleSheet(styles.printer_status_blue)

        '''
        Depending on Status, enable and Disable Buttons
        '''
        if status == "Printing":
            self.playPauseButton.setChecked(True)
            self.stopButton.setDisabled(False)
            self.motionTab.setDisabled(True)
            self.changeFilamentButton.setDisabled(True)
            self.menuCalibrateButton.setDisabled(True)
            self.menuPrintButton.setDisabled(True)
            self.doorLockButton.setDisabled(False)
            # if not self.__timelapse_enabled:
            #     octopiclient.cancelPrint()
            #     self.coolDownAction()

        elif status == "Paused":
            self.playPauseButton.setChecked(False)
            self.stopButton.setDisabled(False)
            self.motionTab.setDisabled(False)
            self.changeFilamentButton.setDisabled(False)
            self.menuCalibrateButton.setDisabled(True)
            self.menuPrintButton.setDisabled(True)
            self.doorLockButton.setDisabled(False)


        else:
            self.stopButton.setDisabled(True)
            self.playPauseButton.setChecked(False)
            self.motionTab.setDisabled(False)
            self.changeFilamentButton.setDisabled(False)
            self.menuCalibrateButton.setDisabled(False)
            self.menuPrintButton.setDisabled(False)
            self.doorLockButton.setDisabled(True)

    ''' ++++++++++++++++++++++++++++Active Extruder/Tool Change++++++++++++++++++++++++ '''

    def selectToolChangeFilament(self):
        '''
        Selects the tool whose temperature needs to be changed. It accordingly changes the button text. it also updates the status of the other toggle buttons
        '''

        if self.toolToggleChangeFilamentButton.isChecked():
            self.setActiveExtruder(1)
            octopiclient.selectTool(1)
            time.sleep(1)

        else:
            self.setActiveExtruder(0)
            octopiclient.selectTool(0)
            time.sleep(1)


    def selectToolMotion(self):
        '''
        Selects the tool whose temperature needs to be changed. It accordingly changes the button text. it also updates the status of the other toggle buttons
        '''

        if self.toolToggleMotionButton.isChecked():
            self.setActiveExtruder(1)
            octopiclient.selectTool(1)

        else:
            self.setActiveExtruder(0)
            octopiclient.selectTool(0)

    def selectToolTemperature(self):
        '''
        Selects the tool whose temperature needs to be changed. It accordingly changes the button text.it also updates the status of the other toggle buttons
        '''
        # self.toolToggleTemperatureButton.setText(
        #     "1") if self.toolToggleTemperatureButton.isChecked() else self.toolToggleTemperatureButton.setText("0")
        if self.toolToggleTemperatureButton.isChecked():
            print ("extruder 1 Temperature")
            self.toolTempSpinBox.setProperty("value", float(self.tool1TargetTemperature.text()))
        else:
            print ("extruder 0 Temperature")
            self.toolTempSpinBox.setProperty("value", float(self.tool0TargetTemperature.text()))

    def setActiveExtruder(self, activeNozzle):
        activeNozzle = int(activeNozzle)
        if activeNozzle == 0:
            self.tool0Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/activeNozzle.png")))
            self.tool1Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/Nozzle.png")))
            self.toolToggleChangeFilamentButton.setChecked(False)
            # self.toolToggleChangeFilamentButton.setText("0")
            self.toolToggleMotionButton.setChecked(False)
            self.toolToggleMotionButton.setText("0")
            self.activeExtruder = 0
        elif activeNozzle == 1:
            self.tool0Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/Nozzle.png")))
            self.tool1Label.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/activeNozzle.png")))
            self.toolToggleChangeFilamentButton.setChecked(True)
            # self.toolToggleChangeFilamentButton.setText("1")
            self.toolToggleMotionButton.setChecked(True)
            self.toolToggleMotionButton.setText("1")
            self.activeExtruder = 1

            # set button states
            # set octoprint if mismatch

    ''' +++++++++++++++++++++++++++++++++Control Screen+++++++++++++++++++++++++++++++ '''

    def control(self):
        self.stackedWidget.setCurrentWidget(self.controlPage)
        if self.toolToggleTemperatureButton.isChecked():
            self.toolTempSpinBox.setProperty("value", float(self.tool1TargetTemperature.text()))
        else:
            self.toolTempSpinBox.setProperty("value", float(self.tool0TargetTemperature.text()))
        self.bedTempSpinBox.setProperty("value", float(self.bedTargetTemperature.text()))

    def setStep(self, stepRate):
        '''
        Sets the class variable "Step" which would be needed for movement and joging
        :param step: step multiplier for movement in the move
        :return: nothing
        '''

        if stepRate == 100:
            self.step100Button.setFlat(True)
            self.step1Button.setFlat(False)
            self.step10Button.setFlat(False)
            self.step = 100
        if stepRate == 1:
            self.step100Button.setFlat(False)
            self.step1Button.setFlat(True)
            self.step10Button.setFlat(False)
            self.step = 1
        if stepRate == 10:
            self.step100Button.setFlat(False)
            self.step1Button.setFlat(False)
            self.step10Button.setFlat(True)
            self.step = 10

    def setToolTemp(self):
        if self.toolToggleTemperatureButton.isChecked():
            octopiclient.gcode(command='M104 T1 S' + str(self.toolTempSpinBox.value()))
            # octopiclient.setToolTemperature({"tool1": self.toolTempSpinBox.value()})
        else:
            octopiclient.gcode(command='M104 T0 S' + str(self.toolTempSpinBox.value()))
            # octopiclient.setToolTemperature({"tool0": self.toolTempSpinBox.value()})

    def preheatToolTemp(self, temp):
        if self.toolToggleTemperatureButton.isChecked():
            octopiclient.gcode(command='M104 T1 S' + str(temp))
        else:
            octopiclient.gcode(command='M104 T0 S' + str(temp))
        self.toolTempSpinBox.setProperty("value", temp)

    def preheatBedTemp(self, temp):
        octopiclient.gcode(command='M140 S' + str(temp))
        self.bedTempSpinBox.setProperty("value", temp)

    def coolDownAction(self):
        ''''
        Turns all heaters and fans off
        '''
        octopiclient.gcode(command='M107')
        octopiclient.setToolTemperature({"tool0": 0, "tool1": 0})
        # octopiclient.setToolTemperature({"tool0": 0})
        octopiclient.setBedTemperature(0)
        self.toolTempSpinBox.setProperty("value", 0)
        self.bedTempSpinBox.setProperty("value", 0)

    ''' +++++++++++++++++++++++++++++++++++Calibration++++++++++++++++++++++++++++++++ '''
    def setZToolOffset(self, offset, setOffset=False):
        '''
        Sets the home offset after the caliberation wizard is done, which is a callback to
        the response of M114 that is sent at the end of the Wizard in doneStep()
        :param offset: the value off the offset to set. is a str is coming from M114, and is float if coming from the nozzleOffsetPage
        :param setOffset: Boolean, is true if the function call is from the nozzleOFfsetPage
        :return:

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''
        self.currentZPosition = offset #gets the current z position, used to set new tool offsets.
        # clean this shit up.
        #fuck you past vijay for not cleaning this up
        try:
            if self.setNewToolZOffsetFromCurrentZBool:
                print(self.toolOffsetZ)
                print(self.currentZPosition)
                newToolOffsetZ = (float(self.toolOffsetZ) + float(self.currentZPosition))
                octopiclient.gcode(command='M218 T1 Z{}'.format(newToolOffsetZ))  # restore eeprom settings to get Z home offset, mesh bed leveling back
                self.setNewToolZOffsetFromCurrentZBool =False
                octopiclient.gcode(command='SAVE_CONFIG')  # store eeprom settings to get Z home offset, mesh bed leveling back
        except Exception as e:
                    print("error: " + str(e))

    def showProbingFailed(self,msg='Probing Failed, Calibrate bed again or check for hardware issue',overlay=True):
        if dialog.WarningOk(self, msg, overlay=overlay):
            octopiclient.cancelPrint()
            return True
        return False

    def showPrinterError(self,msg='Printer error, Check Terminal',overlay=False): #True
        if dialog.WarningOk(self, msg, overlay=overlay):
            pass
            return True
        return False

    def updateEEPROMProbeOffset(self, offset):
        '''
        Sets the spinbox value to have the value of the Z offset from the printer.
        the value is -ve so as to be more intuitive.
        :param offset:
        :return:
        '''
        self.currentNozzleOffset.setText(str(float(offset)))
        self.nozzleOffsetDoubleSpinBox.setValue(0)


    def setZProbeOffset(self, offset):
        '''
        Sets Z Probe offset from spinbox

        #TODO can make this simpler, asset the offset value to string float to begin with instead of doing confitionals
        '''

        octopiclient.gcode(command='M851 Z{}'.format(round(float(offset),2))) #M851 only ajusts nozzle offset
        self.nozzleOffsetDoubleSpinBox.setValue(0)
        _offset=float(self.currentNozzleOffset.text())+float(offset)
        self.currentNozzleOffset.setText(str(float(self.currentNozzleOffset.text())-float(offset))) # show nozzle offset after adjustment
        octopiclient.gcode(command='M500')

    def requestEEPROMProbeOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)

    def nozzleOffset(self):
        '''
        Updates the value of M206 Z in the nozzle offset spinbox. Sends M503 so that the pritner returns the value as a websocket calback
        :return:
        '''
        octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.nozzleOffsetPage)

    def updateToolOffsetXY(self):
        octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.toolOffsetXYPage)

    def updateToolOffsetZ(self):
        octopiclient.gcode(command='M503')
        self.stackedWidget.setCurrentWidget(self.toolOffsetZpage)

    def setToolOffsetX(self):
        octopiclient.gcode(command='M218 T1 X{}'.format(round(self.toolOffsetXDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        octopiclient.gcode(command='M500')

    def setToolOffsetY(self):
        octopiclient.gcode(command='M218 T1 Y{}'.format(round(self.toolOffsetYDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        octopiclient.gcode(command='M500')
        octopiclient.gcode(command='M500')

    def setToolOffsetZ(self):
        octopiclient.gcode(command='M218 T1 Z{}'.format(round(self.toolOffsetZDoubleSpinBox.value(),2)))  # restore eeprom settings to get Z home offset, mesh bed leveling back
        octopiclient.gcode(command='M500')

    def getToolOffset(self, M218Data):

        #if float(M218Data[M218Data.index('X') + 1:].split(' ', 1)[0] ) > 0:
        self.toolOffsetZ = M218Data[M218Data.index('Z') + 1:].split(' ', 1)[0]
        self.toolOffsetX = M218Data[M218Data.index('X') + 1:].split(' ', 1)[0]
        self.toolOffsetY = M218Data[M218Data.index('Y') + 1:].split(' ', 1)[0]
        self.toolOffsetXDoubleSpinBox.setValue(float(self.toolOffsetX))
        self.toolOffsetYDoubleSpinBox.setValue(float(self.toolOffsetY))
        self.toolOffsetZDoubleSpinBox.setValue(float(self.toolOffsetZ))
        self.idexToolOffsetRestoreValue = float(self.toolOffsetZ)

	

    def quickStep1(self):
        '''
        Shows welcome message.
        Homes to MAX
        goes to position where leveling screws can be opened
        :return:
        '''
        self.toolZOffsetCaliberationPageCount = 0
        octopiclient.gcode(command='M104 S200')
        octopiclient.gcode(command='M104 T1 S200')
        #octopiclient.gcode(command='M211 S0')  # Disable software endstop
        octopiclient.gcode(command='T0')  # Set active tool to t0
        octopiclient.gcode(command='M503')  # makes sure internal value of Z offset and Tool offsets are stored before erasing
        octopiclient.gcode(command='M420 S0')  # Dissable mesh bed leveling for good measure
        self.stackedWidget.setCurrentWidget(self.quickStep1Page)
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.gcode(command='T0')
        octopiclient.jog(x=40, y=40, absolute=True, speed=2000)

    def quickStep2(self):
        '''
        levels first position (RIGHT)
        :return:
        '''
        self.stackedWidget.setCurrentWidget(self.quickStep2Page)
        octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    def quickStep3(self):
        '''
        levels second leveling position (LEFT)
        '''
        self.stackedWidget.setCurrentWidget(self.quickStep3Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    def quickStep4(self):
        '''
        levels third leveling position  (BACK)
        :return:
        '''
        # sent twice for some reason
        self.stackedWidget.setCurrentWidget(self.quickStep4Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.jog(x=calibrationPosition['X3'], y=calibrationPosition['Y3'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    # def quickStep5(self):
    #     '''
    #     Nozzle Z offset calc
    #     '''
    #     self.stackedWidget.setCurrentWidget(self.quickStep5Page)
    #     octopiclient.jog(z=15, absolute=True, speed=1500)
    #     octopiclient.gcode(command='M272 S')

    def nozzleHeightStep1(self):
        if self.toolZOffsetCaliberationPageCount == 0 :
            self.toolZOffsetLabel.setText("Move the bed up or down to the First Nozzle , testing height using paper")
            self.stackedWidget.setCurrentWidget(self.nozzleHeightStep1Page)
            octopiclient.jog(z=10, absolute=True, speed=1500)
            octopiclient.jog(x=calibrationPosition['X4'], y=calibrationPosition['Y4'], absolute=True, speed=10000)
            octopiclient.jog(z=1, absolute=True, speed=1500)
            self.toolZOffsetCaliberationPageCount = 1
        elif self.toolZOffsetCaliberationPageCount == 1:
            self.toolZOffsetLabel.setText("Move the bed up or down to the Second Nozzle , testing height using paper")
            octopiclient.gcode(command='G92 Z0')#set the current Z position to zero
            octopiclient.jog(z=1, absolute=True, speed=1500)
            octopiclient.gcode(command='T1')
            octopiclient.jog(x=calibrationPosition['X4'], y=calibrationPosition['Y4'], absolute=True, speed=10000)
            self.toolZOffsetCaliberationPageCount = 2
        else:
            self.doneStep()

    def doneStep(self):
        '''
        Exits leveling
        :return:
        '''
        self.setNewToolZOffsetFromCurrentZBool = True
        octopiclient.gcode(command='M114')
        octopiclient.jog(z=4, absolute=True, speed=1500)
        octopiclient.gcode(command='T0')
        #octopiclient.gcode(command='M211 S1')  # Disable software endstop
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.gcode(command='M104 S0')
        octopiclient.gcode(command='M104 T1 S0')
        octopiclient.gcode(command='M84')
        octopiclient.gcode(command='M500')  # store eeprom settings to get Z home offset, mesh bed leveling back

    def cancelStep(self):
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.gcode(command='M104 S0')
        octopiclient.gcode(command='M104 T1 S0')
        octopiclient.gcode(command='M84')

    
    def testPrint(self,tool0Diameter,tool1Diameter,gcode):
        '''
        Prints a test print
        :param tool0Diameter: Diameter of tool 0 nozzle.04,06 or 08
        :param tool1Diameter: Diameter of tool 1 nozzle.40,06 or 08
        :param gcode: type of gcode to print, dual nozzle calibration, bed leveling, movement or samaple prints in
        single and dual. bedLevel, dualCalibration, movementTest, dualTest, singleTest
        :return:
        '''
        try:
            if gcode == 'bedLevel':
                self.printFromPath('gcode/' + tool0Diameter + '_BedLeveling.gcode', True)
            elif gcode == 'dualCalibration':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_dual_extruder_calibration_Idex.gcode',
                    True)
            elif gcode == 'movementTest':
                self.printFromPath('gcode/movementTest.gcode', True)
            elif gcode == 'dualTest':
                self.printFromPath(
                    'gcode/' + tool0Diameter + '_' + tool1Diameter + '_Fracktal_logo_Idex.gcode',
                    True)
            elif gcode == 'singleTest':
                self.printFromPath('gcode/' + tool0Diameter + '_Fracktal_logo_Idex.gcode',True)

            else:
                print("gcode not found")
        except Exception as e:
            print("Eror:" + e)
    def printFromPath(self,path,prnt=True):
        '''
        Transfers a file from a specific to octoprint's watched folder so that it gets automatically detected by Octoprint.
        Warning: If the file is read-only, octoprint API for reading the file crashes.
        '''

        self.uploadThread = ThreadFileUpload(path, prnt=prnt)
        self.uploadThread.start()
        if prnt:
            self.stackedWidget.setCurrentWidget(self.homePage)


    ''' +++++++++++++++++++++++++++++++++++IDEX Config++++++++++++++++++++++++++++++++ '''


    def idexConfigStep1(self):
        '''
        Shows welcome message.
        Welcome Page, Give Info. Unlock nozzle and push down
        :return:
        '''
        octopiclient.gcode(command='M503')  # Gets old tool offset position
        octopiclient.gcode(command='M218 T1 Z0')  # set nozzle tool offsets to 0
        octopiclient.gcode(command='M104 S200')
        octopiclient.gcode(command='M104 T1 S200')
        octopiclient.home(['x', 'y', 'z'])
        octopiclient.gcode(command='G1 X10 Y10 Z20 F5000')
        octopiclient.gcode(command='T0')  # Set active tool to t0
        octopiclient.gcode(command='M420 S0')  # Dissable mesh bed leveling for good measure
        self.stackedWidget.setCurrentWidget(self.idexConfigStep1Page)
    def idexConfigStep2(self):
        '''
        levels first position (RIGHT)
        :return:
        '''
        self.stackedWidget.setCurrentWidget(self.idexConfigStep2Page)
        octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    def idexConfigStep3(self):
        '''
        levels second leveling position (LEFT)
        '''
        self.stackedWidget.setCurrentWidget(self.idexConfigStep3Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.jog(x=calibrationPosition['X2'], y=calibrationPosition['Y2'], absolute=True, speed=10000)
        octopiclient.jog(z=0, absolute=True, speed=1500)

    def idexConfigStep4(self):
        '''
        Set to Mirror mode and asks to loosen the carriage, push both doen to max
        :return:
        '''
        # sent twice for some reason
        self.stackedWidget.setCurrentWidget(self.idexConfigStep4Page)
        octopiclient.jog(z=10, absolute=True, speed=1500)
        octopiclient.gcode(command='M605 S3')
        octopiclient.jog(x=calibrationPosition['X1'], y=calibrationPosition['Y1'], absolute=True, speed=10000)

    def idexConfigStep5(self):
        '''
        take bed up until both nozzles touch the bed. ASk to take nozzle up and down till nozzle just rests on the bed and tighten
        :return:
        '''
        # sent twice for some reason
        self.stackedWidget.setCurrentWidget(self.idexConfigStep5Page)
        octopiclient.jog(z=1, absolute=True, speed=10000)


    def idexDoneStep(self):
        '''
        Exits leveling
        :return:
        '''
        octopiclient.jog(z=4, absolute=True, speed=1500)
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        octopiclient.home(['z'])
        octopiclient.home(['x', 'y'])
        octopiclient.gcode(command='M104 S0')
        octopiclient.gcode(command='M104 T1 S0')
        octopiclient.gcode(command='M605 S1')
        octopiclient.gcode(command='M218 T1 Z0') #set nozzle offsets to 0
        octopiclient.gcode(command='M84')
        octopiclient.gcode(command='M500')  # store eeprom settings to get Z home offset, mesh bed leveling back

    def idexCancelStep(self):
        self.stackedWidget.setCurrentWidget(self.calibratePage)
        octopiclient.gcode(command='M605 S1')
        octopiclient.home(['z'])
        octopiclient.home(['x', 'y'])
        octopiclient.gcode(command='M104 S0')
        octopiclient.gcode(command='M104 T1 S0')
        octopiclient.gcode(command='M218 T1 Z{}'.format(self.idexToolOffsetRestoreValue))
        octopiclient.gcode(command='M84')


    ''' +++++++++++++++++++++++++++++++++++Keyboard++++++++++++++++++++++++++++++++ '''

    def startKeyboard(self, returnFn, onlyNumeric=False, noSpace=False, text=""):
        '''
        starts the keyboard screen for entering Password
        '''
        keyBoardobj = keyboard.Keyboard(onlyNumeric=onlyNumeric, noSpace=noSpace, text=text)
        keyBoardobj.keyboard_signal.connect(returnFn)
        keyBoardobj.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        keyBoardobj.show()

    ''' ++++++++++++++++++++++++++++++Restore Defaults++++++++++++++++++++++++++++ '''

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
            os.system('sudo cp -f firmware/GCodes.cfg /home/pi/GCodes.cfg')
            print("copied Gcodes")
            os.system('sudo cp -f firmware/IDEX_mode.cfg /home/pi/IDEX_mode.cfg')
            print("copied idex mode")
            os.system('sudo cp -f firmware/printer.cfg /home/pi/printer.cfg')
            print("copied printer cfg")
            os.system('sudo cp -f firmware/variables.cfg /home/pi/variables.cfg')
            print("copied variables")
            octopiclient.gcode(command='M502')
            octopiclient.gcode(command='M500')
            octopiclient.gcode(command='FIRMWARE_RESTART')

    ''' +++++++++++++++++++++++++++++++++++ Misc ++++++++++++++++++++++++++++++++ '''

    def tellAndReboot(self, msg="Rebooting...", overlay=True):
        if dialog.WarningOk(self, msg, overlay=overlay):
            os.system('sudo reboot now')
            return True
        return False

    def askAndReboot(self, msg="Are you sure you want to reboot?", overlay=True):
        if dialog.WarningYesNo(self, msg, overlay=overlay):
            os.system('sudo reboot now')
            return True
        return False

    def checkKlipperPrinterCFG(self):
        '''
        Checks for valid printer.cfg and restores if needed
        '''

        # Open the printer.cfg file:
        try:
            with open('/home/pi/printer.cfg', 'r') as currentConfigFile:
                currentConfig = currentConfigFile.read()
                if "# MCU Config" in currentConfig:
                    configCorruptedFlag = False
                    print("Printer Config File OK")
                else:
                    configCorruptedFlag = True
                    print("Printer Config File Corrupted")
        except:
            configCorruptedFlag = True
            print("Printer Config File Not Found")

        if configCorruptedFlag:
            backupFiles = sorted(glob.glob('/home/pi/printer-*.cfg'), key=os.path.getmtime, reverse=True)
            print("\n".join(backupFiles))
            for backupFile in backupFiles:
                with open(str(backupFile), 'r') as backupConfigFile:
                    backupConfig = backupConfigFile.read()
                    if "# MCU Config" in backupConfig:
                        try:
                            os.remove('/home/pi/printer.cfg')
                        except:
                            print("Files does not exist for deletion")
                        try:
                            os.rename(backupFile, '/home/pi/printer.cfg')
                            print("Printer Config File Restored")
                            return()
                        except:
                            pass
            # If no valid backups found, show error dialog:
            dialog.WarningOk(self, "Printer Config File corrupted. Contact Fracktal support or raise a ticket at care.fracktal.in")
            print("Printer Config File corrupted. Contact Fracktal support or raise a ticket at care.fracktal.in")
            if self.printerStatus == "Printing":
                octopiclient.cancelPrint()
                self.coolDownAction()
        elif not configCorruptedFlag:
            backupFiles = sorted(glob.glob('/home/pi/printer-*.cfg'), key=os.path.getmtime, reverse=True)
            try:
                for backupFile in backupFiles[5:]:
                    os.remove(backupFile)
            except:
                pass

    def pairPhoneApp(self):
        if getIP(ThreadRestartNetworking.ETH) is not None:
            qrip = getIP(ThreadRestartNetworking.ETH)
        elif getIP(ThreadRestartNetworking.WLAN) is not None:
            qrip = getIP(ThreadRestartNetworking.WLAN)
        else:
            if dialog.WarningOk(self, "Network Disconnected"):
                return
        self.QRCodeLabel.setPixmap(
            qrcode.make("http://"+ qrip, image_factory=Image).pixmap())
        self.stackedWidget.setCurrentWidget(self.QRCodePage)

