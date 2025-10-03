"""
MQTBench Loader
---------------
Utility functions to fetch benchmark quantum circuits from MQTBench.
"""

from typing import Any
from mqt.bench import get_benchmark, BenchmarkLevel


def load_mqtbench_circuits(benchmarks: list[dict[str, Any]]) -> list[Any]:
    """
    Load a list of circuits from MQTBench.

    Args:
        benchmarks: A list of dictionaries, each with:
            - "name": benchmark name (str, e.g. "qft", "ghz", "grover")
            - "qubits": number of qubits (int)

        Example:
            benchmarks = [
                {"name": "qft", "qubits": 3},
                {"name": "ghz", "qubits": 5}
            ]

    Returns:
        A list of Qiskit QuantumCircuit objects.
    """
    circuits = []
    for b in benchmarks:
        name = b["name"]
        nq = b["qubits"]
        try:
            qc = get_benchmark(benchmark=name, level=BenchmarkLevel.ALG, circuit_size=nq)
            circuits.append(qc)
        except Exception as e:
            print(f"[WARN] Failed to load {name}-{nq}: {e}")
    return circuits

# Example preset collections of benchmarks
PRESET_SMALL = [
    {"name": "ghz", "qubits": 5},
    {"name": "qft", "qubits": 128},
    {"name": "qft", "qubits": 3},
    {"name": "grover", "qubits": 3},
]

PRESET_MEDIUM = [
    {"name": "qft", "qubits": 10},
    {"name": "ghz", "qubits": 10},
    {"name": "vqe", "qubits": 6},
]