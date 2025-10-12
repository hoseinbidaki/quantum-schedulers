from typing import Any
from src.logger_config import setup_logger
from .base import Scheduler

logger = setup_logger()


class RoundRobinScheduler(Scheduler):
    """
    Round-Robin Scheduler:
    Assigns tasks to backends in a rotating sequence.
    """

    def __init__(self):
        self._counter = 0  # keeps track of the next backend index
        logger.info("Initialized RoundRobinScheduler with counter set to 0.")

    def schedule(self, tasks: list[Any], qnodes: list[Any]) -> dict[str, Any]:
        logger.info(
            f"Scheduling {len(tasks)} tasks across {len(qnodes)} qnodes using RoundRobin policy."
        )
        if not qnodes:
            logger.error("No backends provided for scheduling.")
            raise ValueError("No backends provided for scheduling.")

        assignments = []
        backend_count = len(qnodes)
        from collections import defaultdict
        assignment_details = defaultdict(list)

        for task_id, task in enumerate(tasks):
            backend_index = self._counter % backend_count
            backend = qnodes[backend_index]
            logger.debug(
                f"Assigning task {task_id} to backend index {backend_index} ({getattr(backend, 'name', backend)})."
            )
            assignments.append((task_id, backend))
            logger.info(f"task #{task_id} assign to {backend.name}")
            assignment_details[backend.name].append(task_id)
            self._counter += 1

        logger.info(f"Completed scheduling. Assignments: {assignments}")
        for key in assignment_details.keys():
            logger.info(f"in device {key} assigned: {assignment_details[key]}")
        return {
            "assignments": assignments,
            "metadata": {
                "policy": "round_robin",
                "num_tasks": len(tasks),
                "num_backends": backend_count,
            },
        }
