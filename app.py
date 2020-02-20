import sys
import pyqtgraph as pg
import data_query as dq

from PyQt5 import QtGui, QtWidgets
from sql import session
from typing import List, Dict


class PlotsWindow(QtGui.QWidget):
    def __init__(self, session):
        super().__init__()
        self.title: str = "Plots"
        self.left: int = 100
        self.top: int = 100
        self.width: int = 600
        self.height: int = 400
        self.buffer: int = 60
        self.session = session
        self.initUI()
        self.getNodesAndSensors()

    def initUI(self) -> None:
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        windowLayout = QtWidgets.QVBoxLayout()
        self.createEmptyPlotsGrid()
        windowLayout.addWidget(self.plotsGroup)

        self.setLayout(windowLayout)
        self.show()

    def createEmptyPlotsGrid(self) -> None:
        self.plotsGroup = QtWidgets.QGroupBox()
        layout = QtWidgets.QGridLayout()

        self.plotsGroup.setLayout(layout)

    def getNodesAndSensors(self):
        self.nodes: List[str] = dq.get_all_nodes()
        self.sensors: Dict[str, List[str]] = {}
        for node in self.nodes:
            tmp_sensors: List[str] = dq.get_all_sensors(node)
            self.sensors[node] = tmp_sensors


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

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QtWidgets.QVBoxLayout()

        # Create the buffer duration input box
        bufferLayout = QtWidgets.QHBoxLayout()
        bufferLabel = QtWidgets.QLabel("Buffer duration (s): ")
        self.bufferInput = QtGui.QSpinBox()
        self.bufferInput.setValue(self.master.buffer)
        bufferLayout.addWidget(bufferLabel)
        bufferLayout.addWidget(self.bufferInput)
        layout.addLayout(bufferLayout)

        # Create a list of checkboxes of all the nodes
        nodesLayout = QtWidgets.QVBoxLayout()
        nodesLayout.setStretch(0, 0)
        nodesLabeL = QtWidgets.QLabel("Nodes to plot: ")
        nodesLayout.addWidget(nodesLabeL)
        self.nodeButtons: dict = {}
        for node in self.master.nodes:
            nodeButton = QtWidgets.QCheckBox(node)
            nodeButton.setChecked(False)
            nodesLayout.addWidget(nodeButton)

            self.nodeButtons[node] = nodeButton
        layout.addLayout(nodesLayout)

        self.setLayout(layout)
        self.show()

    def updateSensors(self):
        """ When a node checkbox is toggled, this function dynamically hides and shows the corredponding sensor checkboxes"""
        for node in self.master.nodes:
            if not self.nodeButtons[node].isChecked():
                # Hide all the sensors buttons
                pass
            else:
                # Show all the sensor buttons
                pass


def main():
    app = pg.QtGui.QApplication(sys.argv)
    app.setApplicationName("Plotter")
    plots_win: PlotsWindow = PlotsWindow(session)
    sett_win: SettingsWindow = SettingsWindow(plots_win)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
