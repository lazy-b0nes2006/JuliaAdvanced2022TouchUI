import dialog

def Lock_showLock(self):
    self.pgLock_HID.setText(str(self.__packager.hc()))
    self.pgLock_pin.setText("")
    if not self.__timelapse_enabled:
        # dialog.WarningOk(self, "Machine locked!", overlay=True)
        self.stackedWidget.setCurrentWidget(self.pgLock)
    else:
         # if self.__timelapse_started:
        #     dialog.WarningOk(self, "Demo mode!", overlay=True)
        self.stackedWidget.setCurrentWidget(self.homePage)
    
def Lock_kbAdd(self, txt):
    if len(str(self.pgLock_pin.text())) < 9:
        self.pgLock_pin.setText(str(self.pgLock_pin.text()) + txt)
    self.pgLock_pin.setFocus()
    
def Lock_onPinInputChanged(self):
    self.pgLock_btBackspace.setEnabled(len(str(self.pgLock_pin.text())) > 0)
    self.pgLock_btSubmit.setEnabled(len(str(self.pgLock_pin.text())) > 3)
    
def Lock_submitPIN(self):
    k = -1
    t = self.pgLock_pin.text()
    try:
        k = int(t)
        if self.__packager.match(k):
            self.__packager.save(k)
                # self.__timelapse_enabled = True
            if dialog.SuccessOk(self, "Machine unlocked!", overlay=True):
                self.tellAndReboot()
            self.stackedWidget.setCurrentWidget(self.homePage)
        else:
            dialog.WarningOk(self, "Incorrect unlock code")
    except Exception as e:
        dialog.WarningOk(self, "Error while parsing unlock code")
        print(e)