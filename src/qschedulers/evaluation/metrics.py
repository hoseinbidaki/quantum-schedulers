"""
Metrics
-------
Functions to estimate fidelity, execution time, and swaps for transpiled circuits.
"""

from typing import Any, Tuple
from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGOpNode


def estimate_fidelity_and_time(transpiled_qc: Any, backend: Any, err_map: dict, shots: int = 1024) -> Tuple[float, float, int]:
    """
    Estimate fidelity and execution time for a transpiled circuit.

    Args:
        transpiled_qc: The transpiled QuantumCircuit.
        backend: Qiskit backend.
        err_map: dict from calibration_utils.get_gate_error_map.
        shots: number of repetitions.

    Returns:
        (fidelity, exec_time, swap_count)
    """
    dag = circuit_to_dag(transpiled_qc)
    nodes = list(dag.topological_nodes())

    # Track durations
    node_dur = {}
    for n in nodes:
        if isinstance(n, DAGOpNode):
            opname = n.op.name
            qargs = tuple(q._index for q in n.qargs)  # Qiskit 2.x
            length = _lookup_length(err_map, opname, qargs)
            if length is None:
                length = 300e-9 if opname.lower() in ("cx", "cnot", "cz") else 50e-9
            node_dur[n] = float(length)
        else:
            node_dur[n] = 0.0

    # Critical path (exec time)
    longest_to = {n: 0.0 for n in nodes}
    for n in nodes:
        for s in dag.successors(n):
            cand = longest_to[n] + node_dur.get(s, 0.0)
            if cand > longest_to[s]:
                longest_to[s] = cand
    critical = max(longest_to[n] + node_dur.get(n, 0.0) for n in nodes)
    exec_time = critical * shots

    # Fidelity
    fidelity = 1.0
    for n in nodes:
        if isinstance(n, DAGOpNode):
            opname = n.op.name
            qargs = tuple(q._index for q in n.qargs)
            err = _lookup_error(err_map, opname, qargs)
            if err is None:
                err = 1e-3
            fidelity *= max(0.0, 1.0 - float(err))

    # SWAP count
    swap_count = sum(1 for inst, _, _ in transpiled_qc.data if inst.name.lower() == "swap")

    return fidelity, exec_time, swap_count


def _lookup_error(err_map: dict, opname: str, qargs: tuple):
    opname = opname.lower()
    key = (opname, tuple(qargs))
    if key in err_map and err_map[key].get("error") is not None:
        return err_map[key]["error"]
    return None


def _lookup_length(err_map: dict, opname: str, qargs: tuple):
    opname = opname.lower()
    key = (opname, tuple(qargs))
    if key in err_map and err_map[key].get("length") is not None:
        return err_map[key]["length"]
    return None
