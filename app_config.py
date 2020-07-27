from typing import List


themes: dict = {
    "light":
    {
        "background": "w",
        "axis": "k",
        "text": "FFFFFF",
        "data_curves": "b",
        "attack_curves": "r"
    },
    "dark":
    {
        "background": "k",
        "axis": "w",
        "text": "000000",
        "data_curves": "y",
        "attack_curves": "g"
    }
}

# Useless sensors
useless_sensor: List[str] = [
    "nb_cpus",
    "free_ram",
    "total_ram",
    "free_swap",
    "total_swap",
    "tracked_pid"
]

db_path: str = "postgresql://pi:password@localhost/sentinel"
