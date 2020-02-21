import sys
import pyqtgraph as pg
import data_query as dq

from PyQt5 import QtGui, QtWidgets
from sql import session
from typing import List, Dict
from functools import partial


class PlotsWindow(QtGui.QWidget):
    def __init__(self, session):
        super().__init__()
        self.title: str = "Plots"
        self.left: int = 100
        self.top: int = 100
        self.width: int = 600
        self.height: int = 400
        self.buffer: int = 60  # Buffer in seconds
        self.maxBuffer: int = 300  # Buffer in seconds
        self.timerTimeout: int = 500  # Timeout in milliseconds
        self.session = session
        self.getNodesAndSensors()
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        windowLayout = QtWidgets.QVBoxLayout()
        self.createEmptyPlotsGrid()
        for node in self.nodes:
            windowLayout.addWidget(self.nodeGrids[node], stretch=1)
        self.createAllPlots()

        self.setLayout(windowLayout)
        self.show()

    def getNodesAndSensors(self):
        """ Queries the database for the list of all nodes and sensors """
        self.nodes: List[str] = dq.get_all_nodes()
        self.nodes.sort()
        self.sensors: Dict[str, List[str]] = {}
        for node in self.nodes:
            tmp_sensors: List[str] = dq.get_all_sensors(node)
            tmp_sensors.sort()
            self.sensors[node] = tmp_sensors

    def createEmptyPlotsGrid(self) -> None:
        """ Creates all the node grids for later plotting """
        self.nodeGrids: Dict[str, pg.GraphicsLayoutWidget] = {}
        for node in self.nodes:
            self.nodeGrids[node] = pg.GraphicsLayoutWidget()
            # self.nodeGrids[node].centralLayout().
            self.nodeGrids[node].centralWidget.setBorder(pg.mkPen('r'))

    def createAllPlots(self):
        self.plots: Dict[str, Dict[str, pg.PlotWidget]] = {}
        for i, node in enumerate(self.nodes):
            self.plots[node] = {}
            for j, sensor in enumerate(self.sensors[node]):
                plot = pg.PlotItem(title=node + "/" + sensor)
                plot.hide()
                print("Created plot %s/%s" % (node, sensor))
                self.plots[node][sensor] = plot
                # Add plot to plots grid
                self.nodeGrids[node].addItem(plot)

    def hideNode(self, node):
        self.nodeGrids[node].hide()
        self.updateLayout()

    def showNode(self, node):
        self.nodeGrids[node].show()
        self.updateLayout()

    def hidePlot(self, node: str, sensor: str):
        # print("Hiding plot %s/%s" % (node, sensor))
        self.plots[node][sensor].hide()
        self.updateLayout()

    def showPlot(self, node: str, sensor: str):
        # print("Showing plot %s/%s" % (node, sensor))
        self.plots[node][sensor].show()
        self.updateLayout()

    def updateLayout(self):
        """ Workaround to force the plots to havea correct size. Resizes the main window to its current size, forcing the layout to be updated """
        curr_width: int = self.frameGeometry().width()
        curr_height: int = self.frameGeometry().height()
        self.resize(curr_width, curr_height)


class SettingsWindow(QtGui.QWidget):
    def __init__(self, _master: PlotsWindow):
        super().__init__()
        self.master = _master
        self.title = ("Plotter settings")
        self.left: int = 800
        self.top: int = 800
        self.width: int = 300
        self.height: int = 150
        self.initUI()
        self.connections()

    def initUI(self):
        """ Initialize the UI """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QtWidgets.QVBoxLayout()

        # Create the buffer duration input box
        bufferLayout = QtWidgets.QHBoxLayout()
        bufferLabel = QtWidgets.QLabel("Buffer duration (s): ")
        self.bufferInput: QtWidgets.QSpinBox = QtWidgets.QSpinBox()
        self.bufferInput.setMinimum(1)
        self.bufferInput.setMaximum(self.master.maxBuffer)
        self.bufferInput.setValue(self.master.buffer)
        bufferLayout.addWidget(bufferLabel)
        bufferLayout.addWidget(self.bufferInput)
        layout.addLayout(bufferLayout)

        # Create a list of checkboxes of all the nodes and sensors
        nodesLayout = QtWidgets.QVBoxLayout()
        nodesLabeL = QtWidgets.QLabel("Nodes to plot: ")
        nodesLayout.addWidget(nodesLabeL)
        self.nodeButtons: Dict[str, QtWidgets.QCheckBox] = {}
        self.sensorButtons: Dict[str, Dict[str, QtWidgets.QCheckBox]] = {}
        for node in self.master.nodes:
            # Create the node button
            nodeButton = QtWidgets.QCheckBox(node)
            nodeButton.setChecked(False)
            nodesLayout.addWidget(nodeButton)
            self.nodeButtons[node] = nodeButton
            self.sensorButtons[node] = {}
            # Create the node sensors buttons
            sensorLayout = QtWidgets.QVBoxLayout()
            sensorLayout.setContentsMargins(20, 0, 0, 0)  # Left padding
            for i, sensor in enumerate(self.master.sensors[node]):
                sensorButton = QtWidgets.QCheckBox(sensor)
                sensorButton.setChecked(False)
                sensorButton.hide()
                sensorLayout.addWidget(sensorButton)
                self.sensorButtons[node][sensor] = sensorButton
            nodesLayout.addLayout(sensorLayout)
        layout.addLayout(nodesLayout)

        layout.addStretch()
        self.setLayout(layout)
        self.show()

    def connections(self) -> None:
        """ Define the list of all button connections in the settings pane """
        # Buffer spinbox
        self.bufferInput.valueChanged.connect(self.bufferChanged)
        # Node and sensor checkboxes
        for node in self.master.nodes:
            self.nodeButtons[node].toggled.connect(self.nodeToggled)
            for sensor in self.master.sensors[node]:
                self.sensorButtons[node][sensor].toggled.connect(
                    partial(self.sensorToggled, node, sensor))

    def bufferChanged(self) -> None:
        """ When the buffer input is changed, updates the buffer value of the plotting window. Does not trigger an immediate re-plot """
        newBuffer: int = self.bufferInput.value()
        self.master.buffer = newBuffer

    def nodeToggled(self) -> None:
        """ When a node checkbox is toggled, this function dynamically hides and shows the corresponding sensor checkboxes. It also unchecks sensors of unchecked nodes."""
        for node in self.master.nodes:
            if not self.nodeButtons[node].isChecked():
                # Hide all the sensors buttons
                self.master.hideNode(node)
                for sensor in self.master.sensors[node]:
                    self.sensorButtons[node][sensor].setChecked(False)
                    self.sensorButtons[node][sensor].hide()
            else:
                # Show all the sensor buttons
                self.master.showNode(node)
                for sensor in self.master.sensors[node]:
                    self.sensorButtons[node][sensor].show()

    def sensorToggled(self, node: str, sensor: str) -> None:
        """ Called when a sensor checkbox is toggled """
        print("Sensor %s/%s toggled" % (node, sensor))
        if self.sensorButtons[node][sensor].isChecked():
            self.master.showPlot(node, sensor)
        else:
            self.master.hidePlot(node, sensor)


def main():
    app = pg.QtGui.QApplication(sys.argv)
    app.setApplicationName("Plotter")
    plots_win: PlotsWindow = PlotsWindow(session)
    sett_win: SettingsWindow = SettingsWindow(plots_win)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
