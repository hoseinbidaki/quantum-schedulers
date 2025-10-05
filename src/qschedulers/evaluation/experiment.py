"""
Experiment Runner
-----------------
Runs a scheduler on circuits + backends and outputs CSV with results.
"""

import pandas as pd
from qiskit import transpile
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from src.qschedulers.evaluation.metrics import estimate_fidelity_and_time


def run_experiment(scheduler, circuits, backends, shots=1024, csv_path="results.csv"):
    """
    Run an experiment with a scheduler and save results to CSV.

    Args:
        scheduler: A Scheduler instance (e.g. RoundRobinScheduler()).
        circuits: list of QuantumCircuit objects.
        backends: list of Qiskit backends.
        shots: number of shots for estimation.
        csv_path: output CSV file path.

    Returns:
        pandas.DataFrame with results.
    """
    schedule_result = scheduler.schedule(circuits, backends)
    assignments = schedule_result["assignments"]

    rows = []
    for task_id, backend in assignments:
        qc = circuits[task_id]
        row = {"task_id": task_id, "backend": backend.name}

        try:
            tqc = transpile(qc, backend=backend, optimization_level=3)
            err_map = get_gate_error_map(backend)
            fidelity, exec_time, swaps = estimate_fidelity_and_time(tqc, backend, err_map, shots=shots)
            row.update({
                "status": "success",
                "fidelity": fidelity,
                "exec_time": exec_time,
                "swap_count": swaps,
                "depth": tqc.depth(),
            })
        except Exception as e:
            row.update({
                "status": "fail",
                "error": str(e),
                "fidelity": None,
                "exec_time": None,
                "swap_count": None,
                "depth": None,
            })

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"Saved results to {csv_path}")
    return df
