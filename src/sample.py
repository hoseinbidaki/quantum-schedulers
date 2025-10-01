from qschedulers.datasets.mqtbench_loader import load_mqtbench_circuits, PRESET_SMALL
from qschedulers.schedulers.round_robin import RoundRobinScheduler
from qschedulers.evaluation.experiment import run_experiment
from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane

# Load circuits
circuits = load_mqtbench_circuits(PRESET_SMALL)

# Backends
backends = [FakeHanoiV2(), FakeBrisbane()]

# Scheduler
scheduler = RoundRobinScheduler()

# Run experiment
df = run_experiment(scheduler, circuits, backends, csv_path="mqbench_rr_results.csv")
print(df.head())
