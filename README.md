# Quantum Schedulers

**Quantum Schedulers** is a modular Python package for experimenting with **quantum task scheduling** in cloud and simulated environments.
It provides:

* 📚 **Dataset utilities** for loading circuits from [MQTBench](https://github.com/cda-tum/mqt-bench) and extracting backend calibration data.
* ⚡ **Pluggable schedulers** — start with a simple **Round-Robin scheduler**, and extend with greedy, RL-based, or custom algorithms.
* 📊 **Evaluation tools** to estimate fidelity, execution time, and resource usage of scheduled circuits.
* 📂 **CSV output** for easy integration into ML workflows or analysis.

### ✨ Example workflow

```python
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

# Run experiment and save results to CSV
df = run_experiment(scheduler, circuits, backends, csv_path="mqbench_rr_results.csv")
print(df.head())
```

### 🔑 Features

* Easy-to-extend **Scheduler API** (`Scheduler` base class).
* Built-in **Round-Robin scheduler**.
* Backend-aware fidelity & runtime estimation.
* Ready-to-use **experiment runner** with CSV export.
* Modular structure for community contributions.

---

🚀 Designed for researchers and developers exploring **quantum cloud orchestration** and **task scheduling** in the NISQ era.

---
