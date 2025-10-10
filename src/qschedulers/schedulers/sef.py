from typing import Any
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from .base import Scheduler


class SEFScheduler(Scheduler):
    """
    Smallest Error First (SEF) Scheduler.
    Assigns each QTask to the QNode (backend) with the smallest average error rate of all gate operations.
    """

    def schedule(self, tasks: list[Any], qnodes: list[Any]) -> dict[str, Any]:
        if not qnodes:
            raise ValueError("No backends provided for scheduling.")

        assignments = []

        # Precompute average error for each qnode
        qnode_avg_errors = []
        for qnode in qnodes:
            backend = qnode.backend
            err_map = get_gate_error_map(backend)
            errors = [
                v.get("error", 1e-3)
                for v in err_map.values()
                if v.get("error") is not None
            ]
            avg_error = sum(errors) / len(errors) if errors else 1e-3
            qnode_avg_errors.append(avg_error)

        for task_id, task in enumerate(tasks):
            # Find qnode with smallest average error
            min_error_idx = min(range(len(qnodes)), key=lambda i: qnode_avg_errors[i])
            best_qnode = qnodes[min_error_idx]
            assignments.append((task_id, best_qnode))

        return {
            "assignments": assignments,
            "metadata": {
                "policy": "smallest_error_first",
                "num_tasks": len(tasks),
                "num_backends": len(qnodes),
            },
        }
