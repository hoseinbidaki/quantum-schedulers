from src.Experiments.ExperimentsHandler import ExperimentsHandler
from src.qschedulers.schedulers.round_robin import RoundRobinScheduler


if __name__ == "__main__":

    schedulers = [RoundRobinScheduler()]

    exp = ExperimentsHandler()

    for scheduler in schedulers:
        scheduler_name = scheduler.__class__.__name__
        print(f"\nRunning experiments for: {scheduler_name}")

        tasks = exp.create_quantum_task_with_different_quantum_benchmark_algorithm()
        nodes = exp.create_cluster_of_5_different_quantum_nodes_27_to_127_qubit()

        exp.run(scheduler, tasks, nodes)

        exp.export_result_to_csv(scheduler_name)

    exp.make_plot(schedulers)
