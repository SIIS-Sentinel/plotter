import matplotlib.pyplot as plt
import matplotlib
import argparse
import time
import pyqtgraph as pg
import sys
import data_query as dq

from pyqtgraph.Qt import QtGui, QtCore
from typing import List, Tuple, Dict
from matplotlib.animation import FuncAnimation
from math import ceil, sqrt


def animate(frame: int, node_name: str, sensor_name: str) -> None:
    """Prune data before buffer"""
    if args.buffer:
        current_time: float = time.time()
        cutoff_ts: float = current_time - args.buffer
        data: List[Tuple[float, float]] = dq.get_data_tuples_after_ts(
            node_name, sensor_name, cutoff_ts)
    else:
        data = dq.get_data_tuples(
            node_name, sensor_name)
    ts: List[float] = [e[0] for e in data]
    val: List[float] = [e[1] for e in data]
    unit: str = dq.get_sensor_unit(node_name, sensor_name)
    attacks: List[Tuple[float, int]
                  ] = dq.get_node_attacks_after_ts(node_name, ts[0])

    plt.cla()
    # Plot the values
    plt.plot(ts, val, label="%s (%s)" % (sensor_name, unit))
    # Plot the attacks
    for a in attacks:
        plt.axvline(x=a[0], color='r', linestyle="--")
    plt.xlabel("Time (s)")
    plt.legend(loc='upper left')
    plt.tight_layout()


def animate_all(frame: int, node_name: str, axes: matplotlib.axes.Axes) -> None:
    sensors: List[str] = dq.remove_useless_sensors(
        dq.get_all_sensors(args.all))
    # Get the data
    current_time: float = time.time()
    if args.buffer:
        # Prune data before before buffer
        cutoff_ts: float = current_time - args.buffer
        data_dict: Dict[str, List[Tuple[float, float]]] = dq.get_data_tuples_batch_after_ts(
            node_name, sensors, cutoff_ts)
    else:
        # Do not prune
        data_dict = dq.get_data_tuples_batch(node_name, sensors)
    plt.gcf().canvas.flush_events()
    attacks_all: List[Tuple[float, int]] = dq.get_node_attacks(node_name)
    for i, s in enumerate(sensors):
        ts_offset: List[float] = [e[0] for e in data_dict[s]]
        offset: float = ts_offset[0]
        attacks = [a for a in attacks_all if a[0] >= offset]
        ts: List[float] = [e - offset for e in ts_offset]
        values: List[float] = [e[1] for e in data_dict[s]]
        ax = axes.reshape(-1)[i]
        ax.clear()
        ax.plot(ts, values, label=sensors[i])
        for a in attacks:
            ax.axvline(x=a[0] - offset, color="r", linestyle="--")
        ax.legend(loc='upper left')
    plt.tight_layout()


def get_subplot_format(num_graphs: int) -> Tuple[int, int]:
    """Returns an optimal number of cols/rows for the given number of plots """
    cols: int = ceil(sqrt(num_graphs))
    rows: int = ceil(num_graphs / cols)
    return (cols, rows)


def getWinCurves(win: pg.graphicsItems.PlotDataItem.PlotDataItem) -> List[pg.graphicsItems.PlotDataItem.PlotDataItem]:
    return [e for e in win.items() if type(e) == pg.graphicsItems.PlotDataItem.PlotDataItem]


def getWinPlots(win: pg.graphicsItems.PlotDataItem.PlotDataItem) -> List[pg.graphicsItems.PlotItem.PlotItem]:
    return [e for e in win.items() if type(e) == pg.graphicsItems.PlotItem.PlotItem]


def plot_all_qt():
    global win, app, qtArgs
    # Get the sensors list
    sensors: List[str] = dq.remove_useless_sensors(
        dq.get_all_sensors(args.all))
    # Get the plot objects
    curves: List[pg.graphicsItems.PlotDataItem.PlotDataItem] = getWinCurves(
        win)
    # Get the data to plot
    current_time: float = time.time()
    if args.buffer:
        cutoff_ts: float = current_time - args.buffer
        data_dict: Dict[str, List[Tuple[float, float]]] = dq.get_data_tuples_batch_after_ts(
            args.all, sensors, cutoff_ts)
    else:
        data_dict = dq.get_data_tuples_batch(args.all, sensors)
    # If necessary, create the curves and legend the first time
    if len(curves) == 0:
        plots = getWinPlots(win)
        for i, sensor in enumerate(sensors):
            plots[i].addLegend()
            plots[i].plot(name=sensor)
        curves = getWinCurves(win)
    # Plot the data
    for i, sensor in enumerate(sensors):
        offset: float = data_dict[sensor][0][0]
        x = [e[0] - offset for e in data_dict[sensor]]
        y = [e[1] for e in data_dict[sensor]]
        curves[i].setData(x, y, pen=pg.mkPen('b', width=3))
    app.processEvents()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Plot real-time Watchtower data.')
    parser.add_argument("--node", metavar="node", type=str,
                        help="Node you wish to examine")
    parser.add_argument("--sensor", metavar="sensor", type=str,
                        help="Sensor you wish to examine")
    parser.add_argument("--listnodes", action="store_true",
                        help="List all the available nodes")
    parser.add_argument("--listsensors", metavar="Node", type=str,
                        help="List all the available sensors of the given node")
    parser.add_argument("--plot", metavar="name",
                        nargs=2, type=str, help="Node and sensor name to plot")
    parser.add_argument("--all", metavar="node", type=str,
                        help="Plot all available sensors for the given node")
    parser.add_argument("--buffer", metavar="duration",
                        type=int, help="Sliding time window of plotting (in s)")
    parser.add_argument("--qt", action="store_true",
                        help="Use PyQtGraph instead of Matplotlib (faster graphs)")
    args = parser.parse_args()
    if args.listnodes:
        nodes = dq.get_all_nodes()
        print("Available nodes: ")
        for node in nodes:
            print("* %s" % node)
    elif args.listsensors:
        sensors: List[str] = dq.get_all_sensors(args.listsensors)
        print("Available sensors:")
        for sensor in sensors:
            print("* %s" % sensor)
    elif args.all:
        sensors = dq.remove_useless_sensors(dq.get_all_sensors(args.all))
        num_sensors: int = len(sensors)
        (cols, rows) = get_subplot_format(num_sensors)
        if not args.qt:
            fig: matplotlib.figure.Figure
            axes: matplotlib.axes.Axes
            fig, axes = plt.subplots(rows, cols)
            anim = FuncAnimation(fig, animate_all,
                                 interval=1000, fargs=[args.all, axes])
            plt.show()
        else:
            pg.setConfigOptions(background='w', foreground='k')
            app = QtGui.QApplication([])
            win = pg.GraphicsWindow()
            for i in range(rows):
                for j in range(cols):
                    plt = win.addPlot(row=i, col=j)
            qtArgs = {"node_name": args.all}
            timer = QtCore.QTimer()
            timer.timeout.connect(plot_all_qt)
            timer.start(100)
            if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_'):
                QtGui.QApplication.instance().exec_()

    elif args.node and args.sensor:
        anim = FuncAnimation(plt.gcf(), animate, interval=1000,
                             fargs=[args.node, args.sensor])
        plt.show()
    elif args.plot:
        anim = FuncAnimation(plt.gcf(), animate,
                             interval=1000, fargs=args.plot)
        plt.show()
    else:
        parser.print_help()
