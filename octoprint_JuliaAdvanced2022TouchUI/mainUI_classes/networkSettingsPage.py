class networkSettingsPage:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.networkInfoButton.pressed.connect(self.obj.wifiSettingsPageInstance.networkInfo)
        self.obj.configureWifiButton.pressed.connect(self.obj.wifiSettingsPageInstance.wifiSettings)
        self.obj.configureEthButton.pressed.connect(self.obj.ethernetSettingsPageInstance.ethSettings)
        self.obj.networkSettingsBackButton.pressed.connect(lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.settingsPage))
