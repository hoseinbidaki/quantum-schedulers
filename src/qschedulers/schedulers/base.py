from abc import abc, abstractmethod

from typing import Any

class Scheduler(abc.ABC):
    """
    Abstract base class for all quantum task schedulers.
    Every scheduler must implement the `schedule` method.
    """

    @abstractmethod
    def schedule(self, tasks: list[Any], backends: list[Any]) -> dict[str, Any]:
        """
        Schedule a list of tasks onto available backends.

        Args:
            tasks: A list of quantum tasks (e.g., circuits).
            backends: A list of quantum backends/devices (real or simulated).

        Returns:
            A dictionary mapping:
                - "assignments": list of (task_id, backend_id) pairs
                - "metadata": any additional info (logs, statistics, etc.)
        """
        pass