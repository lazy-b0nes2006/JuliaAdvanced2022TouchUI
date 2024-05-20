from threads import octopiclient
import styles
from config import _fromUtf8
from PyQt5 import QtGui

def printer_status_connections(self):
    self.QtSocket.temperatures_signal.connect(self.updateTemperature)
    self.QtSocket.print_status_signal.connect(self.updatePrintStatus)
    self.QtSocket.status_signal.connect(self.updateStatus)


def updateTemperature(self, temperature):
    '''
    Slot that gets a signal originating from the thread that keeps polling for printer status
    runs at 1HZ, so do things that need to be constantly updated only. This also controls the cooling fan depending on the temperatures
    :param temperature: dict containing key:value pairs with keys being the tools, bed and their values being their corresponding temperratures
    '''
    if temperature['tool0Target'] == None:
        temperature['tool0Target'] = 0
    if temperature['bedTarget'] == None:
        temperature['bedTarget'] = 0
    if temperature['bedActual'] == None:
        temperature['bedActual'] = 0


    if temperature['tool0Target'] == 0:
        self.tool0TempBar.setMaximum(300)
        self.tool0TempBar.setStyleSheet(styles.bar_heater_cold)
    elif temperature['tool0Actual'] <= temperature['tool0Target']:
        self.tool0TempBar.setMaximum(temperature['tool0Target'])
        self.tool0TempBar.setStyleSheet(styles.bar_heater_heating)
    else:
        self.tool0TempBar.setMaximum(temperature['tool0Actual'])
    self.tool0TempBar.setValue(int(temperature['tool0Actual']))     #self.tool0TempBar.setValue(temperature['tool0Actual'])
    self.tool0ActualTemperature.setText(str(int(temperature['tool0Actual'])))  # + unichr(176)
    self.tool0TargetTemperature.setText(str(int(temperature['tool0Target'])))

    if temperature['bedTarget'] == 0:
        self.bedTempBar.setMaximum(150)
        self.bedTempBar.setStyleSheet(styles.bar_heater_cold)
    elif temperature['bedActual'] <= temperature['bedTarget']:
        self.bedTempBar.setMaximum(temperature['bedTarget'])
        self.bedTempBar.setStyleSheet(styles.bar_heater_heating)
    else:
        self.bedTempBar.setMaximum(int(temperature['bedActual']))       #self.bedTempBar.setMaximum(temperature['bedActual'])
    self.bedTempBar.setValue(int(temperature['bedActual']))     #self.bedTempBar.setValue(temperature['bedActual'])
    self.bedActualTemperatute.setText(str(int(temperature['bedActual'])))  # + unichr(176))
    self.bedTargetTemperature.setText(str(int(temperature['bedTarget'])))  # + unichr(176))

    # updates the progress bar on the change filament screen
    if self.changeFilamentHeatingFlag:
        if temperature['tool0Target'] == 0:
            self.changeFilamentProgress.setMaximum(300)
        elif temperature['tool0Target'] - temperature['tool0Actual'] > 1:
            self.changeFilamentProgress.setMaximum(temperature['tool0Target'])
        else:
            self.changeFilamentProgress.setMaximum(temperature['tool0Actual'])
            self.changeFilamentHeatingFlag = False
            if self.loadFlag:
                self.stackedWidget.setCurrentWidget(self.changeFilamentExtrudePage)
            else:
                self.stackedWidget.setCurrentWidget(self.changeFilamentRetractPage)
                octopiclient.extrude(10)  # extrudes some amount of filament to prevent plugging

        self.changeFilamentProgress.setValue(temperature['tool0Actual'])

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
            img = octopiclient.getImage(file['job']['file']['name'].replace(".gcode", ".png"))
            if img:
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(img)
                self.printPreviewMain.setPixmap(pixmap)
            else:
                self.printPreviewMain.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))

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
        # if not Development:
        #     if not self.__timelapse_enabled:
        #         octopiclient.cancelPrint()
        #         self.coolDownAction()

    elif status == "Paused":
        self.playPauseButton.setChecked(False)
        self.stopButton.setDisabled(False)
        self.motionTab.setDisabled(False)
        self.changeFilamentButton.setDisabled(False)
        self.menuCalibrateButton.setDisabled(True)
        self.menuPrintButton.setDisabled(True)

    else:
        self.stopButton.setDisabled(True)
        self.playPauseButton.setChecked(False)
        self.motionTab.setDisabled(False)
        self.changeFilamentButton.setDisabled(False)
        self.menuCalibrateButton.setDisabled(False)
        self.menuPrintButton.setDisabled(False)
