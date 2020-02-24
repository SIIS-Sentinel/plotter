# Generates test data used to test and debug plotter

import data_query as dq
import random as rd
import time
import math

from sql import session, Node, Sensor, Measurement, Event, Attack
from typing import List, Dict

nodes: List[str] = [
    "node_1",
    "node_2",
    "node_3",
    "node_4"
]

sensors: Dict[str, List[str]] = {
    "node_1": [
        "sensor_a",
        "sensor_b",
        "sensor_c",
        "sensor_d",
        "sensor_e",
        "sensor_f"
    ],
    "node_2": [
        "sensor_a",
        "sensor_b",
        "sensor_c",
        "sensor_d",
        "sensor_e",
        "sensor_f"
    ],
    "node_3": [
        "sensor_a",
        "sensor_b",
        "sensor_c",
        "sensor_d",
        "sensor_e",
        "sensor_f"
    ],
    "node_4": [
        "sensor_a",
        "sensor_b",
        "sensor_c",
        "sensor_d",
        "sensor_e",
        "sensor_f"
    ]
}


def add_node(name: str):
    oldNode = session.query(Node.name).filter_by(name=name).all()
    if len(oldNode) == 0:
        newNode = Node(name=name)
        session.add(newNode)
        session.commit()
        # session.flush()


def add_event(ts: float, ev_type: str, node: int):
    newEvent = Event(timestamp=ts, event_type=ev_type, node_id=node)
    session.add(newEvent)
    session.commit()
    # session.flush()


def add_measurement(ts: float, value: float, sensor: int, node: int):
    newMeasurement = Measurement(
        timestamp=ts, value=value, sensor_id=sensor, node_id=node)
    session.add(newMeasurement)
    session.commit()
    # session.flush()


def add_sensor(name: str, unit: str, avg: float, std: float, node: int):
    oldSensor = session.query(Sensor).filter_by(node_id=node, name=name).all()
    if len(oldSensor) == 0:
        newSensor = Sensor(name=name, unit=unit, average=avg,
                           std=std, node_id=node)
        session.add(newSensor)
        session.commit()
        # session.flush()


def add_attack(ts: float, attack_type: int, node: int) -> None:
    newAttack: Attack = Attack(
        timestamp=ts, attack_type=attack_type, node_id=node)
    session.add(newAttack)
    session.commit()


if __name__ == "__main__":
    # Get missing nodes and sensors
    curr_nodes: List[str] = dq.get_all_nodes()
    missing_nodes = [n for n in nodes if n not in curr_nodes]
    curr_sensors: Dict[str, List[str]] = {}
    missing_sensors: Dict[str, List[str]] = {}
    for node in nodes:
        curr_sensors[node] = dq.get_all_sensors(node)
        missing_sensors[node] = [n for n in sensors[node]
                                 if n not in curr_sensors[node]]

    # Add missing nodes and sensors
    for node in missing_nodes:
        print("Adding node %s" % node)
        add_node(node)
    for node in nodes:
        for sensor in missing_sensors[node]:
            print("Adding sensor %s/%s" % (node, sensor))
            add_sensor(sensor, "N/A", 0, 0, dq.get_node_id(node))

    # Start adding data on a loop
    attack_counter: int = 0
    attack_period: int = 10
    while True:
        meas_time = time.time()
        for node in nodes:
            node_id: int = dq.get_node_id(node)
            for sensor in sensors[node]:
                sensor_id = dq.get_sensor_id(sensor, node)
                value = math.sin(time.time() / 3.) + rd.random() * 0
                add_measurement(meas_time, value, sensor_id, node_id)
        attack_counter += 1
        if attack_counter >= attack_period:
            attack_counter = 0
            node_id = dq.get_node_id(rd.choice(nodes))
            add_attack(meas_time, 0, node_id)
        time.sleep(0.5)
