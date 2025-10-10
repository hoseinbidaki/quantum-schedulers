from typing import Any
from src.logger_config import setup_logger
from qiskit import transpile
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from src.qschedulers.evaluation.metrics import estimate_fidelity_and_time
from .base import Scheduler

logger = setup_logger()

class FANScheduler(Scheduler):
    """
    Fidelity-Aware Network (FAN) Scheduler.
    Assigns tasks to qnodes based on fidelity/time tradeoff.
    """

    def __init__(self, shots: int = 1024):
        self.shots = shots
        logger.info(f"Initialized FANScheduler with shots={shots}.")

    def schedule(self, tasks: list[Any], qnodes: list[Any]) -> dict[str, Any]:
        logger.info(f"Scheduling {len(tasks)} tasks across {len(qnodes)} qnodes using FAN policy.")
        if not qnodes:
            logger.error("No backends provided for scheduling.")
            raise ValueError("No backends provided for scheduling.")

        assignments = []

        for task_id, task in enumerate(tasks):
            best_qnode = None
            best_score = -float("inf")
            best_meta = None
            logger.debug(f"Evaluating task {task_id} for best qnode assignment.")

            for qnode in qnodes:
                try:
                    backend = qnode.backend
                    tqc = transpile(task.circuit, backend, optimization_level=3)
                    err_map = get_gate_error_map(backend)
                    fidelity, exec_time, swaps = estimate_fidelity_and_time(
                        tqc, backend, err_map, shots=self.shots
                    )
                    score = fidelity / (exec_time + 1e-9)
                    logger.debug(f"Task {task_id} on backend {getattr(backend, 'name', backend)}: fidelity={fidelity}, exec_time={exec_time}, score={score}")
                    if score > best_score:
                        best_score = score
                        best_qnode = qnode
                        best_meta = (fidelity, exec_time, swaps)
                except Exception as e:
                    logger.warning(f"Error evaluating task {task_id} on backend {getattr(qnode, 'name', qnode)}: {e}")
                    continue

            if best_qnode is None:
                logger.error(f"No suitable qnode found for task {task_id}.")
                ...

            assignments.append((task_id, best_qnode))

        logger.info(f"Completed scheduling. Assignments: {assignments}")
        return {
            "assignments": assignments,
            "metadata": {
                "policy": "fidelity_aware_network",
                "num_tasks": len(tasks),
                "num_backends": len(qnodes),
            },
        }
