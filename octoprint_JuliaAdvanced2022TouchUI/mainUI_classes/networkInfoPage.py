class networkInfoPage:
    def __init__(self, obj):
        self.obj = obj

    def connect(self):
        self.obj.networkInfoBackButton.pressed.connect(
            lambda: self.obj.stackedWidget.setCurrentWidget(self.obj.networkSettingsPage))
