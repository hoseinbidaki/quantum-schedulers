from src.Experiments.ExperimentsHandler import ExperimentsHandler
from src.qschedulers.schedulers.round_robin import RoundRobinScheduler
from src.qschedulers.schedulers.fan import FANScheduler
from src.qschedulers.schedulers.fdf import FDFScheduler
from src.qschedulers.schedulers.sef import SEFScheduler


if __name__ == "__main__":

    schedulers = [RoundRobinScheduler(), FANScheduler(), FDFScheduler(), SEFScheduler()]

    exp = ExperimentsHandler()

    for scheduler in schedulers:
        scheduler_name = scheduler.__class__.__name__
        print(f"\nRunning experiments for: {scheduler_name}")

        tasks = exp.get_test_ready_tasks()
        nodes = exp.get_test_QNodes()

        exp.run(scheduler, tasks, nodes)

        exp.export_result_to_csv(scheduler_name)


    exp.make_plot(schedulers)