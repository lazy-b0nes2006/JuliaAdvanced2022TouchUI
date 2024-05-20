import dialog
from threads import octopiclient, ThreadFileUpload
import subprocess
from datetime import datetime
from PyQt5 import QtGui
from config import _fromUtf8
import os
from hurry.filesize import size

def job_ops_connections(self):
    self.stopButton.pressed.connect(self.stopActionMessageBox)
    self.playPauseButton.clicked.connect(self.playPauseAction)

    self.fileSelectedBackButton.pressed.connect(self.fileListLocal)
    self.fileSelectedPrintButton.pressed.connect(self.printFile)
    self.localStorageSelectButton.pressed.connect(self.printSelectedLocal)
    self.localStorageDeleteButton.pressed.connect(self.deleteItem)
    
    self.USBStorageSelectButton.pressed.connect(self.printSelectedUSB)
    self.USBStorageSaveButton.pressed.connect(lambda: self.transferToLocal(prnt=False))
    
    self.fileSelectedUSBBackButton.pressed.connect(self.fileListUSB)
    self.fileSelectedUSBTransferButton.pressed.connect(lambda: self.transferToLocal(prnt=False))
    self.fileSelectedUSBPrintButton.pressed.connect(lambda: self.transferToLocal(prnt=True))

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
    for f in files:
        if ".gcode" in f['name']:
            self.fileListWidget.addItem(f['name'])
    #self.fileListWidget.addItems([f['name'] for f in files])
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
        img = octopiclient.getImage(self.fileListWidget.currentItem().text().replace(".gcode", ".png"))
        if img:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(img)
            self.printPreviewSelected.setPixmap(pixmap)

        else:
            self.printPreviewSelected.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))
    except:
        print ("Log: Nothing Selected")
        # Set image fot print preview:
        # self.printPreviewSelected.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/fracktal.png")))
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
        file = '/media/usb0/' + str(self.fileListWidgetUSB.currentItem().text().replace(".gcode", ".png"))
        try:
            exists = os.path.exists(file)
        except:
            exists = False

        if exists:
            self.printPreviewSelectedUSB.setPixmap(QtGui.QPixmap(_fromUtf8(file)))
        else:
            self.printPreviewSelectedUSB.setPixmap(QtGui.QPixmap(_fromUtf8("templates/img/thumbnail.png")))
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
    octopiclient.selectFile(self.fileListWidget.currentItem().text(), True)
    # octopiclient.startPrint()
    self.stackedWidget.setCurrentWidget(self.homePage)

def deleteItem(self):
    '''
    Deletes a gcode file, and if associates, its image file from the memory
    '''
    octopiclient.deleteFile(self.fileListWidget.currentItem().text())
    octopiclient.deleteFile(self.fileListWidget.currentItem().text().replace(".gcode", ".png"))

    # delete PNG also
    self.fileListLocal()
