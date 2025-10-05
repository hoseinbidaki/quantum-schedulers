from dataclasses import dataclass
from typing import Any


@dataclass
class QuantumTask:
    id: int
    circuit: Any
    arrival_time: float = 0.0
    priority: int = 0