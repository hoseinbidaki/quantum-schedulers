# Quantum Schedulers

**Quantum Schedulers** is a modular Python package for experimenting with **quantum task scheduling** in cloud and simulated environments.
It provides:

* 📚 **Dataset utilities** for loading circuits from [MQTBench](https://github.com/cda-tum/mqt-bench) and extracting backend calibration data.
* ⚡ **Pluggable schedulers** — start with a simple **Round-Robin scheduler**, and extend with greedy, RL-based, or custom algorithms.
* 📊 **Evaluation tools** to estimate fidelity, execution time, and resource usage of scheduled circuits.
* 📂 **CSV output** for easy integration into ML workflows or analysis.
* ☁️ **Cloud orchestration module** — the new `cloud` module (`src/qschedulers/cloud`) provides tools for simulating and managing quantum tasks in cloud environments, including orchestrators, environments, quantum nodes, and tasks.


---

## 📖 Running the Project with `uv`

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, modern Python package management.

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/quantum-schedulers.git
cd quantum-schedulers
```

### 2. Create a virtual environment

```bash
uv venv
```

This will create a `.venv` folder inside the project.
Activate it:

* **Linux/macOS**

  ```bash
  source .venv/bin/activate
  ```
* **Windows (PowerShell)**

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Install dependencies

```bash
uv sync
```

This reads the `pyproject.toml` and installs all required dependencies (Qiskit, MQTBench, pandas, etc.).

### 4. Run an example

```bash
uv run python -m src.examples.sample_cloud
```

Or open one of the example notebooks under `examples/` in Jupyter.

---


