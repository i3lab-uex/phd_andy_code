# Generated from PROBE using Acceleo
from typing import List
from python_application.generated_code.enumerations.DeviceType import DeviceType
from python_application.generated_code.model.Dataset import Dataset
from python_application.generated_code.model.OptimizationTask import OptimizationTask
from python_application.generated_code.model.Experiment import Experiment


def _simulate_experiment(task: OptimizationTask, experiment: Experiment) -> str:
    """
    Simulates the execution of an experiment. This is a placeholder function for future injection.
    :return: Status message of the simulation
    """
    output = []
    output.append(f"   • Simulating experiment: {experiment.name}...")
    output.append(
        f"     → Using model: {task.foundation_model.name} ({task.foundation_model.type})"
    )
    output.append(f"     → Optimizing metric: {task.optimization_metric.name}")
    output.append(f"     → Sample: {experiment.sample.filename}")
    output.append(
        f"     → Stop Conditions: {[type(c).__name__ for c in experiment.stop_condition]}"
    )
    output.append(f"     ✓ Simulation complete.")
    return "\n".join(output)


class PROBE:
    """Root container for device, datasets and optimization tasks."""

    def __init__(
        self,
        device: DeviceType,
        dataset: List[Dataset],
        optimization_task: List[OptimizationTask],
    ):
        """
        :param device: device of the PROBE
        :param dataset: dataset of the PROBE
        :param optimization_task: optimization_task of the PROBE
        """
        self.device = device
        self.dataset = dataset
        self.optimization_task = optimization_task

    def get_experiments_for_task(self, task_name: str) -> List[str]:
        for task in self.optimization_task:
            if task.name == task_name:
                return [exp.name for exp in task.experiment]
        return []

    def run_all_experiments_for_task(self, task_name: str) -> str:
        for task in self.optimization_task:
            if task.name == task_name:
                output = [f"▶ Running all experiments for task: {task.name}"]
                for experiment in task.experiment:
                    output.append(_simulate_experiment(task, experiment))
                return "\n".join(output)
        return f"⚠ Task '{task_name}' not found."

    def run_single_experiment(self, task_name: str, experiment_name: str) -> str:
        for task in self.optimization_task:
            if task.name == task_name:
                for experiment in task.experiment:
                    if experiment.name == experiment_name:
                        return _simulate_experiment(task, experiment)
                return (
                    f"⚠ Experiment '{experiment_name}' not found in task '{task_name}'"
                )
        return f"⚠ Task '{task_name}' not found."
