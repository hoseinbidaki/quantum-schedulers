import json
import sys
from src.qschedulers.datasets.mqtbench_loader import (
    load_mqtbench_circuits,
    PRESET_SMALL,
)
from src.qschedulers.schedulers.round_robin import RoundRobinScheduler
from src.qschedulers.evaluation.experiment import run_experiment
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.orchestrator import Orchestrator
from src.qschedulers.schedulers import FANScheduler
from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane
import simpy.core as sp
import pandas as pd


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_dataset_example(config):
    circuits = load_mqtbench_circuits(config.get("preset", PRESET_SMALL))
    backends = [FakeHanoiV2(), FakeBrisbane()]
    scheduler = RoundRobinScheduler()
    df = run_experiment(
        scheduler,
        circuits,
        backends,
        csv_path=config.get("csv_path", "mqbench_rr_results.csv"),
    )
    print(df.head())


def run_cloud_example(config):
    env = sp.Environment()
    backends = [FakeHanoiV2(), FakeBrisbane()]
    qnodes = [
        QuantumNode(env, backend, name=name)
        for backend, name in zip(backends, ["Hanoi", "Brisbane"])
    ]
    tasks = [QuantumTask(**task) for task in config["tasks"]]
    scheduler = RoundRobinScheduler()
    orch = Orchestrator(env, scheduler, qnodes)
    orch.submit(tasks)
    env.run()
    results = orch.get_results()
    for r in results:
        print(r)
    if config.get("csv_path"):
        pd.DataFrame(results).to_csv(config["csv_path"], index=False)


def run_cloud_fan_example(config):
    env = sp.Environment()
    backends = [FakeHanoiV2(), FakeBrisbane()]
    qnodes = [
        QuantumNode(env, backend, name=name)
        for backend, name in zip(backends, ["Hanoi", "Brisbane"])
    ]
    tasks = [QuantumTask(**task) for task in config["tasks"]]
    scheduler = FANScheduler()
    orch = Orchestrator(env, scheduler, qnodes)
    orch.submit(tasks)
    env.run()
    results = orch.get_results()
    for r in results:
        print(r)
    if config.get("csv_path"):
        pd.DataFrame(results).to_csv(config["csv_path"], index=False)


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_example.py <config.json>")
        sys.exit(1)
    config_path = sys.argv[1]
    config = load_config(config_path)
    example_type = config.get("example_type", "dataset")
    if example_type == "dataset":
        run_dataset_example(config)
    elif example_type == "round_robin":
        run_cloud_example(config)
    elif example_type == "fan":
        run_cloud_fan_example(config)
    else:
        print(f"Unknown example_type: {example_type}")


if __name__ == "__main__":
    main()
