from typing import List

# Useless sensors
useless_sensor: List[str] = [
    "nb_cpus",
    "free_ram",
    "total_ram",
    "free_swap",
    "total_swap",
    "tracked_pid"
]

db_path: str = "postgresql://pi:password@10.0.0.222/sentinel"
