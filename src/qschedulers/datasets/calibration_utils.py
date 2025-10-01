"""
Calibration Utilities
---------------------
Helpers to extract error rates and gate times from Qiskit backends.
"""

from typing import Dict, Tuple, Any



def get_gate_error_map(backend: Any) -> dict[tuple[str, tuple[int, ...]], dict[str, float]]:
    """
   Build a mapping from (gate_name, qubits) to error and duration.

   Args:
       backend: A Qiskit backend (real, or fake like FakeHanoiV2).

   Returns:
       Dictionary of {(gate_name, qubit_tuple): {"error": float, "length": float}}
   """
    err_map = {}
    try:
        props = backend.properties()
        for g in props.gates:
            name = g.name
            qtuple = tuple(g.qubits)
            err = None
            length = None
            for p in g.parameters:
                pname = getattr(p, "name", "")
                pval = getattr(p, "value", 0)
                if "gate_error" in pname:
                    err = pval
                if "gate_length" in pname or "gate_time" in pname:
                    length = pval
            err_map[(name.lower(), qtuple)] = {"error": err, "length": length}
    except Exception as e:
        pass

    return err_map
