from typing import Any

from .base import Scheduler


class RoundRobinScheduler(Scheduler):
    """
       Round-Robin Scheduler:
       Assigns tasks to backends in a rotating sequence.
       """

    def __init__(self):
        self._counter = 0  # keeps track of the next backend index


    def schedule(self, tasks: list[Any], backends: list[Any]) -> dict[str, Any]:
        if not backends:
            raise ValueError("No backends provided for scheduling.")

        assignments = []
        backend_count = len(backends)

        for task_id, task in enumerate(tasks):
            backend_index = self._counter % backend_count
            backend = backends[backend_index]

            assignments.append((task_id, backend))

            self._counter += 1

        return {
            "assignments": assignments,
            "metadata": {
                "policy": "round_robin",
                "num_tasks": len(tasks),
                "num_backends": backend_count,
            },
        }
