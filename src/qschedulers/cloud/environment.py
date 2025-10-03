from dataclasses import dataclass
from typing import Any

from qiskit import QuantumCircuit


@dataclass
class QuantumTask:
    id: int
    circuit: Any
    arrival_time: float = 0.0
    priority: int = 0


import qsimpy.core as sp

def create_cloud_env():
    env = sp.Environment()
    return env
