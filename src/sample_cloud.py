from mqt.bench import get_benchmark, BenchmarkLevel
import simpy.core as sp
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.schedulers import Scheduler, RoundRobinScheduler
from src.qschedulers.cloud.orchestrator import Orchestrator


if __name__ == "__main__":
    from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane
    from mqt.bench import get_benchmark

    # Environment
    env = sp.Environment()

    # Backends wrapped in QNodes
    qnodes = [
        QuantumNode(env, FakeHanoiV2(), name="Hanoi"),
        QuantumNode(env, FakeBrisbane(), name="Brisbane"),
    ]

    # Example tasks (circuits with different arrival times)
    tasks = [
        QuantumTask(id=3, circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=30), arrival_time=0),   # arrives while others still running
        QuantumTask(id=0, circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=10), arrival_time=1),  # may fail on small backend
        QuantumTask(id=1, circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=5), arrival_time=0),   # shares arrival, must wait
        QuantumTask(id=2, circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=15), arrival_time=0),  # likely too big for FakeHanoi
    ]


    # Scheduler
    scheduler = RoundRobinScheduler()
    orch = Orchestrator(env, scheduler, qnodes)

    # Submit tasks to orchestrator
    orch.submit(tasks)

    # Run simulation
    env.run()

    # Show results
    for r in orch.results:
        print(r)