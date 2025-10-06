from typing import Any
from qiskit import transpile
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from src.qschedulers.evaluation.metrics import estimate_fidelity_and_time
from .base import Scheduler


class FANScheduler(Scheduler):
    """
    Fidelity-Aware Network (FAN) Scheduler.
    Assigns tasks to qnodes based on fidelity/time tradeoff.
    """

    def __init__(self, shots: int = 1024):
        self.shots = shots

    def schedule(self, tasks: list[Any], qnodes: list[Any]) -> dict[str, Any]:
        if not qnodes:
            raise ValueError("No backends provided for scheduling.")

        assignments = []

        for task_id, task in enumerate(tasks):
            best_qnode = None
            best_score = -float("inf")
            best_meta = None

            for qnode in qnodes:
                try:
                    backend = qnode.backend
                    tqc = transpile(task.circuit, backend, optimization_level=3)
                    err_map = get_gate_error_map(backend)
                    fidelity, exec_time, swaps = estimate_fidelity_and_time(
                        tqc, backend, err_map, shots=self.shots
                    )
                    # Heuristic: balance fidelity vs. latency
                    score = fidelity / (exec_time + 1e-9)

                    if score > best_score:
                        best_score = score
                        best_qnode = qnode
                        best_meta = (fidelity, exec_time, swaps)
                except Exception as e:
                    continue  # skip invalid qnodes for this circuit

            if best_qnode is None:
                # Use continue if you don’t want the None backend to appear in the result.
                ...
                # continue
                # raise RuntimeError(f"No suitable qnode found for task {task_id}")

            assignments.append((task_id, best_qnode))

        return {
            "assignments": assignments,
            "metadata": {
                "policy": "fidelity_aware_network",
                "num_tasks": len(tasks),
                "num_backends": len(qnodes),
            },
        }
