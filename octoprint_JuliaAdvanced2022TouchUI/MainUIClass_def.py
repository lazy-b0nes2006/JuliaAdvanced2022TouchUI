from PyQt5 import QtWidgets, QtGui
import mainGUI
from config import Development, _fromUtf8
import logging
from threads import *
import styles
from socket_qt import QtWebsocket

from gui_elements import ClickableLineEdit

from decorators import load_and_assign_functions

class MainUIClass(QtWidgets.QMainWindow, mainGUI.Ui_MainWindow):
    
    def __init__(self):
        '''
        This method gets called when an object of type MainUIClass is defined
        '''
        super(MainUIClass, self).__init__()
        load_and_assign_functions('mainUI_class_functions', MainUIClass)
        if not Development:
            formatter = logging.Formatter("%(asctime)s %(message)s")
            self._logger = logging.getLogger("TouchUI")
            file_handler = logging.FileHandler("/home/pi/ui.log")
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


            for spinbox in self.findChildren(QtWidgets.QSpinBox):
                lineEdit = spinbox.lineEdit()
                lineEdit.setReadOnly(True)
                lineEdit.setDisabled(True)
                p = lineEdit.palette()
                p.setColor(QtGui.QPalette.Highlight, QtGui.QColor(40, 40, 40))
                lineEdit.setPalette(p)


        except Exception as e:
            self._logger.error(e)

    def setupUi(self, MainWindow):
        super(MainUIClass, self).setupUi(MainWindow)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Gotham"))
        font.setPointSize(15)

        self.wifiPasswordLineEdit = ClickableLineEdit(self.wifiSettingsPage)
        self.wifiPasswordLineEdit.setGeometry(QtCore.QRect(0, 170, 480, 60))
        self.wifiPasswordLineEdit.setFont(font)
        self.wifiPasswordLineEdit.setStyleSheet(styles.textedit)
        self.wifiPasswordLineEdit.setObjectName(_fromUtf8("wifiPasswordLineEdit"))

        font.setPointSize(11)
        self.ethStaticIpLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.ethStaticIpLineEdit.setGeometry(QtCore.QRect(120, 10, 300, 30))
        self.ethStaticIpLineEdit.setFont(font)
        self.ethStaticIpLineEdit.setStyleSheet(styles.textedit)
        self.ethStaticIpLineEdit.setObjectName(_fromUtf8("ethStaticIpLineEdit"))

        self.ethStaticGatewayLineEdit = ClickableLineEdit(self.ethStaticSettings)
        self.ethStaticGatewayLineEdit.setGeometry(QtCore.QRect(120, 60, 300, 30))
        self.ethStaticGatewayLineEdit.setFont(font)
        self.ethStaticGatewayLineEdit.setStyleSheet(styles.textedit)
        self.ethStaticGatewayLineEdit.setObjectName(_fromUtf8("ethStaticGatewayLineEdit"))

        self.menuCartButton.setDisabled(True)

        self.movie = QtGui.QMovie("templates/img/loading.gif")
        self.loadingGif.setMovie(self.movie)
        self.movie.start()

    def proceed(self):
        '''
        Startes websocket, as well as initialises button actions and callbacks. THis is done in such a manner so that the callbacks that dnepend on websockets
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

    def setActions(self):

        '''
        defines all the Slots and Button events.
        '''
        self.calibration_connections()
        self.printer_status_connections()
        self.updates_connections()
        self.filament_sensor_connections()

        #self.QtSocket.z_home_offset_signal.connect(self.getZHomeOffset)
        #self.QtSocket.temperatures_signal.connect(self.updateTemperature)
        #self.QtSocket.status_signal.connect(self.updateStatus)
        #self.QtSocket.print_status_signal.connect(self.updatePrintStatus)
        # self.QtSocket.update_started_signal.connect(self.softwareUpdateProgress)
        # self.QtSocket.update_log_signal.connect(self.softwareUpdateProgressLog)
        # self.QtSocket.update_log_result_signal.connect(self.softwareUpdateResult)
        # self.QtSocket.update_failed_signal.connect(self.updateFailed)
        # self.QtSocket.connected_signal.connect(self.onServerConnected)
        # self.QtSocket.filament_sensor_triggered_signal.connect(self.filamentSensorHandler)
        # self.QtSocket.firmware_updater_signal.connect(self.firmwareUpdateHandler)

        # # Text Input events

        self.network_connections()

        # self.wifiPasswordLineEdit.clicked_signal.connect(lambda: self.startKeyboard(self.wifiPasswordLineEdit.setText))
        # self.ethStaticIpLineEdit.clicked_signal.connect(lambda: self.ethShowKeyboard(self.ethStaticIpLineEdit))
        # self.ethStaticGatewayLineEdit.clicked_signal.connect(lambda: self.ethShowKeyboard(self.ethStaticGatewayLineEdit))

        # Button Events:

        self.job_ops_connections()

        # Home Screen:
        # self.stopButton.pressed.connect(self.stopActionMessageBox)
        # self.menuButton.pressed.connect(self.keyboardButton)
        self.menuButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        # self.controlButton.pressed.connect(self.control)
        # self.playPauseButton.clicked.connect(self.playPauseAction)

        # MenuScreen
        self.menuBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
        # self.menuControlButton.pressed.connect(self.control)
        self.menuPrintButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
        self.menuCalibrateButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        self.menuSettingsButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # # Calibrate Page
        # self.calibrateBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        # self.nozzleOffsetButton.pressed.connect(self.nozzleOffset)
        # # the -ve sign is such that its converted to home offset and not just distance between nozzle and bed
        # self.nozzleOffsetSetButton.pressed.connect(
        #     lambda: self.setZHomeOffset(self.nozzleOffsetDoubleSpinBox.value(), True))
        # self.nozzleOffsetBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        # #Bypass calibration wizzard page for not using Klipper
        # # self.calibrationWizardButton.clicked.connect(
        # #     lambda: self.stackedWidget.setCurrentWidget(self.calibrationWizardPage))
        # self.calibrationWizardButton.clicked.connect(self.quickStep1)

        # self.calibrationWizardBackButton.clicked.connect(
        #     lambda: self.stackedWidget.setCurrentWidget(self.calibratePage))
        # #required for Klipper
        # # self.quickCalibrationButton.clicked.connect(self.quickStep6)
        # # self.fullCalibrationButton.clicked.connect(self.quickStep1)

        # self.quickStep1NextButton.clicked.connect(self.quickStep2)
        # self.quickStep2NextButton.clicked.connect(self.quickStep3)
        # self.quickStep3NextButton.clicked.connect(self.quickStep4)
        # self.quickStep4NextButton.clicked.connect(self.quickStep5)
        # self.quickStep5NextButton.clicked.connect(self.doneStep)
        # # Required for Klipper
        # # self.quickStep5NextButton.clicked.connect(self.quickStep6)
        # # self.quickStep6NextButton.clicked.connect(self.doneStep)

        # # self.moveZPCalibrateButton.pressed.connect(lambda: octopiclient.jog(z=-0.05))
        # # self.moveZPCalibrateButton.pressed.connect(lambda: octopiclient.jog(z=0.05))
        # self.quickStep1CancelButton.pressed.connect(self.cancelStep)
        # self.quickStep2CancelButton.pressed.connect(self.cancelStep)
        # self.quickStep3CancelButton.pressed.connect(self.cancelStep)
        # self.quickStep4CancelButton.pressed.connect(self.cancelStep)
        # self.quickStep5CancelButton.pressed.connect(self.cancelStep)
        # # self.quickStep6CancelButton.pressed.connect(self.cancelStep)

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
        # self.localStorageSelectButton.pressed.connect(self.printSelectedLocal)
        # self.localStorageDeleteButton.pressed.connect(self.deleteItem)

        # selectedFile Local Screen
        # self.fileSelectedBackButton.pressed.connect(self.fileListLocal)
        # self.fileSelectedPrintButton.pressed.connect(self.printFile)

        # filelistUSBPage
        self.USBStorageBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.printLocationPage))
        self.USBStorageScrollUp.pressed.connect(
            lambda: self.fileListWidgetUSB.setCurrentRow(self.fileListWidgetUSB.currentRow() - 1))
        self.USBStorageScrollDown.pressed.connect(
            lambda: self.fileListWidgetUSB.setCurrentRow(self.fileListWidgetUSB.currentRow() + 1))
        # self.USBStorageSelectButton.pressed.connect(self.printSelectedUSB)
        # self.USBStorageSaveButton.pressed.connect(lambda: self.transferToLocal(prnt=False))

        # selectedFile USB Screen
        # self.fileSelectedUSBBackButton.pressed.connect(self.fileListUSB)
        # self.fileSelectedUSBTransferButton.pressed.connect(lambda: self.transferToLocal(prnt=False))
        # self.fileSelectedUSBPrintButton.pressed.connect(lambda: self.transferToLocal(prnt=True))

        # ControlScreen

        self.control_connections()

        self.moveYPButton.pressed.connect(lambda: octopiclient.jog(y=self.step, speed=1000))
        self.moveYMButton.pressed.connect(lambda: octopiclient.jog(y=-self.step, speed=1000))
        self.moveXMButton.pressed.connect(lambda: octopiclient.jog(x=-self.step, speed=1000))
        self.moveXPButton.pressed.connect(lambda: octopiclient.jog(x=self.step, speed=1000))
        self.moveZPButton.pressed.connect(lambda: octopiclient.jog(z=self.step, speed=1000))
        self.moveZMButton.pressed.connect(lambda: octopiclient.jog(z=-self.step, speed=1000))
        self.extruderButton.pressed.connect(lambda: octopiclient.extrude(self.step))
        self.retractButton.pressed.connect(lambda: octopiclient.extrude(-self.step))
        self.motorOffButton.pressed.connect(lambda: octopiclient.gcode(command='M18'))
        self.fanOnButton.pressed.connect(lambda: octopiclient.gcode(command='M106'))
        self.fanOffButton.pressed.connect(lambda: octopiclient.gcode(command='M107'))
        # self.cooldownButton.pressed.connect(self.coolDownAction)
        # self.step100Button.pressed.connect(lambda: self.setStep(100))
        # self.step1Button.pressed.connect(lambda: self.setStep(1))
        # self.step10Button.pressed.connect(lambda: self.setStep(10))
        self.homeXYButton.pressed.connect(lambda: octopiclient.home(['x', 'y']))
        self.homeZButton.pressed.connect(lambda: octopiclient.home(['z']))
        self.controlBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.homePage))
        self.setToolTempButton.pressed.connect(lambda: octopiclient.setToolTemperature(
            self.toolTempSpinBox.value()))
        self.setBedTempButton.pressed.connect(lambda: octopiclient.setBedTemperature(self.bedTempSpinBox.value()))

        self.setFlowRateButton.pressed.connect(lambda: octopiclient.flowrate(self.flowRateSpinBox.value()))
        self.setFeedRateButton.pressed.connect(lambda: octopiclient.feedrate(self.feedRateSpinBox.value()))

        # self.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='SET_GCODE_OFFSET Z_ADJUST=0.025 MOVE=1'))
        # self.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='SET_GCODE_OFFSET Z_ADJUST=-0.025 MOVE=1'))
        self.moveZPBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z0.025'))
        self.moveZMBabyStep.pressed.connect(lambda: octopiclient.gcode(command='M290 Z-0.025'))


        # ChangeFilament rutien

        self.change_filament_connections()

        # self.changeFilamentButton.pressed.connect(self.changeFilament)
        # self.changeFilamentBackButton.pressed.connect(self.control)
        # self.changeFilamentBackButton2.pressed.connect(self.changeFilamentCancel)
        # self.changeFilamentUnloadButton.pressed.connect(lambda: self.unloadFilament())
        # self.changeFilamentLoadButton.pressed.connect(lambda: self.loadFilament())
        # self.loadDoneButton.pressed.connect(self.control)
        # self.unloadDoneButton.pressed.connect(self.changeFilament)
        self.retractFilamentButton.pressed.connect(lambda: octopiclient.extrude(-20))
        self.ExtrudeButton.pressed.connect(lambda: octopiclient.extrude(20))

        # Settings Page

        self.pair_phone_connections()

        self.networkSettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))
        self.displaySettingsButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))
        self.settingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.MenuPage))
        # self.pairPhoneButton.pressed.connect(self.pairPhoneApp)
        # self.OTAButton.pressed.connect(self.softwareUpdate)
        # self.versionButton.pressed.connect(self.displayVersionInfo)

        self.restartButton.pressed.connect(self.askAndReboot)
        self.restoreFactoryDefaultsButton.pressed.connect(self.restoreFactoryDefaults)
        self.restorePrintSettingsButton.pressed.connect(self.restorePrintDefaults)

        # Network settings page
        # self.networkInfoButton.pressed.connect(self.networkInfo)
        # self.configureWifiButton.pressed.connect(self.wifiSettings)
        # self.configureEthButton.pressed.connect(self.ethSettings)
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

        # Ethernet setings page
        self.ethStaticCheckBox.stateChanged.connect(self.ethStaticChanged)
        # self.ethStaticCheckBox.stateChanged.connect(lambda: self.ethStaticSettings.setVisible(self.ethStaticCheckBox.isChecked()))
        self.ethStaticIpKeyboardButton.pressed.connect(lambda: self.ethShowKeyboard(self.ethStaticIpLineEdit))
        self.ethStaticGatewayKeyboardButton.pressed.connect(lambda: self.ethShowKeyboard(self.ethStaticGatewayLineEdit))
        self.ethSettingsDoneButton.pressed.connect(self.ethSaveStaticNetworkInfo)
        self.ethSettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.networkSettingsPage))

        # Display settings
        self.rotateDisplay.pressed.connect(self.showRotateDisplaySettingsPage)
        self.calibrateTouch.pressed.connect(self.touchCalibration)
        self.displaySettingsBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # Rotate Display Settings
        self.rotateDisplaySettingsDoneButton.pressed.connect(self.saveRotateDisplaySettings)
        self.rotateDisplaySettingsCancelButton.pressed.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.displaySettingsPage))

        # QR Code
        self.QRCodeBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))

        # SoftwareUpdatePage
        self.softwareUpdateBackButton.pressed.connect(lambda: self.stackedWidget.setCurrentWidget(self.settingsPage))
        self.performUpdateButton.pressed.connect(lambda: octopiclient.performSoftwareUpdate())

        # Firmware update page
        self.firmwareUpdateBackButton.pressed.connect(self.firmwareUpdateBack)

        # Filament sensor toggle
        self.toggleFilamentSensorButton.clicked.connect(self.toggleFilamentSensor)

    #  # Lock settings
    #     if not Development:
    #         self.pgLock_pin.textChanged.connect(self.Lock_onPinInputChanged)
    
    #         self.pgLock_bt1.clicked.connect(lambda: self.Lock_kbAdd("1"))
    #         self.pgLock_bt2.clicked.connect(lambda: self.Lock_kbAdd("2"))
    #         self.pgLock_bt3.clicked.connect(lambda: self.Lock_kbAdd("3"))
    #         self.pgLock_bt4.clicked.connect(lambda: self.Lock_kbAdd("4"))
    #         self.pgLock_bt5.clicked.connect(lambda: self.Lock_kbAdd("5"))
    #         self.pgLock_bt6.clicked.connect(lambda: self.Lock_kbAdd("6"))
    #         self.pgLock_bt7.clicked.connect(lambda: self.Lock_kbAdd("7"))
    #         self.pgLock_bt8.clicked.connect(lambda: self.Lock_kbAdd("8"))
    #         self.pgLock_bt9.clicked.connect(lambda: self.Lock_kbAdd("9"))
    #         self.pgLock_bt0.clicked.connect(lambda: self.Lock_kbAdd("0"))
    #         self.pgLock_btBackspace.clicked.connect(lambda: self.pgLock_pin.backspace())
    #         self.pgLock_btSubmit.clicked.connect(self.Lock_submitPIN)

        
# MainUIClass.Lock_showLock = door_lock.Lock_showLock
# MainUIClass.Lock_kbAdd = door_lock.Lock_kbAdd
# MainUIClass.Lock_onPinInputChanged = door_lock.Lock_onPinInputChanged
# MainUIClass.Lock_submitPIN = door_lock.Lock_submitPIN

# MainUIClass.printRestoreMessageBox = print_restore.printRestoreMessageBox
# MainUIClass.onServerConnected = print_restore.onServerConnected

# MainUIClass.isFilamentSensorInstalled = filament_sensor.isFilamentSensorInstalled
# MainUIClass.filamentSensorHandler = filament_sensor.filamentSensorHandler
# MainUIClass.toggleFilamentSensor = filament_sensor.toggleFilamentSensor

# MainUIClass.firmwareUpdateCheck = firmware_ota_update.firmwareUpdateCheck
# MainUIClass.firmwareUpdateStart = firmware_ota_update.firmwareUpdateStart
# MainUIClass.firmwareUpdateStartProgress = firmware_ota_update.firmwareUpdateStartProgress
# MainUIClass.firmwareUpdateProgress = firmware_ota_update.firmwareUpdateProgress
# MainUIClass.firmwareUpdateBack = firmware_ota_update.firmwareUpdateBack
# MainUIClass.firmwareUpdateHandler = firmware_ota_update.firmwareUpdateHandler

# MainUIClass.getFirmwareVersion = firmware_ota_update.getFirmwareVersion
# MainUIClass.displayVersionInfo = firmware_ota_update.displayVersionInfo
# MainUIClass.softwareUpdateResult = firmware_ota_update.softwareUpdateResult
# MainUIClass.softwareUpdateProgress = firmware_ota_update.softwareUpdateProgress
# MainUIClass.softwareUpdateProgressLog = firmware_ota_update.softwareUpdateProgressLog
# MainUIClass.updateFailed = firmware_ota_update.updateFailed
# MainUIClass.softwareUpdate = firmware_ota_update.softwareUpdate

# MainUIClass.touchCalibration = display_settings.touchCalibration
# MainUIClass.showRotateDisplaySettingsPage = display_settings.showRotateDisplaySettingsPage
# #MainUIClass.saveRotateDisplaySettings = display_settings.saveRotateDisplaySettings
# MainUIClass.saveRotateDisplaySettings = display_settings.saveRotateDisplaySettings

# MainUIClass.acceptWifiSettings = network_config.acceptWifiSettings
# MainUIClass.wifiReconnectResult = network_config.wifiReconnectResult
# MainUIClass.networkInfo = network_config.networkInfo
# MainUIClass.wifiSettings = network_config.wifiSettings
# MainUIClass.scan_wifi = network_config.scan_wifi
# MainUIClass.setIPStatus = network_config.setIPStatus

# MainUIClass.ethSettings = network_config.ethSettings
# MainUIClass.ethStaticChanged = network_config.ethStaticChanged
# MainUIClass.ethNetworkInfo = network_config.ethNetworkInfo
# MainUIClass.isIpErr = network_config.isIpErr
# MainUIClass.showIpErr = network_config.showIpErr
# MainUIClass.ethSaveStaticNetworkInfo = network_config.ethSaveStaticNetworkInfo
# MainUIClass.ethReconnectResult = network_config.ethReconnectResult
# MainUIClass.ethShowKeyboard = network_config.ethShowKeyboard

# MainUIClass.unloadFilament = change_filament.unloadFilament
# MainUIClass.loadFilament = change_filament.loadFilament
# MainUIClass.changeFilament = change_filament.changeFilament
# MainUIClass.changeFilamentCancel = change_filament.changeFilamentCancel

# MainUIClass.stopActionMessageBox = job_operations.stopActionMessageBox
# MainUIClass.playPauseAction = job_operations.playPauseAction
# MainUIClass.fileListLocal = job_operations.fileListLocal
# MainUIClass.fileListUSB = job_operations.fileListUSB
# MainUIClass.printSelectedLocal = job_operations.printSelectedLocal
# MainUIClass.printSelectedUSB = job_operations.printSelectedUSB
# MainUIClass.transferToLocal = job_operations.transferToLocal
# MainUIClass.printFile = job_operations.printFile
# MainUIClass.deleteItem = job_operations.deleteItem

# MainUIClass.updateTemperature = printer_status.updateTemperature
# MainUIClass.updatePrintStatus = printer_status.updatePrintStatus
# MainUIClass.updateStatus = printer_status.updateStatus

# MainUIClass.control = control_screen.control
# MainUIClass.setStep = control_screen.setStep
# MainUIClass.coolDownAction = control_screen.coolDownAction

# # MainUIClass.getZHomeOffset = calibration.getZHomeOffset
# # MainUIClass.setZHomeOffset = calibration.setZHomeOffset
# # MainUIClass.nozzleOffset = calibration.nozzleOffset
# # MainUIClass.quickStep1 = calibration.quickStep1
# # MainUIClass.quickStep2 = calibration.quickStep2
# # MainUIClass.quickStep3 = calibration.quickStep3
# # MainUIClass.quickStep4 = calibration.quickStep4
# # MainUIClass.quickStep5 = calibration.quickStep5
# # #MainUIClass.quickStep6 = calibration.quickStep6
# # MainUIClass.doneStep = calibration.doneStep
# # MainUIClass.cancelStep = calibration.cancelStep

# MainUIClass.startKeyboard = start_keyboard.startKeyboard

# MainUIClass.restoreFactoryDefaults = restore_defaults.restoreFactoryDefaults
# MainUIClass.restorePrintDefaults = restore_defaults.restorePrintDefaults

# MainUIClass.tellAndReboot = reboot.tellAndReboot
# MainUIClass.askAndReboot = reboot.askAndReboot

# MainUIClass.handleStartupError = error_handling.handleStartupError

# MainUIClass.pairPhoneApp = pair_phone.pairPhoneApp

