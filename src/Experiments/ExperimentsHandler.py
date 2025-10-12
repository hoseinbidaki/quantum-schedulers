from src.qschedulers.cloud.orchestrator import Orchestrator

from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask

from mqt.bench import get_benchmark, BenchmarkLevel

from qiskit_ibm_runtime.fake_provider import *

import simpy as sp

import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

import numpy as np
from qiskit import QuantumCircuit
import re

from src.logger_config import setup_logger
logger = setup_logger()

class ExperimentsHandler():
    """
    simple run some task on some node and return results
    """
    def __init__(self):
        self.env = sp.Environment()
        self.results = {}


    def run(self, scheduler, Qtasks, Qnodes):
        orch = Orchestrator(self.env, scheduler, Qnodes)
        orch.submit(Qtasks)
        self.env.run()
        scheduler_name = scheduler.__class__.__name__
        self.results[scheduler_name] = orch.get_results()
        return self.results[scheduler_name]

    def export_result_to_csv(self, scheduler_name):
        csv_path = scheduler_name + ".csv"
        if self.results[scheduler_name]:
            fieldnames = list(self.results[scheduler_name][0].keys())
            with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results[scheduler_name])

    def make_plot(self, schedulers, save_dir="plots"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        plots_path = os.path.join(base_dir, save_dir)
        os.makedirs(plots_path, exist_ok=True)

        all_means = {}
        for scheduler in schedulers:
            scheduler_name = scheduler.__class__.__name__
            df = pd.DataFrame(self.results[scheduler_name])
            numeric_cols = ["waiting_time", "turnaround_time", "fidelity", "exec_time_est", "swap_count"]
            all_means[scheduler_name] = df[numeric_cols].mean()

        mean_df = pd.DataFrame(all_means)


        plt.figure(figsize=(9, 5))
        mean_df.plot(kind="bar", width=0.7)
        plt.title("Average Metrics Comparison Across Algorithms")
        plt.ylabel("Average Value")
        plt.xlabel("Metric")
        plt.xticks(rotation=30, ha="right")
        plt.grid(axis='y', linestyle="--", alpha=0.6)
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"plot_{timestamp}.png"
        filepath = os.path.join(plots_path, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()

        logger.info(f"✅ Plot saved successfully at:\n{filepath}")


    def get_test_QNodes(self):
        qnodes = [
            QuantumNode(self.env, FakeHanoiV2(), name="Hanoi"),
            QuantumNode(self.env, FakeBrisbane(), name="Brisbane"),
        ]
        return qnodes

    def create_cluster_of_5_different_quantum_nodes_27_to_127_qubit(self):
        """
        Create and return a cluster of five simulated quantum nodes,
        each representing a distinct IBM Quantum device with different
        qubit capacities (ranging roughly from 27 to 127 qubits).

        These "Fake" backends are simulation stubs provided by Qiskit
        to emulate real IBM Quantum hardware, useful for testing
        distributed or federated quantum scheduling without access
        to actual quantum machines.

        Returns:
            list[QuantumNode]: A list containing five QuantumNode instances,
            each initialized with a different fake backend and unique name.
        """
        qnodes = [
            QuantumNode(self.env, FakeAuckland(), name="Auckland"),  # 27-qubit simulated backend
            QuantumNode(self.env, FakeHanoiV2(), name="Hanoi"),  # 27-qubit simulator (variant)
            QuantumNode(self.env, FakeKolkataV2(), name="Kolkata"),  # 27-qubit simulator (variant)
            QuantumNode(self.env, FakeBrisbane(), name="Brisbane"),  # 127-qubit simulated backend
            QuantumNode(self.env, FakeSherbrooke(), name="Sherbrooke")  # 127-qubit simulated backend
        ]
        return qnodes

    def create_quantum_task_with_different_quantum_benchmark_algorithm(
            self,
            n_tasks: int = 100,
            seed: int = 1234,
            lam: float = 0.6,  # Poisson arrival rate (average task arrival rate)
            min_qubits: int = 2,
            max_qubits: int = 14,
            # max_qubits: int = 27,
            min_depth: int = 3,
            max_depth: int = 14,
            # max_depth: int = 30,
            pad_heavy: bool = False,       # optionally skip depth padding for heavy benchmarks

    ):
        """
        Create a list of QuantumTask objects using all 30 benchmark algorithms
        available in MQT Bench. Each task randomly selects one algorithm,
        a qubit count between 2–27, and an approximate initial circuit depth
        between 3–30 layers (before transpilation).

        Task arrivals follow a Poisson process to emulate task arrivals
        at a cloud quantum data center.

        Args:
            n_tasks (int): Total number of quantum tasks to generate.
            seed (int): Random seed for reproducibility.
            lam (float): Poisson process rate parameter (λ).
            min_qubits, max_qubits (int): Range of circuit sizes (number of qubits).
            min_depth, max_depth (int): Approximate target circuit depth before transpilation.

        Returns:
            list[QuantumTask]: A list of generated quantum tasks with Poisson-distributed arrivals.
        """

        rng = np.random.default_rng(seed)

        # --- Full list of 30 supported benchmark algorithms ---
        benchmark_pool = [
            "ae",  # Amplitude Estimation
            "bmw_quark_cardinality",  # QUARK Cardinality Circuit
            "bmw_quark_copula",  # QUARK Copula Circuit
            "bv",  # Bernstein–Vazirani
            "cdkm_ripple_carry_adder",  # CDKM Ripple-Carry Adder
            "dj",  # Deutsch–Jozsa
            "draper_qft_adder",  # Draper QFT Adder
            "full_adder",  # Full Adder
            "ghz",  # GHZ State
            "graphstate",  # Graph State
            "grover",  # Grover’s Algorithm
            "half_adder",  # Half Adder
            "hhl",  # Harrow–Hassidim–Lloyd Algorithm
            "hrs_cumulative_multiplier",  # Häner–Roetteler–Svore Cumulative Multiplier
            "modular_adder",  # Modular Adder
            "multiplier",  # Multiplier
            "qaoa",  # Quantum Approximate Optimization Algorithm
            "qft",  # Quantum Fourier Transform
            "qftentangled",  # QFT with GHZ input
            "qnn",  # Quantum Neural Network
            "qpeexact",  # Quantum Phase Estimation (exact phase)
            "qpeinexact",  # Quantum Phase Estimation (inexact phase)
            "qwalk",  # Quantum Walk
            "randomcircuit",  # Random Quantum Circuit
            "rg_qft_multiplier",  # Ruiz–Garcia QFT Multiplier
            "shor",  # Shor’s Algorithm
            "vbe_ripple_carry_adder",  # Vedral–Barenco–Eker Ripple-Carry Adder
            "vqe_real_amp",  # VQE (Real Amplitudes ansatz)
            "vqe_su2",  # VQE (Efficient SU2 ansatz)
            "vqe_two_local",  # VQE (Two-Local ansatz)
            "wstate",  # W-State Preparation
        ]

        # Simple, conservative per-benchmark sizing hints (will also parse errors dynamically).
        # Many arithmetic/adder-style circuits require even qubit counts.
        EVEN_REQUIRED = {
            "modular_adder",
            "multiplier",
            "cdkm_ripple_carry_adder",
            "vbe_ripple_carry_adder",
            "draper_qft_adder",
            "rg_qft_multiplier",
            "hrs_cumulative_multiplier",
            "full_adder",
            "half_adder",
        }

        # Upper bounds for heavy circuits (kept small to prevent massive unrolling)
        HEAVY_CAP = {
            "shor": 6,
            "multiplier": 8,
            "rg_qft_multiplier": 8,
            "hrs_cumulative_multiplier": 8,
            "modular_adder": 8,
            "cdkm_ripple_carry_adder": 8,
            "vbe_ripple_carry_adder": 8,
            "draper_qft_adder": 8,
            "full_adder": 6,
            "half_adder": 6,
        }

        # --- Poisson arrivals: first arrives at t=0, then cumulative sum of exponential gaps ---
        inter_arrivals = rng.exponential(1.0 / lam, size=max(0, n_tasks - 1))
        arrival_times = np.concatenate([[0.0], np.cumsum(inter_arrivals)]) if n_tasks > 0 else np.array([])

        # Optional: log arrival times (uncomment if you use a logger)
        # from src.logger_config import setup_logger
        # setup_logger().info(f"arrival_times is {arrival_times}")

        tasks = []

        # --- Light padding to approximate pre-transpilation depth without changing logic meaning ---
        def _pad_to_depth(circ: QuantumCircuit, target_depth: int) -> QuantumCircuit:
            """Increase circuit depth via barriers + tiny RX layers (no semantic change)."""
            try:
                current = circ.depth()
            except Exception:
                current = 0
            if current is None or current >= target_depth:
                return circ
            q = circ.num_qubits
            while circ.depth() < target_depth:
                circ.barrier()
                for qi in range(q):
                    angle = ((qi + 1) * np.pi) / 256.0
                    circ.rx(angle if (qi % 2 == 0) else -angle, qi)
            return circ

        def _enforce_rules(name: str, size: int) -> int:
            """Apply simple per-benchmark constraints before circuit generation."""
            # Heavy caps (limit maximum size for problematic algorithms)
            if name in HEAVY_CAP:
                size = min(size, HEAVY_CAP[name])
            # Enforce even qubits for arithmetic-style circuits
            if name in EVEN_REQUIRED and (size % 2 == 1):
                size += 1
            # Clamp to global bounds
            return max(min_qubits, min(size, max_qubits))

        def _adapt_from_error(msg: str, size: int) -> int:
            """
            Parse common MQT Bench ValueError messages to adjust circuit_size.
            Examples:
              - 'num_qubits must be an even integer ≥ 2'
              - 'num_qubits must be ≥ 4'
            """
            # Enforce even if error mentions it
            if "even" in msg.lower() and (size % 2 == 1):
                size += 1
            # Extract lower bounds like '≥ 4' or '>= 4'
            m = re.search(r"[≥>]=?\s*(\d+)", msg)
            if m:
                lb = int(m.group(1))
                if size < lb:
                    size = lb
            # Safety clamp
            return max(min_qubits, min(size, max_qubits))

        for i in range(n_tasks):
            benchmark_name = rng.choice(benchmark_pool)
            # Random target depth and size (then adjusted by rules)
            target_depth = int(rng.integers(min_depth, max_depth + 1))
            circuit_size = int(rng.integers(min_qubits, max_qubits + 1))

            # Retry loop: adjust size based on rules or error messages; switch algorithm if needed
            attempts = 0
            success = False
            while attempts < 8 and not success:
                attempts += 1
                size_try = _enforce_rules(benchmark_name, circuit_size)
                try:
                    circuit = get_benchmark(
                        benchmark_name,
                        level=BenchmarkLevel.ALG,
                        circuit_size=size_try
                    )
                    success = True
                except ValueError as e:
                    circuit_size = _adapt_from_error(str(e), size_try)
                    # Occasionally swap algorithm if still failing
                    if attempts in (4, 7):
                        benchmark_name = rng.choice(benchmark_pool)

            if not success:
                # Last resort: pick a permissive algorithm and small size
                fallback = rng.choice(["qft", "ghz", "graphstate"])
                size_try = _enforce_rules(fallback, circuit_size)
                circuit = get_benchmark(fallback, level=BenchmarkLevel.ALG, circuit_size=size_try)
                benchmark_name = fallback  # record actual algo used

            # Depth padding (skip for heavy circuits if pad_heavy is False)
            if (benchmark_name not in HEAVY_CAP) or pad_heavy:
                circuit = _pad_to_depth(circuit, target_depth)

            # Build the task
            tasks.append(
                QuantumTask(
                    id=i,
                    circuit=circuit,
                    arrival_time=float(arrival_times[i]),
                )
            )

        return tasks

    def get_test_ready_tasks(self):
        tasks = [
            QuantumTask(
                id=0,
                circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=5),
                arrival_time=0,
            ),
            QuantumTask(
                id=1,
                circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=10),
                arrival_time=1,
            ),
            QuantumTask(
                id=2,
                circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=30),
                arrival_time=1,
            ),
            QuantumTask(
                id=3,
                circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=5),
                arrival_time=5,
            ),
        ]
        return tasks