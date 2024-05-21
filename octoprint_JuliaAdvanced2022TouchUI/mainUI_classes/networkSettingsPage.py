class networkSettingsPage:
    def __init__(self, obj):
        self.obj = obj
        obj.networkInfoButton.pressed.connect(obj.wifiSettingsPageInstance.networkInfo)
        obj.configureWifiButton.pressed.connect(obj.wifiSettingsPageInstance.wifiSettings)
        obj.configureEthButton.pressed.connect(obj.ethernetSettingsPageInstance.ethSettings)
        obj.networkSettingsBackButton.pressed.connect(lambda: obj.stackedWidget.setCurrentWidget(obj.settingsPage))