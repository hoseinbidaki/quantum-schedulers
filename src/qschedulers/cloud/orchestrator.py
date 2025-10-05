"""
Orchestrator
------------
Coordinates tasks, schedulers, and quantum nodes inside a qsimpy environment.
"""

import simpy.core as sp
from qiskit import transpile

from qschedulers.cloud.qtask import QuantumTask
from qschedulers.cloud.qnode import QuantumNode
from qschedulers.schedulers.base import Scheduler
from qschedulers.datasets.calibration_utils import get_gate_error_map
from qschedulers.evaluation.metrics import estimate_fidelity_and_time


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
        result = self.scheduler.schedule(tasks, self.qnodes)
        assignments = result["assignments"]
        for task_id, qnode in assignments:
            task = tasks[task_id]
            self.env.process(self._run_task(task, qnode))

    def _run_task(self, task: QuantumTask, qnode: QuantumNode):
        # Wait until task arrival
        yield self.env.timeout(task.arrival_time)
        arrival = self.env.now

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
