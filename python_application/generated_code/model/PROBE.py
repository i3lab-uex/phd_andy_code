# Generated from PROBE using Acceleo
from typing import List, Dict, Any
from python_application.generated_code.enumerations.DeviceType import DeviceType
from python_application.generated_code.model.Dataset import Dataset
from python_application.generated_code.model.OptimizationTask import OptimizationTask
import os


class PROBE:
    """
    Represents a PROBE instance for running optimization tasks.
    This class provides methods to run optimization tasks using genetic algorithms
    and prompts, allowing for both whole task optimization and specific experiment optimization.
    """

    def __init__(
        self,
        device: DeviceType,
        dataset: List[Dataset],
        optimization_task: List[OptimizationTask],
    ):
        """
        Initialize a PROBE instance.

        Params:
        :param device: device of the PROBE
        :param dataset: dataset of the PROBE
        :param optimization_task: optimization_task of the PROBE
        """
        self.device = device
        self.dataset = dataset
        self.optimization_task = optimization_task

    def run_optimization_whole_task(
        self, task_name: str, population_size: int = 100, seed: int = 1
    ) -> Dict[str, Any]:
        """
        Run SAM optimization for all experiments in a task using PROBE configuration.

        Args:
            task_name (str): Name of the optimization task
            population_size (int, optional): Population size for genetic algorithm. Defaults to 100.
            seed (int, optional): Random seed for reproducibility. Defaults to 1.

        Returns:
            Dict[str, Any]: Experiment results including metrics and execution time
        """
        try:
            from python_application.static_code.genetic_algorithm.optimization_executor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.log_capture import global_stream_capture

            # Find the specified task
            target_task = None
            for task in self.optimization_task:
                if task.name == task_name:
                    target_task = task
                    break

            if not target_task:
                return {
                    "status": "error",
                    "message": f"Task '{task_name}' not found",
                    "results": None,
                }

            # Create an executor with stream capture and run optimization for all experiments
            executor = OptimizationExecutor(self, global_stream_capture)

            # Use context manager to capture all output
            with global_stream_capture.capture():
                results = executor.run_task_optimization(
                    task=target_task,
                    population_size=population_size,
                    seed=seed,
                    use_prompts=False,
                )

            return {
                "status": "success",
                "message": f"Optimization completed for task '{task_name}'",
                "results": results,
            }

        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import optimization modules: {e}",
                "results": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Experiment execution failed: {e}",
                "results": None,
            }

    def run_optimization_using_task_experiment(
        self,
        task_name: str,
        experiment_name: str,
        population_size: int = 100,
        seed: int = 1,
    ) -> Dict[str, Any]:
        """
        Run SAM optimization for a specific experiment using PROBE configuration.

        Args:
            task_name (str): Name of the optimization task
            experiment_name (str): Name of the specific experiment
            population_size (int, optional): Population size for genetic algorithm. Defaults to 100.
            seed (int, optional): Random seed for reproducibility. Defaults to 1.

        Returns:
            Dict[str, Any]: Experiment results including metrics and execution time
        """
        try:
            from python_application.static_code.genetic_algorithm.optimization_executor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.log_capture import global_stream_capture

            # Find the specified task and experiment
            target_task = None
            target_experiment = None

            for task in self.optimization_task:
                if task.name == task_name:
                    target_task = task
                    for experiment in task.experiment:
                        if experiment.name == experiment_name:
                            target_experiment = experiment
                            break
                    break

            if not target_task:
                return {
                    "status": "error",
                    "message": f"Task '{task_name}' not found",
                    "results": None,
                }

            if not target_experiment:
                return {
                    "status": "error",
                    "message": f"Experiment '{experiment_name}' not found in task '{task_name}'",
                    "results": None,
                }

            # Create an executor with stream capture and run optimization for a specific experiment
            executor = OptimizationExecutor(self, global_stream_capture)

            # Use context manager to capture all output
            with global_stream_capture.capture():
                results = executor.run_single_experiment_optimization(
                    task=target_task,
                    experiment=target_experiment,
                    population_size=population_size,
                    seed=seed,
                    use_prompts=False,
                )

            return {
                "status": "success",
                "message": f"Optimization completed for experiment '{experiment_name}'",
                "results": results,
            }

        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import optimization modules: {e}",
                "results": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Experiment execution failed: {e}",
                "results": None,
            }

    def run_prompt_optimization_whole_task(
        self,
        task_name: str,
        prompts_path: str,
        population_size: int = 100,
        seed: int = 1,
    ) -> Dict[str, Any]:
        """
        Run SAM optimization for all experiments in a task using prompts from JSON files.

        Args:
            task_name (str): Name of the optimization task
            prompts_path (str): Path to the directory containing JSON prompt files
            population_size (int, optional): Population size for genetic algorithm. Defaults to 100.
            seed (int, optional): Random seed for reproducibility. Defaults to 1.

        Returns:
            Dict[str, Any]: Experiment results including metrics and execution time
        """
        try:
            from python_application.static_code.genetic_algorithm.optimization_executor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.log_capture import global_stream_capture

            # Find the specified task
            target_task = None
            for task in self.optimization_task:
                if task.name == task_name:
                    target_task = task
                    break

            if not target_task:
                return {
                    "status": "error",
                    "message": f"Task '{task_name}' not found",
                    "results": None,
                }

            # Validate prompts path
            if not os.path.exists(prompts_path):
                return {
                    "status": "error",
                    "message": f"Prompts path does not exist: {prompts_path}",
                    "results": None,
                }

            # Create an executor with stream capture and run optimization for all experiments with prompts
            executor = OptimizationExecutor(self, global_stream_capture)

            # Use context manager to capture all output
            with global_stream_capture.capture():
                results = executor.run_task_optimization(
                    task=target_task,
                    population_size=population_size,
                    seed=seed,
                    use_prompts=True,
                    prompts_path=prompts_path,
                )

            return {
                "status": "success",
                "message": f"Prompt-based optimization completed for task '{task_name}'",
                "results": results,
            }

        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import optimization modules: {e}",
                "results": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Experiment execution failed: {e}",
                "results": None,
            }

    def run_prompt_optimization_using_task_experiment(
        self,
        task_name: str,
        experiment_name: str,
        prompts_path: str,
        population_size: int = 100,
        seed: int = 1,
    ) -> Dict[str, Any]:
        """
        Run SAM optimization for a specific experiment using prompts from JSON files.

        Args:
            task_name (str): Name of the optimization task
            experiment_name (str): Name of the specific experiment
            prompts_path (str): Path to the directory containing JSON prompt files
            population_size (int, optional): Population size for genetic algorithm. Defaults to 100.
            seed (int, optional): Random seed for reproducibility. Defaults to 1.

        Returns:
            Dict[str, Any]: Experiment results including metrics and execution time
        """
        try:
            from python_application.static_code.genetic_algorithm.optimization_executor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.log_capture import global_stream_capture

            # Find the specified task and experiment
            target_task = None
            target_experiment = None

            for task in self.optimization_task:
                if task.name == task_name:
                    target_task = task
                    for experiment in task.experiment:
                        if experiment.name == experiment_name:
                            target_experiment = experiment
                            break
                    break

            if not target_task:
                return {
                    "status": "error",
                    "message": f"Task '{task_name}' not found",
                    "results": None,
                }

            if not target_experiment:
                return {
                    "status": "error",
                    "message": f"Experiment '{experiment_name}' not found in task '{task_name}'",
                    "results": None,
                }

            # Validate prompts path
            if not os.path.exists(prompts_path):
                return {
                    "status": "error",
                    "message": f"Prompts path does not exist: {prompts_path}",
                    "results": None,
                }

            # Create an executor with log capture and run optimization for a specific experiment with prompts
            executor = OptimizationExecutor(self, global_stream_capture)

            # Use context manager to capture all output
            with global_stream_capture.capture():
                results = executor.run_single_experiment_optimization(
                    task=target_task,
                    experiment=target_experiment,
                    population_size=population_size,
                    seed=seed,
                    use_prompts=True,
                    prompts_path=prompts_path,
                )

            return {
                "status": "success",
                "message": f"Prompt-based optimization completed for experiment '{experiment_name}'",
                "results": results,
            }

        except ImportError as e:
            return {
                "status": "error",
                "message": f"Failed to import optimization modules: {e}",
                "results": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Experiment execution failed: {e}",
                "results": None,
            }
