import styles
from PyQt5 import QtGui
from threads import octopiclient
from config import _fromUtf8

class printerStatus:
    def __init__(self, obj):
        self.obj = obj

    ''' +++++++++++++++++++++++++++++++++Printer Status+++++++++++++++++++++++++++++++++++ '''
    def updateTemperature(self, temperature):
        '''
        Slot that gets a signal originating from the thread that keeps polling for printer status
        runs at 1HZ, so do things that need to be constantly updated only. This also controls the cooling fan depending on the temperatures
        :param temperature: dict containing key:value pairs with keys being the tools, bed and their values being their corresponding temperatures
        '''
        if temperature['tool0Target'] is None:
            temperature['tool0Target'] = 0
        if temperature['bedTarget'] is None:
            temperature['bedTarget'] = 0
        if temperature['bedActual'] is None:
            temperature['bedActual'] = 0

        if temperature['tool0Target'] == 0:
            self.obj.tool0TempBar.setMaximum(300)
            self.obj.tool0TempBar.setStyleSheet(styles.bar_heater_cold)
        elif temperature['tool0Actual'] <= temperature['tool0Target']:
            self.obj.tool0TempBar.setMaximum(int(temperature['tool0Target']))
            self.obj.tool0TempBar.setStyleSheet(styles.bar_heater_heating)
        else:
            self.obj.tool0TempBar.setMaximum(temperature['tool0Actual'])
        self.obj.tool0TempBar.setValue(int(temperature['tool0Actual']))
        self.obj.tool0ActualTemperature.setText(str(int(temperature['tool0Actual'])))
        self.obj.tool0TargetTemperature.setText(str(int(temperature['tool0Target'])))

        if temperature['bedTarget'] == 0:
            self.obj.bedTempBar.setMaximum(150)
            self.obj.bedTempBar.setStyleSheet(styles.bar_heater_cold)
        elif temperature['bedActual'] <= temperature['bedTarget']:
            self.obj.bedTempBar.setMaximum(temperature['bedTarget'])
            self.obj.bedTempBar.setStyleSheet(styles.bar_heater_heating)
        else:
            self.obj.bedTempBar.setMaximum(int(temperature['bedActual']))
        self.obj.bedTempBar.setValue(int(temperature['bedActual']))
        self.obj.bedActualTemperatute.setText(str(int(temperature['bedActual'])))
        self.obj.bedTargetTemperature.setText(str(int(temperature['bedTarget'])))

        # updates the progress bar on the change filament screen
        if self.obj.changeFilamentHeatingFlag:
            if temperature['tool0Target'] == 0:
                self.obj.changeFilamentProgress.setMaximum(300)
            elif temperature['tool0Target'] - temperature['tool0Actual'] > 1:
                self.obj.changeFilamentProgress.setMaximum(temperature['tool0Target'])
            else:
                self.obj.changeFilamentProgress.setMaximum(temperature['tool0Actual'])
                self.obj.changeFilamentHeatingFlag = False
                if self.obj.loadFlag:
                    self.obj.stackedWidget.setCurrentWidget(self.obj.changeFilamentExtrudePage)
                else:
                    self.obj.stackedWidget.setCurrentWidget(self.obj.changeFilamentRetractPage)
                    octopiclient.extrude(10)  # extrudes some amount of filament to prevent plugging

            self.obj.changeFilamentProgress.setValue(temperature['tool0Actual'])

    def updatePrintStatus(self, file):
        '''
        Displays information of a particular file on the home page, is a slot for the signal emitted from the thread that keeps polling for printer status
        runs at 1HZ, so do things that need to be constantly updated only
        :param file: dict of all the attributes of a particular file
        '''
        if file is None:
            self.obj.currentFile = None
            self.obj.currentImage = None
            self.obj.timeLeft.setText("-")
            self.obj.fileName.setText("-")
            self.obj.printProgressBar.setValue(0)
            self.obj.printTime.setText("-")
            self.obj.playPauseButton.setDisabled(True)  # if file available, make play button visible
        else:
            self.obj.playPauseButton.setDisabled(False)  # if file available, make play button visible
            self.obj.fileName.setText(file['job']['file']['name'])
            self.obj.currentFile = file['job']['file']['name']
            if file['progress']['printTime'] is None:
                self.obj.printTime.setText("-")
            else:
                m, s = divmod(file['progress']['printTime'], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                self.obj.printTime.setText("%d:%d:%02d:%02d" % (d, h, m, s))

            if file['progress']['printTimeLeft'] is None:
                self.obj.timeLeft.setText("-")
            else:
                m, s = divmod(file['progress']['printTimeLeft'], 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                self.obj.timeLeft.setText("%d:%d:%02d:%02d" % (d, h, m, s))

            if file['progress']['completion'] is None:
                self.obj.printProgressBar.setValue(0)
            else:
                self.obj.printProgressBar.setValue(file['progress']['completion'])

            '''
            If image is available from server, set it, otherwise display default image.
            If the image was already loaded, don't load it again.
            '''
            if self.obj.currentImage != self.obj.currentFile:
                self.obj.currentImage = self.obj.currentFile
                img = octopiclient.getImage(file['job']['file']['name'].replace(".gcode", ".png"))
                if img:
                    pixmap = QtGui.QPixmap()
                    pixmap.loadFromData(img)
                    self.obj.printPreviewMain.setPixmap(pixmap)
                else:
                    self.obj.printPreviewMain.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))

    def updateStatus(self, status):
        '''
        Updates the status bar, is a slot for the signal emitted from the thread that constantly polls for printer status
        this function updates the status bar, as well as enables/disables relevant buttons
        :param status: String of the status text
        '''
        self.obj.printerStatusText = status
        self.obj.printerStatus.setText(status)

        if status == "Printing":  # Green
            self.obj.printerStatusColour.setStyleSheet(styles.printer_status_green)
        elif status == "Offline":  # Red
            self.obj.printerStatusColour.setStyleSheet(styles.printer_status_red)
        elif status == "Paused":  # Amber
            self.obj.printerStatusColour.setStyleSheet(styles.printer_status_amber)
        elif status == "Operational":  # Amber
            self.obj.printerStatusColour.setStyleSheet(styles.printer_status_blue)

        '''
        Depending on Status, enable and Disable Buttons
        '''
        if status == "Printing":
            self.obj.playPauseButton.setChecked(True)
            self.obj.stopButton.setDisabled(False)
            self.obj.motionTab.setDisabled(True)
            self.obj.changeFilamentButton.setDisabled(True)
            self.obj.menuCalibrateButton.setDisabled(True)
            self.obj.menuPrintButton.setDisabled(True)
            # if not Development:
            #     if not self.__timelapse_enabled:
            #         octopiclient.cancelPrint()
            #         self.coolDownAction()
        elif status == "Paused":
            self.obj.playPauseButton.setChecked(False)
            self.obj.stopButton.setDisabled(False)
            self.obj.motionTab.setDisabled(False)
            self.obj.changeFilamentButton.setDisabled(False)
            self.obj.menuCalibrateButton.setDisabled(True)
            self.obj.menuPrintButton.setDisabled(True)
        else:
            self.obj.stopButton.setDisabled(True)
            self.obj.playPauseButton.setChecked(False)
            self.obj.motionTab.setDisabled(False)
            self.obj.changeFilamentButton.setDisabled(False)
            self.obj.menuCalibrateButton.setDisabled(False)
            self.obj.menuPrintButton.setDisabled(False)
