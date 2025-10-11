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

        # رسم نمودار
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

        print(f"✅ Plot saved successfully at:\n{filepath}")

    def get_test_QNodes(self):
        qnodes = [
            QuantumNode(self.env, FakeHanoiV2(), name="Hanoi"),
            QuantumNode(self.env, FakeBrisbane(), name="Brisbane"),
        ]
        return qnodes

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