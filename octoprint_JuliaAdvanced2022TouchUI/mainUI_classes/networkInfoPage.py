class networkInfoPage:
    def __init__(self, obj):
        obj.networkInfoBackButton.pressed.connect(
            lambda: obj.stackedWidget.setCurrentWidget(obj.networkSettingsPage))
