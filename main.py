from typing import List, Tuple
from sql import session, Node, Event, Measurement, Sensor
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
from math import ceil, sqrt


# Given a node name, returns its ID
def get_node_id(name: str) -> int:
    node = session.query(Node.id).filter_by(name=name).all()
    if len(node) == 0:
        return 0
    return node[0].id


# Given a sensor/node name, returns its ID
def get_sensor_id(sensor_name: str, node_name: str) -> int:
    node_id = session.query(Node.id).filter_by(name=node_name).all()
    sensor = session.query(Sensor.id).filter_by(
        name=sensor_name, node_id=node_id[0].id).all()
    if len(sensor) == 0:
        return 0
    return sensor[0].id


# Returns the list of all data points for the given node/sensor
def get_data_tuples(node_name: str, sensor_name: str) -> List[Tuple[float, float]]:
    node_id: int = get_node_id(node_name)
    sensor_id: int = get_sensor_id(sensor_name, node_name)
    values: list = session.query(Measurement).filter_by(
        node_id=node_id, sensor_id=sensor_id).all()
    tuples: List[Tuple[float, float]] = [
        (e.timestamp, e.value) for e in values]
    return tuples


# Returns the list of all sensors for the given node in the database
def get_all_sensors(node_name: str) -> List[str]:
    node_id: int = get_node_id(node_name)
    sensors: list = session.query(Sensor).filter_by(node_id=node_id).all()
    sensors_str: List[str] = [e.name for e in sensors]
    return sensors_str


# Returns the list of all nodes names stored in the database
def get_all_nodes() -> List[str]:
    nodes: list = session.query(Node).all()
    nodes_str: List[str] = [e.name for e in nodes]
    return nodes_str


def get_sensor_unit(node_name: str, sensor_name: str) -> str:
    sensor_id = get_sensor_id(sensor_name, node_name)
    sensor = session.query(Sensor).filter_by(id=sensor_id).all()
    return sensor[0].unit


def animate(frame: int, node_name: str, sensor_name: str) -> None:
    data: List[Tuple[float, float]] = get_data_tuples(node_name, sensor_name)
    # Prune data before buffer
    if args.buffer and args.buffer < len(data):
        n: int = len(data)
        data = data[n - args.buffer:]
    ts: List[float] = [e[0] for e in data]
    val: List[float] = [e[1] for e in data]
    unit = get_sensor_unit(node_name, sensor_name)

    plt.cla()

    plt.plot(ts, val, label="%s (%s)" % (sensor_name, unit))
    plt.xlabel("Time (s)")
    plt.legend(loc='upper left')
    plt.tight_layout()


def animate_all(frame: int, node_name: str, axes) -> None:
    sensors: List[str] = get_all_sensors(args.all)
    data: list = []

    # Prune data before before buffer
    tmp: list = get_data_tuples(node_name, sensors[0])
    if args.buffer and args.buffer < len(tmp):
        n = len(tmp)
        for sensor in sensors:
            subdata: list = get_data_tuples(node_name, sensor)[
                n - args.buffer:]
            data.append(subdata)
    # Do not prune
    else:
        for sensor in sensors:
            data.append(get_data_tuples(node_name, sensor))

    plt.gcf().canvas.flush_events()
    for i in range(len(sensors)):
        ts_offset: List[float] = [e[0] for e in data[i]]
        offset: float = ts_offset[0]
        ts: List[float] = [e - offset for e in ts_offset]
        values: List[float] = [e[1] for e in data[i]]
        ax = axes.reshape(-1)[i]
        ax.clear()
        ax.plot(ts, values, label=sensors[i])
        ax.legend(loc='upper left')
    plt.tight_layout()


def get_subplot_format(num_graphs: int) -> Tuple[int, int]:
    cols: int = ceil(sqrt(num_graphs))
    rows: int = ceil(num_graphs / cols)
    return (cols, rows)


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
                        type=int, help="Maximum number of data points plotted at once")
    args = parser.parse_args()
    if args.listnodes:
        nodes = get_all_nodes()
        print("Available nodes: ")
        for node in nodes:
            print("* %s" % node)
    elif args.listsensors:
        sensors: List[str] = get_all_sensors(args.listsensors)
        print("Available sensors:")
        for sensor in sensors:
            print("* %s" % sensor)
    elif args.all:
        num_sensors: int = len(get_all_sensors(args.all))
        (cols, rows) = get_subplot_format(num_sensors)
        fig, axes = plt.subplots(rows, cols)
        anim = FuncAnimation(fig, animate_all,
                             interval=1000, fargs=[args.all, axes])
        plt.show()
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
