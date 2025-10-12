"""
Orchestrator
------------
Coordinates tasks, schedulers, and quantum nodes inside a qsimpy environment.
"""

import simpy.core as sp
import simpy
from qiskit import transpile

from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.schedulers.base import Scheduler
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from src.qschedulers.evaluation.metrics import estimate_fidelity_and_time
from src.logger_config import setup_logger

logger = setup_logger()

class Orchestrator:
    def __init__(
        self,
        env: sp.Environment,
        scheduler: Scheduler,
        qnodes: list[QuantumNode],
        shots: int = 1024,
    ):
        self.env = env
        self.scheduler = scheduler
        self.qnodes = qnodes
        self.shots = shots
        self.results = []

    def submit(self, tasks: list[QuantumTask]):
        logger.info(f"Submitting {len(tasks)} tasks")
        logger.info("Calling scheduler.schedule(...) now")
        result = self.scheduler.schedule(tasks, self.qnodes)
        logger.info("scheduler.schedule returned")
        assignments = result["assignments"]
        for task_id, qnode in assignments:
            task = tasks[task_id]
            self.env.process(self._run_task(task, qnode))

    def _run_task(self, task: QuantumTask, qnode: QuantumNode):
        # Wait until task arrival
        yield self.env.timeout(task.arrival_time)
        arrival = self.env.now

        if not qnode:
            self.results.append(
                {
                    "task_id": task.id,
                    "backend": "",
                    "status": "failed",
                    "message": "error_message",
                    "arrival_time": arrival,
                    "start_time": -1,
                    "finish_time": -1,
                    "waiting_time": -1,
                    "turnaround_time": -1,
                    "fidelity": -1,
                    "exec_time_est": -1,
                    "swap_count": -1,
                }
            )
            return None
        with qnode.request() as req:
            yield req
            start = self.env.now
            waiting_time = start - arrival

            status = "success"
            error_message = None

            # Estimate exec time as service time
            try:
                tqc = transpile(
                    task.circuit, backend=qnode.backend, optimization_level=3
                )

                err_map = get_gate_error_map(qnode.backend)
                fidelity, exec_time, swaps = estimate_fidelity_and_time(
                    tqc, qnode.backend, err_map, shots=self.shots
                )
                service_time = exec_time
            except Exception as e:
                error_message = e
                status = "failed"
                fidelity, exec_time, swaps = None, None, None
                service_time = 1.0

            # This line is where the execution is simulated in time
            yield self.env.timeout(service_time)

            finish = self.env.now
            turnaround_time = finish - arrival

            self.results.append(
                {
                    "task_id": task.id,
                    "backend": qnode.backend.name,
                    "status": status,
                    "message": error_message,
                    "arrival_time": arrival,
                    "start_time": start,
                    "finish_time": finish,
                    "waiting_time": waiting_time,
                    "turnaround_time": turnaround_time,
                    "fidelity": fidelity,
                    "exec_time_est": exec_time,
                    "swap_count": swaps,
                }
            )

    def get_results(self):
        return self.results
