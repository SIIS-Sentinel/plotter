from typing import List, Tuple, Dict
from operator import itemgetter

from bookkeeper.sql import create_sessions, Node, Sensor, Measurement, Attack

import app_config as cfg

session = create_sessions(cfg.db_path)


def get_node_id(name: str) -> int:
    """Given a node name, returns its ID"""
    node = session.query(Node.id).filter_by(name=name).all()
    if len(node) == 0:
        return 0
    return node[0].id


def get_sensor_id(sensor_name: str, node_name: str) -> int:
    """Given a sensor/node name, returns its ID"""
    node_id = session.query(Node.id).filter_by(name=node_name).all()
    sensor = session.query(Sensor.id).filter_by(
        name=sensor_name, node_id=node_id[0].id).all()
    if len(sensor) == 0:
        return 0
    return sensor[0].id


def get_data_tuples(node_name: str, sensor_name: str) -> List[Tuple[float, float]]:
    """Returns the list of all data points for the given node/sensor"""
    node_id: int = get_node_id(node_name)
    sensor_id: int = get_sensor_id(sensor_name, node_name)
    values: list = session.query(Measurement.timestamp, Measurement.value).filter_by(
        node_id=node_id, sensor_id=sensor_id).all()
    tuples: List[Tuple[float, float]] = [
        (e.timestamp, e.value) for e in values]
    return tuples


def get_data_tuples_after_ts(node_name: str, sensor_name: str, cutoff_ts: float) -> List[Tuple[float, float]]:
    """Returns the list of all data points for the given node/sensor after the given timestamp"""
    node_id: int = get_node_id(node_name)
    sensor_id: int = get_sensor_id(sensor_name, node_name)
    values: list = session.\
        query(Measurement.value, Measurement.timestamp).\
        filter_by(node_id=node_id, sensor_id=sensor_id).\
        filter(Measurement.timestamp >= cutoff_ts).\
        all()
    tuples: List[Tuple[float, float]] = [
        (e.timestamp, e.value) for e in values]
    tuples.sort(key=itemgetter(0))
    return tuples


def get_data_tuples_batch_after_ts(node_name: str, sensor_list: List[str], cutoff_ts: float) -> Dict[str, List[Tuple[float, float]]]:
    """Returns a list of list of tuples of all the sensors requested """
    node_id: int = get_node_id(node_name)
    sensor_id_list: List[Tuple[str, int]] = [
        (s, get_sensor_id(s, node_name)) for s in sensor_list]
    values_blob: list = session.\
        query(Measurement.value, Measurement.timestamp, Measurement.sensor_id).\
        filter_by(node_id=node_id).\
        filter(Measurement.sensor_id.in_([s[1] for s in sensor_id_list])).\
        filter(Measurement.timestamp >= cutoff_ts).\
        all()
    values: Dict[str, List[Tuple[float, float]]] = {}
    for sensor in sensor_id_list:
        tmp_value: List[Tuple[float, float]] = []
        for value in values_blob[::-1]:  # Go over the list backwards
            if value.sensor_id == sensor[1]:
                tmp_value.append((value.timestamp, value.value))
        tmp_value.sort(key=itemgetter(0))
        values[sensor[0]] = tmp_value
    return values


def get_data_tuples_batch_after_ts_all_nodes(nodes_list: List[str], sensor_dict: Dict[str, List[str]], cutoff_ts: float) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
    """ Returns all the values for all the given nodes/sensors after the given cutoff timestamp """
    # node_ids: List[int] = [get_node_id(e) for e in nodes_list]
    sensor_ids: Dict[str, int] = {n + s: get_sensor_id(
        s, n) for n in nodes_list for s in sensor_dict[n]}
    sensor_ids_list: List[int] = [e for e in sensor_ids.values()]
    values_blob: list = session.\
        query(Measurement.value, Measurement.timestamp, Measurement.sensor_id).\
        filter(Measurement.sensor_id.in_(sensor_ids_list)).\
        filter(Measurement.timestamp >= cutoff_ts).\
        all()
    values: Dict[str, Dict[str, List[Tuple[float, float]]]] = {}
    for node in nodes_list:
        values[node] = {}
        for sensor in sensor_dict[node]:
            tmp_value: List[Tuple[float, float]] = []
            for value in values_blob:
                if value.sensor_id == sensor_ids[node + sensor]:
                    tmp_value.append((value.timestamp, value.value))
            tmp_value.sort(key=itemgetter(0))
            values[node][sensor] = tmp_value
    return values


def get_data_tuples_batch(node_name: str, sensor_list: List[str]) -> Dict[str, List[Tuple[float, float]]]:
    return get_data_tuples_batch_after_ts(node_name, sensor_list, 0)


def get_all_sensors(node_name: str) -> List[str]:
    """Returns the list of all sensors for the given node in the database """
    node_id: int = get_node_id(node_name)
    sensors: list = session.query(Sensor.name).filter_by(node_id=node_id).all()
    sensors_str: List[str] = [e.name for e in sensors]
    return sensors_str


def get_all_nodes() -> List[str]:
    """Returns the list of all nodes names stored in the database """
    nodes: list = session.query(Node.name).all()
    nodes_str: List[str] = [e.name for e in nodes]
    return nodes_str


def get_sensor_unit(node_name: str, sensor_name: str) -> str:
    """Returns the unit of the sensor"""
    sensor_id = get_sensor_id(sensor_name, node_name)
    sensor = session.query(Sensor.unit).filter_by(id=sensor_id).all()
    return sensor[0].unit


def get_node_attacks(node_name: str) -> List[Tuple[float, int]]:
    """Returns a list of tuples of timestamp/attack_type"""
    node_id: int = get_node_id(node_name)
    attacks: List[Attack] = session.query(
        Attack.timestamp, Attack.attack_type).filter_by(node_id=node_id).all()
    attacks_list: List[Tuple[float, int]] = [
        (a.timestamp, a.attack_type) for a in attacks]
    return attacks_list


def get_node_attacks_after_ts(node_name: str, cutoff_ts: float) -> List[Tuple[float, int]]:
    """Returns a list of tuples of timestamp/attack_type of attacks after the given timestamp """
    attacks_all: List[Tuple[float, int]] = get_node_attacks(node_name)
    attacks_cutoff: List[Tuple[float, int]] = [
        a for a in attacks_all if a[0] >= cutoff_ts]
    return attacks_cutoff


def remove_useless_sensors(all_sensors: List[str]) -> List[str]:
    """Removes useless sensors from the given sensors list """
    for sensor in cfg.useless_sensor:
        if sensor in all_sensors:
            all_sensors.remove(sensor)
    return all_sensors
