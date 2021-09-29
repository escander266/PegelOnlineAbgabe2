import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QLabel
from PyQt5 import QtGui

# using Urlreader from pomodules
from .pomodules.urlreader import Urlreader, quote
from .pomodules import poBaseURL

# inherit QWidget
class PoGraph(QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # use a separate method to build the UI
        self.initUI()

    def initUI(self):
        self.verticalLayout = QVBoxLayout(self)
        self.comboBox = QComboBox()
        self.comboBox.currentIndexChanged.connect(self.doLoadGraph)

        self.lbGraph = QLabel()

        self.verticalLayout.addWidget(self.comboBox)
        self.verticalLayout.addWidget(self.lbGraph)


    # Slot to load new/next image
    def doLoadGraph(self):

        station = quote(self.comboBox.currentText())

        # removes the graph once no station is selected
        if not station:
            self.lbGraph.clear()
            return

        # loads the data of the past 2 weeks
        url = poBaseURL + "stations/%s/W/measurements.png?start=P15D"%station
        print(url)
        ur = Urlreader(url)

        img_data = ur.getDataResponse()

        # covert png-data into a pixmap
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(img_data)
        self.lbGraph.setPixmap(pixmap)
        # resize the label to fit the image dimensions
        self.lbGraph.resize(pixmap.width(), pixmap.height())


	# Interface to set a list of stations to choose from
    def setStations(self, stations):
        self.comboBox.clear()
        for s in stations:
            name = s['shortname']
            self.comboBox.addItem(name)

        self.comboBox.setCurrentIndex(0)

        # sorts the list alphabetically
        self.comboBox.model().sort(0)

