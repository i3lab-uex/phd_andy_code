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
            from python_application.static_code.genetic_algorithm.OptimizationExecutor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.LogCapture import (
                global_stream_capture,
            )

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
            from python_application.static_code.genetic_algorithm.OptimizationExecutor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.LogCapture import (
                global_stream_capture,
            )

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
        stop_callback=None,
    ) -> Dict[str, Any]:
        """
        Run SAM optimization for all experiments in a task using prompts from JSON files.

        Args:
            task_name (str): Name of the optimization task
            prompts_path (str): Path to the directory containing JSON prompt files
            population_size (int, optional): Population size for genetic algorithm. Defaults to 100.
            seed (int, optional): Random seed for reproducibility. Defaults to 1.
            stop_callback (callable, optional): Function that returns True if optimization should stop

        Returns:
            Dict[str, Any]: Experiment results including metrics and execution time
        """
        try:
            from python_application.static_code.genetic_algorithm.OptimizationExecutor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.LogCapture import (
                global_stream_capture,
            )

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
                    stop_callback=stop_callback,
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
        stop_callback=None,
    ) -> Dict[str, Any]:
        """
        Run SAM optimization for a specific experiment using prompts from JSON files.

        Args:
            task_name (str): Name of the optimization task
            experiment_name (str): Name of the specific experiment
            prompts_path (str): Path to the directory containing JSON prompt files
            population_size (int, optional): Population size for genetic algorithm. Defaults to 100.
            seed (int, optional): Random seed for reproducibility. Defaults to 1.
            stop_callback (callable, optional): Function that returns True if optimization should stop

        Returns:
            Dict[str, Any]: Experiment results including metrics and execution time
        """
        try:
            from python_application.static_code.genetic_algorithm.OptimizationExecutor import (
                OptimizationExecutor,
            )
            from python_application.static_code.utils.LogCapture import (
                global_stream_capture,
            )

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
                    stop_callback=stop_callback,
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

    def display_probe(self) -> str:
        """
        Display the complete PROBE configuration.

        Returns:
            str: Formatted string with PROBE information
        """
        output = [f"🖥️ Device: {self.device}"]

        for ds in self.dataset:
            output.append(f"\n📂 Dataset: {ds.name} - {ds.description} ({ds.type})")
            for ss in ds.subset:
                output.append(f"  📁 Subset: {ss.name}, Path: {ss.path}")
                output.append(
                    f"    Data folder: {ss.dataFolderName}, Labels folder: {ss.labelsFolderName}"
                )
                output.append(f"    Samples ({len(ss.sample)} total):")
                for sp in ss.sample:
                    output.append(
                        f"      🖼️ Sample: {sp.filename} (Format: {sp.extension})"
                    )

        for i, ot in enumerate(self.optimization_task):
            output.append(
                f"\n🚀 Optimization Task {i + 1}: {ot.name} - {ot.description}"
            )
            output.append(f"  🔬 Algorithm: {ot.algorithm}")
            output.append(
                f"  🤖 Foundation Model: {ot.foundation_model.name} ({ot.foundation_model.type}) "
                f"v{ot.foundation_model.version}"
            )
            output.append(
                f"    📁 Checkpoint: {ot.foundation_model.checkpointFilepath}"
            )
            output.append(f"    ⚙️ Configuration: {ot.foundation_model.configuration}")
            if (
                hasattr(ot.foundation_model, "description")
                and ot.foundation_model.description
            ):
                output.append(f"    📝 Description: {ot.foundation_model.description}")

            output.append(
                f"  🎯 Optimization Metric: {ot.optimization_metric.name} ({ot.optimization_metric.type})"
            )
            output.append(
                f"  📊 Performance Metrics ({len(ot.performance_metric)} total):"
            )
            for m in ot.performance_metric:
                output.append(f"    - {m.name}")

            output.append(f"  🧪 Experiments ({len(ot.experiment)} total):")
            for e in ot.experiment:
                output.append(f"    ▶ Experiment: {e.name}")
                output.append(
                    f"      🏁 Initial State: {e.initial_state.description} (Improved: {e.initial_state.hasImproved})"
                )
                output.append(
                    f"      💬 Prompt Type: {type(e.initial_state.prompt).__name__}"
                )

                # Detailed prompt information
                if (
                    hasattr(e.initial_state.prompt, "bounding_box")
                    and e.initial_state.prompt.bounding_box
                ):
                    output.append(
                        f"        📦 Bounding Boxes ({len(e.initial_state.prompt.bounding_box)} total):"
                    )
                    for idx, box in enumerate(e.initial_state.prompt.bounding_box):
                        if (
                            hasattr(box, "x")
                            and hasattr(box, "y")
                            and hasattr(box, "width")
                            and hasattr(box, "height")
                        ):
                            output.append(
                                f"          Box {idx + 1}: x={box.x}, y={box.y}, w={box.width}, h={box.height}"
                            )
                        else:
                            output.append(
                                f"          Box {idx + 1}: {type(box).__name__}"
                            )

                if (
                    hasattr(e.initial_state.prompt, "point")
                    and e.initial_state.prompt.point
                ):
                    output.append(
                        f"        📍 Points ({len(e.initial_state.prompt.point)} total):"
                    )
                    for idx, point in enumerate(e.initial_state.prompt.point):
                        point_info = f"          Point {idx + 1}: Type={point.type}"
                        if hasattr(point, "x") and hasattr(point, "y"):
                            point_info += f", x={point.x}, y={point.y}"
                        if hasattr(point, "label"):
                            point_info += f", label={point.label}"
                        output.append(point_info)

                output.append(
                    f"      ⏹️ Stop Conditions ({len(e.stop_condition)} total):"
                )
                for idx, sc in enumerate(e.stop_condition):
                    condition_info = f"        {idx + 1}. {type(sc).__name__}"
                    # Add specific details for different stop condition types
                    if hasattr(sc, "minutesDuration"):
                        condition_info += f" (Duration: {sc.minutesDuration} minutes)"
                    elif hasattr(sc, "numIterations"):
                        condition_info += f" (Max iterations: {sc.numIterations})"
                    elif hasattr(sc, "threshold") and hasattr(sc, "metric"):
                        condition_info += (
                            f" (Threshold: {sc.threshold}, Metric: {sc.metric})"
                        )
                    output.append(condition_info)

                output.append(
                    f"      🖼️ Sample: {e.sample.filename} ({e.sample.extension})"
                )

        return "\n".join(output)

    def save_logs_to_file(self, custom_content: str = None) -> str:
        """
        Save PROBE logs to a file in logs/probe_configurations/ directory with incremental numbering.

        Args:
            custom_content (str, optional): Custom content to save. If None, uses display_probe() output.

        Returns:
            str: Confirmation message with the file path
        """
        import os
        from datetime import datetime

        # Create logs directory structure
        logs_dir = os.path.join("logs", "probe_configurations")
        os.makedirs(logs_dir, exist_ok=True)

        # Find the next available number
        counter = 1
        while True:
            filename = f"probe_config{counter}.txt"
            filepath = os.path.join(logs_dir, filename)
            if not os.path.exists(filepath):
                break
            counter += 1

        # Get content to save
        if custom_content is not None:
            content = custom_content
        else:
            content = self.display_probe()

        # Add timestamp header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"PROBE Configuration - Generated on {timestamp}\n"
        header += "=" * 60 + "\n\n"
        full_content = header + content

        # Save file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_content)
            return f"✅ Configuration saved successfully to {filepath}"
        except Exception as e:
            return f"❌ Error saving configuration: {str(e)}"
