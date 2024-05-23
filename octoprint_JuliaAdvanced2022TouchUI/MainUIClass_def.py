from PyQt5 import QtWidgets, QtGui
import mainGUI
from config import Development, _fromUtf8
import logging
from threads import *
import styles
from socket_qt import QtWebsocket

from gui_elements import ClickableLineEdit

from import_helper import load_classes

from mainUI_classes import start_keyboard, printRestore, controlScreen, filamentSensor, printerStatus, homePage, menuPage, calibrationPage, socketConnections, getFilesAndInfo, printLocationScreen, changeFilamentRoutine, networkInfoPage, wifiSettingsPage, ethernetSettingsPage, networkSettingsPage, displaySettings, softwareUpdatePage, firmwareUpdatePage, settingsPage

class MainUIClass(QtWidgets.QMainWindow, mainGUI.Ui_MainWindow):
    
    def __init__(self):
        '''
        This method gets called when an object of type MainUIClass is defined
        '''
        super(MainUIClass, self).__init__()
        classes = load_classes('mainUI_classes')
        globals().update(classes)
        
        self.controlScreenInstance = controlScreen(self)
        self.printRestoreInstance = printRestore(self)
        self.startKeyboard = start_keyboard.startKeyboard

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
            self.controlScreenInstance.setStep(10)
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
            self.sanityCheck.startup_error_signal.connect(self.controlScreenInstance.handleStartupError)


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

        filamentSensor.isFilamentSensorInstalled(self)
        self.printRestoreInstance.onServerConnected()

    def setActions(self):

        '''
        defines all the Slots and Button events.
        '''

        self.printerStatusInstance = printerStatus(self)    
        self.socketConnectionsInstance = socketConnections(self)
        #Initialising all pages/screens
        self.homePageInstance = homePage(self)
        self.menuPageInstance = menuPage(self)
        self.calibrationPageInstance = calibrationPage(self)
        self.getFilesAndInfoInstance = getFilesAndInfo(self)
        self.printLocationScreenInstance = printLocationScreen(self)
        self.controlScreenInstance.initialise(self)
        self.changeFilamentRoutineInstance = changeFilamentRoutine(self)
        self.networkInfoPageInstance = networkInfoPage(self)
        self.wifiSettingsPageInstance = wifiSettingsPage(self)
        self.ethernetSettingsPageInstance = ethernetSettingsPage(self)
        self.displaySettingsInstance = displaySettings(self)
        self.softwareUpdatePageInstance = softwareUpdatePage(self)
        self.firmwareUpdatePageInstance = firmwareUpdatePage(self)
        self.filamentSensorInstance = filamentSensor(self)
        self.settingsPageInstance = settingsPage(self)
        self.networkSettingsPageInstance = networkSettingsPage(self)
 
        #  # Lock settings
        #     if not Development:
        #         self.lockSettingsInstance = lockSettings(self)
        