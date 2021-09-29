import os
# import PyQGIS
from qgis.core import (QgsVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsProject,
                       QgsLayerTreeLayer)

from PyQt5.QtWidgets import QMessageBox, QToolButton, QFrame

# depending on the names you choose and the queries you may implement
from .pomodules.poqgsstations import PoQgsStations # -> to create the stations layer
from .pomodules.poqgscurrentw import PoQgsCurrentw # -> same for water levels

class PoRunner:

    def __init__(self, ui, iface):
        self.iface = iface
        self.ui = ui

        # setup the signal/slots
        self.initConnects()

        # set object variables here...

        # local dir helps us to access basemap data and styles within the plugin folder
        self.local_dir = os.path.dirname(os.path.realpath(__file__))

        self.basemap_rivers = None
        self.currentw = None
        self.layer = None


    def initConnects(self):
        self.ui.chbxShowBasemap.toggled.connect(self.doToggleBasemap)
        self.ui.pbLoadCurrentW.clicked.connect(self.doLoadCurrentW)
        self.ui.bgStylesCurrentW.buttonClicked.connect(self.doCurrentWChangeStyle)

        #labels
        self.ui.chbxShowLabels.toggled.connect(self.doToggleLabels)
        self.ui.chbxShowLabels.setEnabled(False)

        #radio buttons
        self.ui.rbState.setEnabled(False)
        self.ui.rbTrend.setEnabled(False)

        # button for full-extent-zoom
        self.tBzoomAll = QToolButton()
        self.tBzoomAll.setDefaultAction(self.iface.actionZoomFullExtent())
        self.ui.hlTools.insertWidget(0, self.tBzoomAll)

        # seperator
        self.vLine = QFrame ()
        self.vLine.setFrameShape (QFrame.VLine)
        self.vLine.setFrameShadow (QFrame.Sunken)
        self.ui.hlTools.insertWidget (0, self.vLine)


        # button for attribute table
        self.tbOpenTable = QToolButton()
        self.tbOpenTable.setDefaultAction(self.iface.actionOpenTable())
        self.ui.hlTools.insertWidget(0, self.tbOpenTable)

        # seperator
        self.vLine = QFrame ()
        self.vLine.setFrameShape (QFrame.VLine)
        self.vLine.setFrameShadow (QFrame.Sunken)
        self.ui.hlTools.insertWidget (0, self.vLine)

        # button for select feature
        self.tbactionSelect = QToolButton()
        self.tbactionSelect.setDefaultAction(self.iface.actionSelect())
        self.ui.hlTools.insertWidget(0, self.tbactionSelect)

        # seperator
        self.vLine = QFrame ()
        self.vLine.setFrameShape (QFrame.VLine)
        self.vLine.setFrameShadow (QFrame.Sunken)
        self.ui.hlTools.insertWidget (0, self.vLine)

        # identify button
        self.tbactionIdentify = QToolButton()
        self.tbactionIdentify.setDefaultAction(self.iface.actionIdentify())
        self.ui.hlTools.insertWidget(0, self.tbactionIdentify)

        # button for deselection
        self.ui.pbDeselect.clicked.connect(self.deselect)


    # slot methods will follow here...

    def doToggleLabels(self):
        if self.ui.chbxShowLabels.isChecked():
            self.currentw.setLabelsEnabled(True)
        else:
            self.currentw.setLabelsEnabled(False)
        self.layerRefresh(self.currentw)


    def deselect(self):
        self.layer = self.iface.activeLayer()

        # catches the error message when no layer is loaded yet
        if self.layer is None:
            result = QMessageBox.warning(self.ui, 'Warning', "Load data from Pegelonline first",
                              QMessageBox.Ok)
            if result == QMessageBox.Ok:
                return
        else:
            self.layer.removeSelection()

    def doSelectionChanged(self, selection):
        #print(selection)

        # creates an empty list and append each station entry with an id
        stations = []

        for id in selection:
            feat = self.currentw.getFeature(id)
            print(feat['shortname'])
            stations.append(feat)

        self.ui.poGraph.setStations(stations)

        # changes zoom based on selection
        if selection:
            self.iface.actionZoomToSelected().trigger()
        else:
            self.iface.actionZoomFullExtent().trigger()


    def doCurrentWChangeStyle(self, button):

        # applies styles based on radio button
        if button.objectName() == "rbState":
            style = "styles/stateMnwMhw.qml"
        elif button.objectName() == "rbTrend":
            style = "styles/trend.qml"

        self.currentw.loadNamedStyle(os.path.join(self.local_dir, style))
        self.layerRefresh(self.currentw)

        #maptips are set again whenever style changes
        self.layer = self.iface.activeLayer()
        self.layer.setMapTipTemplate('[%"shortname"%] level: [%"value"%], '
                                        'state: [%"stateMnwMhw"%]')
        self.iface.actionMapTips().setChecked(True)

    def layerRefresh(self, lyr):
        """Refreshes a layer in QGIS display"""

        if self.iface.mapCanvas().isCachingEnabled():
            lyr.triggerRepaint()
        else:
            self.iface.mapCanvas().refresh()


    def doLoadCurrentW(self):
        if self.currentw:
            # ask user to reload
            result = QMessageBox.question(self.ui, 'Download', "Reload Layer from Pegelonline?",
                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if result == QMessageBox.Yes:
                QgsProject.instance().removeMapLayer(self.currentw) # will call onDeleteCurrentw
            else:
                return

        postats = PoQgsCurrentw()
        self.currentw = self.createPoMemoryLayer(postats, "Water levels", "styles/trend.qml")
        # self.ui.rbTrend.setChecked(True)
        self.currentw.willBeDeleted.connect(self.onDeleteCurrentw)
        self.currentw.selectionChanged.connect(self.doSelectionChanged)

        # labels
        self.ui.chbxShowLabels.setChecked(True)
        self.ui.chbxShowLabels.setEnabled(True)

        # radio buttons
        self.ui.rbTrend.setEnabled(True)
        self.ui.rbState.setEnabled(True)

        #maptips are enabled once layer is loaded
        self.layer = self.iface.activeLayer()
        self.layer.setMapTipTemplate('[%"shortname"%] level: [%"value"%], '
                                        'state: [%"stateMnwMhw"%]')
        self.iface.actionMapTips().setChecked(True)

    def onDeleteCurrentw(self):
        self.currentw = None

        # disables button on delete
        self.ui.chbxShowLabels.setEnabled(False)
        self.ui.rbState.setEnabled(False)
        self.ui.rbTrend.setEnabled(False)

        #deletes the graph widget if the layer is deleted
        self.ui.poGraph.setStations([])

    def createPoMemoryLayer(self, postats, layername, style):
        """Creates a memory layer from pomodules features
        returns the layer object
        """
        # load data
        features = postats.getFeatures()
        # create layer
        crs = QgsCoordinateReferenceSystem(4326)
        vlout = QgsVectorLayer("Point?crs=%s"%crs.authid(), layername, "memory")
        pr = vlout.dataProvider()
        pr.addAttributes(postats.fields)
        vlout.updateFields()

        pr.addFeatures(features)
        vlout.updateExtents()

        # add layer to QGIS canvas
        QgsProject.instance().addMapLayer(vlout)
        # add a styele
        vlout.loadNamedStyle(os.path.join(self.local_dir, style))
        # turn on labeling
        vlout.setLabelsEnabled(True)
        self.layerRefresh(vlout)

        return vlout

    def doToggleBasemap(self):

        # we need that below
        layerTree = self.iface.layerTreeCanvasBridge().rootGroup()

        # get state of chbx
        # if true, set visible
        if self.ui.chbxShowBasemap.isChecked():

            # is layer is already created/loaded?
            if self.basemap_rivers is None:

                # load layer
                lpath = os.path.join(self.local_dir, "basemap/waters.gpkg") +  "|layername=water_l"
                self.basemap_rivers = self.loadBaseLayer(lpath,"rivers")

                # signal&slot for layers willBeDeleted
                self.basemap_rivers.willBeDeleted.connect(self.onDeleteBasemapRivers)

            else:
                self.setLayerVisible(self.basemap_rivers, True)

        else:
           if self.basemap_rivers is not None:
                self.setLayerVisible(self.basemap_rivers, False)

    def setLayerVisible(self, layer, visible=True):
        layerTree = self.iface.layerTreeCanvasBridge().rootGroup()

        lt = layerTree.findLayer(layer.id())
        if lt:
            lt.setItemVisibilityChecked(visible)

    def loadBaseLayer (self, path, name):
        "" "loads a vector layer and puts it last in layertree" ""
        vlayer = QgsVectorLayer (path, name, "ogr")
        if not vlayer.isValid ():
            print ("Layer '% s' not valid"% path)
            return None
        # see: https://gis.stackexchange.com/questions/267894/how-to-duplicate-a-map-layer-at-most-once-as-the-bottom-layer-in-qgis3-python
        QgsProject.instance().addMapLayer(vlayer, False)
        layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
        layerTree.insertChildNode (-1, QgsLayerTreeLayer (vlayer))
        return vlayer

    def onDeleteBasemapRivers(self):
        print("onDeleteBasemapRivers")
        self.basemap_rivers = None

        self.ui.chbxShowBasemap.setChecked(False)
