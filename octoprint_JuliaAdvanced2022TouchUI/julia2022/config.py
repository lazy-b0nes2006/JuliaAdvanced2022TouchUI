from PyQt5 import QtCore
from collections import OrderedDict

# TODO:
'''
# Remove SD card capability from octoprint settings
# Should add error/status checking in the response in some functions in the octoprintAPI
# session keys??
# printer status should show errors from printer.
# async requests
# http://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot
# fix wifi
# status bar netweorking and wifi stuff
# reconnect to printer using GUI
# check if disk is getting full
# recheck for internet being conneted, refresh button
# load filaments from a file
# store settings to a file
# change the way active extruder print stores the current active extruder using positionEvent
#settings should show the current wifi
#clean up keyboard nameing
#add asertions and exeptions
#disaable done button if empty
#oncancel change filament cooldown
#toggle temperature indipendant of motion
#get active extruder from motion controller. when pausing, note down and resume with active extruder
#QR code has dictionary with IP address also
Testing:
# handle nothing selected in file select menus when deleting and printing etc.
# Delete items from local and USB
# different file list pages for local and USB
# test USB/Local properly
# check for uploading error when uploading from USB
# Test if active extruder goes back after pausing
# TRy to fuck with printing process from GUI
# PNG Handaling
# dissable buttons while printing
'''

Development = False      # set to True if running on any system other than RaspberryPi

ip = '192.168.0.20'
apiKey = 'B508534ED20348F090B4D0AD637D3660'

file_name = ''
filaments = [
                ("PLA", 190),
                ("ABS", 220),
                ("PETG", 220),
                ("PVA", 210),
                ("TPU", 230),
                ("Nylon", 220),
                ("PolyCarbonate", 240),
                ("HIPS", 220),
                ("WoodFill", 220),
                ("CopperFill", 200),
                ("Breakaway", 220)
]

filaments = OrderedDict(filaments)

#values before 2020 changes
calibrationPosition = {'X1': 63, 'Y1': 67, #110, 18
                       'X2': 542, 'Y2': 67, #510, 18
                       'X3': 303, 'Y3': 567, #310, 308
                       'X4': 303, 'Y4': 20
                       }

tool0PurgePosition = {'X': -27, 'Y': -112}
tool1PurgePosition = {'X': 648, 'Y': -112}

ptfeTubeLength = 2400 #2400 for 600x600, 1500 for 600x300 keep as multiples of 300 only

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s