import dialog

class lockSettings:
    def __init__(self, obj):
        self.obj = obj

        obj.pgLock_pin.textChanged.connect(self.Lock_onPinInputChanged)

        obj.pgLock_bt1.clicked.connect(lambda: self.Lock_kbAdd("1"))
        obj.pgLock_bt2.clicked.connect(lambda: self.Lock_kbAdd("2"))
        obj.pgLock_bt3.clicked.connect(lambda: self.Lock_kbAdd("3"))
        obj.pgLock_bt4.clicked.connect(lambda: self.Lock_kbAdd("4"))
        obj.pgLock_bt5.clicked.connect(lambda: self.Lock_kbAdd("5"))
        obj.pgLock_bt6.clicked.connect(lambda: self.Lock_kbAdd("6"))
        obj.pgLock_bt7.clicked.connect(lambda: self.Lock_kbAdd("7"))
        obj.pgLock_bt8.clicked.connect(lambda: self.Lock_kbAdd("8"))
        obj.pgLock_bt9.clicked.connect(lambda: self.Lock_kbAdd("9"))
        obj.pgLock_bt0.clicked.connect(lambda: self.Lock_kbAdd("0"))
        obj.pgLock_btBackspace.clicked.connect(lambda: obj.pgLock_pin.backspace())
        obj.pgLock_btSubmit.clicked.connect(self.Lock_submitPIN)

    def Lock_showLock(self):
        self.obj.pgLock_HID.setText(str(self.obj.__packager.hc()))
        self.obj.pgLock_pin.setText("")
        if not self.obj.__timelapse_enabled:
            # dialog.WarningOk(self, "Machine locked!", overlay=True)
            self.obj.stackedWidget.setCurrentWidget(self.obj.pgLock)
        else:
            # if self.__timelapse_started:
            #     dialog.WarningOk(self, "Demo mode!", overlay=True)
            self.obj.stackedWidget.setCurrentWidget(self.obj.homePage)
        
    def Lock_kbAdd(self, txt):
        if len(str(self.obj.pgLock_pin.text())) < 9:
            self.obj.pgLock_pin.setText(str(self.obj.pgLock_pin.text()) + txt)
        self.obj.pgLock_pin.setFocus()
        
    def Lock_onPinInputChanged(self):
        self.obj.pgLock_btBackspace.setEnabled(len(str(self.obj.pgLock_pin.text())) > 0)
        self.obj.pgLock_btSubmit.setEnabled(len(str(self.obj.pgLock_pin.text())) > 3)
        
    def Lock_submitPIN(self):
        k = -1
        t = self.obj.pgLock_pin.text()
        try:
            k = int(t)
            if self.obj.__packager.match(k):
                self.obj.__packager.save(k)
                # self.__timelapse_enabled = True
                if dialog.SuccessOk(self.obj, "Machine unlocked!", overlay=True):
                    self.tellAndReboot()
                self.obj.stackedWidget.setCurrentWidget(self.obj.homePage)
            else:
                dialog.WarningOk(self.obj, "Incorrect unlock code")
        except Exception as e:
            dialog.WarningOk(self.obj, "Error while parsing unlock code")
            print(e)
