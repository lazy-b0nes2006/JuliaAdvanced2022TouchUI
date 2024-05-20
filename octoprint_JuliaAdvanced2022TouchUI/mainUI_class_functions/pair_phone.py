from network_utils import getIP
import qrcode
from threads import ThreadRestartNetworking
from gui_elements import Image
import dialog

def pair_phone_connections(self):
    self.pairPhoneButton.pressed.connect(self.pairPhoneApp)

def pairPhoneApp(self):
    if getIP(ThreadRestartNetworking.ETH) is not None:
        qrip = getIP(ThreadRestartNetworking.ETH)
    elif getIP(ThreadRestartNetworking.WLAN) is not None:
        qrip = getIP(ThreadRestartNetworking.WLAN)
    else:
        if dialog.WarningOk(self, "Network Disconnected"):
            return
    self.QRCodeLabel.setPixmap(
        qrcode.make("http://"+ qrip, image_factory=Image).pixmap())
    self.stackedWidget.setCurrentWidget(self.QRCodePage)
