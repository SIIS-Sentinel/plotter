from typing import List, Tuple
from sql import session, Node, Event, Measurement, Sensor
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse


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
    # node_name, sensor_name = names
    data: List[Tuple[float, float]] = get_data_tuples(node_name, sensor_name)
    ts: List[float] = [e[0] for e in data]
    val: List[float] = [e[1] for e in data]
    unit = get_sensor_unit(node_name, sensor_name)

    plt.cla()

    plt.plot(ts, val, label="%s (%s)" % (sensor_name, unit))
    plt.xlabel("Time (s)")
    plt.legend(loc='upper left')
    plt.tight_layout()


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
    args = parser.parse_args()
    if args.listnodes:
        nodes = get_all_nodes()
        print("Available nodes: ")
        for node in nodes:
            print("* %s" % node)
    elif args.listsensors:
        sensors = get_all_sensors(args.listsensors)
        print("Available sensors:")
        for sensor in sensors:
            print("* %s" % sensor)
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
