"""
Optimization executor that leverages PROBE dynamic configuration.
This module centralizes optimization execution using PROBE task and experiment definitions.
"""

import os
import glob
import time
import random
import torch
import numpy as np
import nibabel as nib
from typing import Dict, Any, List, Optional
from pymoo.optimize import minimize
from pymoo.algorithms.soo.nonconvex.ga import GA
from segment_anything import sam_model_registry, SamPredictor

from python_application.generated_code.model.PROBE import PROBE
from python_application.generated_code.model.OptimizationTask import OptimizationTask
from python_application.generated_code.model.Experiment import Experiment
from python_application.static_code.genetic_algorithm.SAMOptimizationProblem import (
    SAMOptimizationProblem,
    OptimizationCallback,
    process_image_slice,
    create_input_labels,
    save_optimization_history,
    create_visualization,
    write_statistics,
    ensure_output_directory,
)
from python_application.static_code.genetic_algorithm.PromptManager import (
    PromptManager,
)
from python_application.static_code.metrics.MetricCalculation import (
    compare_original_and_predicted_masks,
)
from python_application.static_code.utils.LogCapture import (
    StreamCapture,
    ProgressTracker,
)


def _get_sample_files(
    dataset_info: Dict[str, str], experiment: Experiment
) -> List[str]:
    """
    Get list of files to process based on experiment sample configuration.

    Args:
        dataset_info (Dict[str, str]): Dataset configuration
        experiment (Experiment): Experiment configuration

    Returns:
        List[str]: List of file paths to process
    """
    # If the experiment specifies a specific sample, use only that
    if experiment.sample and experiment.sample.filename:
        sample_file = f"{dataset_info['images_path']}/{experiment.sample.filename}"
        if os.path.exists(sample_file):
            return [sample_file]
        else:
            raise FileNotFoundError(f"Sample file not found: {sample_file}")

    # Otherwise, use all files in the dataset
    if dataset_info["name"] == "Coronacases":
        files = glob.glob(f"{dataset_info['images_path']}/coronacases_*.nii.gz")
    else:
        # Generic pattern for other datasets
        files = glob.glob(f"{dataset_info['images_path']}/*.nii.gz")

    files.sort()
    return files


def _process_single_slice(
    image_slice: np.ndarray,
    mask_slice: np.ndarray,
    predictor: SamPredictor,
    prompt_info: Dict[str, Any],
    task: OptimizationTask,
    slice_name: str,
    dataset_info: Dict[str, str],
    population_size: int,
    seed: int,
) -> Dict[str, Any]:
    """
    Process a single image slice.

    Args:
        image_slice (np.ndarray): Image slice data
        mask_slice (np.ndarray): Mask slice data
        predictor (SamPredictor): SAM predictor
        prompt_info (Dict[str, Any]): Prompt information
        task (OptimizationTask): Optimization task
        slice_name (str): Name for output files
        dataset_info (Dict[str, str]): Dataset configuration
        population_size (int): GA population size
        seed (int): Random seed

    Returns:
        Dict[str, Any]: Processing results
    """
    start_time = time.time()

    # Check if mask has valid data
    labels = np.unique(mask_slice)
    if labels.size <= 1:
        print(f"Slice {slice_name} has no mask data. Skipping...")
        return None

    # Process image
    processed_image = process_image_slice(
        image_slice
    )
    print(f"Processing slice {slice_name} - Image shape: {processed_image.shape}")

    # Setup predictor
    predictor.set_image(processed_image)

    # Prepare an optimization problem
    original_mask_as_bool = mask_slice != 0
    objective = task.optimization_metric.name.lower()
    if "jaccard" in objective:
        objective = "jaccard"
    elif "dice" in objective:
        objective = "dice"
    else:
        objective = "score"

    problem = SAMOptimizationProblem(
        coordinates=prompt_info["coordinates"],
        input_box=prompt_info["input_box"],
        predictor=predictor,
        input_label=prompt_info["input_label"],
        original_mask_as_bool=original_mask_as_bool,
        objective=objective,
        multimask=False,
        population_size=population_size,
    )

    # Run optimization
    algorithm = GA(pop_size=population_size)
    history_callback = OptimizationCallback()

    result = minimize(
        problem,
        algorithm,
        seed=seed,
        callback=history_callback,
        save_history=False,
        verbose=True,
    )

    # Calculate metrics
    best_coordinates = result.X
    objective_value = float(-result.F)

    jaccard, dice = compare_original_and_predicted_masks(mask_slice, problem.best_mask)

    elapsed_time = time.time() - start_time

    # Save results
    output_path = dataset_info["output_path"]
    ensure_output_directory(output_path)

    # Save optimization history
    history_file = f"{output_path}/{slice_name}_history.txt"
    save_optimization_history(history_callback, history_file, objective)

    # Create visualization
    visualization_file = f"{output_path}/{slice_name}_result.pdf"
    create_visualization(
        processed_image,
        problem.best_mask,
        prompt_info["input_box"],
        best_coordinates,
        prompt_info["input_label"],
        objective,
        problem.best_score,
        jaccard,
        dice,
        visualization_file,
    )

    print(
        f"Slice {slice_name} - Objective: {objective_value:.4f}, "
        f"Dice: {dice:.4f}, Jaccard: {jaccard:.4f}, "
        f"Score: {problem.best_score:.4f}, Time: {elapsed_time:.2f}s"
    )

    return {
        "slice_name": slice_name,
        "objective_value": objective_value,
        "dice": dice,
        "jaccard": jaccard,
        "score": problem.best_score,
        "time": elapsed_time,
        "coordinates": best_coordinates.tolist(),
    }


class OptimizationExecutor:
    """Executor that runs optimizations using PROBE dynamic configuration."""

    def __init__(self, probe: "PROBE", stream_capture: Optional[StreamCapture] = None):
        """
        Initialize the optimization executor.

        Args:
            probe (PROBE): PROBE instance with dynamic configuration
            stream_capture (Optional[StreamCapture]): Stream capture instance for progress tracking
        """
        self.probe = probe
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.stream_capture = stream_capture
        self.progress_tracker = (
            ProgressTracker(stream_capture) if stream_capture else None
        )

    def _extract_dataset_info(self, task: OptimizationTask) -> Dict[str, str]:
        """
        Extract dataset information from PROBE configuration.

        Args:
            task (OptimizationTask): Optimization task containing dataset references

        Returns:
            Dict[str, str]: Dataset configuration
        """
        # Find the dataset referenced by the task
        dataset = self.probe.dataset[0] if self.probe.dataset else None
        if not dataset:
            raise ValueError("No dataset found in PROBE configuration")

        subset = dataset.subset[0] if dataset.subset else None
        if not subset:
            raise ValueError("No subset found in dataset configuration")

        return {
            "name": dataset.name,
            "images_path": f"{subset.path}/{subset.dataFolderName}",
            "masks_path": f"{subset.path}/{subset.labelsFolderName}",
            "output_path": f"output/{dataset.name}/{task.name}"
        }

    def _setup_sam_model(self, task: OptimizationTask) -> SamPredictor:
        """
        Set up the SAM model from task configuration.

        Args:
            task (OptimizationTask): Task containing model configuration

        Returns:
            SamPredictor: Configured SAM predictor
        """
        foundation_model = task.foundation_model
        sam = sam_model_registry[foundation_model.name](
            checkpoint=foundation_model.checkpointFilepath
        )
        sam.to(device=self.device)
        return SamPredictor(sam)

    def run_single_experiment_optimization(
        self,
        task: OptimizationTask,
        experiment: Experiment,
        population_size: int = 100,
        seed: int = 1,
        use_prompts: bool = False,
        prompts_path: Optional[str] = None,
        stop_callback=None,
    ) -> Dict[str, Any]:
        """
        Run optimization for a single experiment.

        Args:
            task (OptimizationTask): Optimization task configuration
            experiment (Experiment): Specific experiment to run
            population_size (int, optional): GA population size. Defaults to 100.
            seed (int, optional): Random seed. Defaults to 1.
            use_prompts (bool, optional): Whether to use JSON prompts. Defaults to False.
            prompts_path (Optional[str], optional): Path to JSON prompts. Defaults to None.
            stop_callback (callable, optional): Function that returns True if optimization should stop

        Returns:
            Dict[str, Any]: Optimization results
        """
        total_start_time = time.time()
        random.seed(seed)

        if self.progress_tracker:
            self.progress_tracker.update_stage(
                f"Initializing experiment: {experiment.name}"
            )

        # Extract configuration
        dataset_info = self._extract_dataset_info(task)
        predictor = self._setup_sam_model(task)

        # Get files to process
        files = _get_sample_files(dataset_info, experiment)

        # Setup output
        output_file = f"{dataset_info['output_path']}/{experiment.name}_results.txt"
        ensure_output_directory(dataset_info["output_path"])

        results = []
        all_metrics = {"dice": [], "jaccard": [], "score": [], "time": []}

        # Process each file
        for file_idx, file_path in enumerate(files):
            # Check if optimization should stop
            if stop_callback and stop_callback():
                print(f"🛑 Optimization stopped by user request at file {file_idx + 1}")
                break

            filename = file_path.split("/")[-1]
            base_name = filename.replace(".nii.gz", "")

            if self.progress_tracker:
                self.progress_tracker.update_file(
                    f"[{file_idx + 1}/{len(files)}] {filename}"
                )

            # Load data
            image = nib.load(file_path)
            mask_file = f"{dataset_info['masks_path']}/{filename}"
            mask = nib.load(mask_file)

            image_data = image.get_fdata()
            mask_data = mask.get_fdata()

            # Process each slice
            for slice_idx in range(image_data.shape[2]):
                # Check if optimization should stop
                if stop_callback and stop_callback():
                    print(f"🛑 Optimization stopped by user request at slice {slice_idx + 1}")
                    break

                slice_name = f"{experiment.name}_{base_name}_slice_{slice_idx}"

                if self.progress_tracker:
                    self.progress_tracker.update_slice(
                        f"{slice_name} [{slice_idx + 1}/{image_data.shape[2]}]"
                    )

                image_slice = image_data[..., slice_idx]
                mask_slice = mask_data[..., slice_idx]

                # Get prompt information
                if use_prompts and prompts_path:
                    try:
                        box_coords, pos_coords, neg_coords = (
                            PromptManager.parse_json_prompt(
                                prompts_path, base_name, slice_idx
                            )
                        )
                        prompt_info = {
                            "input_box": np.array(box_coords),
                            "coordinates": np.array(pos_coords + neg_coords),
                            "input_label": create_input_labels(pos_coords, neg_coords),
                        }
                    except Exception as e:
                        error_msg = f"Error loading prompts for {base_name} slice {slice_idx}: {e}"
                        if self.progress_tracker:
                            # Log the error in the progress tracker
                            print(f"❌ Error: {error_msg}")
                        continue

                else:
                    # Default prompt information if no prompts are used
                    prompt_info = {
                        "input_box": np.array(
                            [0, 0, image_slice.shape[0], image_slice.shape[1]]
                        ),
                        "coordinates": np.array([]),
                        "input_label": create_input_labels([], []),
                    }

                # Process slice
                slice_result = _process_single_slice(
                    image_slice,
                    mask_slice,
                    predictor,
                    prompt_info,
                    task,
                    slice_name,
                    dataset_info,
                    population_size,
                    seed,
                )

                if slice_result:
                    results.append(slice_result)
                    all_metrics["dice"].append(slice_result["dice"])
                    all_metrics["jaccard"].append(slice_result["jaccard"])
                    all_metrics["score"].append(slice_result["score"])
                    all_metrics["time"].append(slice_result["time"])

                    if self.progress_tracker:
                        self.progress_tracker.log_result(slice_name, slice_result)

        # Write summary results
        if self.progress_tracker:
            self.progress_tracker.update_stage("Writing results and statistics")

        total_time = time.time() - total_start_time

        with open(output_file, "w") as f:
            f.write(f"Experiment: {experiment.name}\n")
            f.write(f"Task: {task.name}\n")
            f.write(f"Total execution time: {total_time:.2f} seconds\n")
            f.write(f"Processed slices: {len(results)}\n\n")

            f.write("Slice\tObjective\tDice\tJaccard\tScore\tTime\tCoordinates\n")
            for result in results:
                coords_str = ",".join([str(c) for c in result["coordinates"]])
                f.write(
                    f"{result['slice_name']}\t{result['objective_value']:.4f}\t"
                    f"{result['dice']:.4f}\t{result['jaccard']:.4f}\t"
                    f"{result['score']:.4f}\t{result['time']:.2f}\t{coords_str}\n"
                )

        write_statistics(
            output_file,
            all_metrics["jaccard"],
            all_metrics["dice"],
            all_metrics["score"],
            all_metrics["time"],
            total_time,
        )

        final_results = {
            "experiment_name": experiment.name,
            "total_time": total_time,
            "processed_slices": len(results),
            "avg_dice": np.mean(all_metrics["dice"]) if all_metrics["dice"] else 0,
            "avg_jaccard": (
                np.mean(all_metrics["jaccard"]) if all_metrics["jaccard"] else 0
            ),
            "avg_score": np.mean(all_metrics["score"]) if all_metrics["score"] else 0,
            "detailed_results": results,
        }

        if self.progress_tracker:
            self.progress_tracker.log_final_summary(
                {"name": experiment.name, **final_results}
            )

        return final_results

    def run_task_optimization(
        self,
        task: OptimizationTask,
        population_size: int = 100,
        seed: int = 1,
        use_prompts: bool = False,
        prompts_path: Optional[str] = None,
        stop_callback=None,
    ) -> Dict[str, Any]:
        """
        Run optimization for all experiments in a task.

        Args:
            task (OptimizationTask): Optimization task with experiments
            population_size (int, optional): GA population size. Defaults to 100.
            seed (int, optional): Random seed. Defaults to 1.
            use_prompts (bool, optional): Whether to use JSON prompts. Defaults to False.
            prompts_path (Optional[str], optional): Path to JSON prompts. Defaults to None.
            stop_callback (callable, optional): Function that returns True if optimization should stop

        Returns:
            Dict[str, Any]: Combined results from all experiments
        """
        task_start_time = time.time()
        experiment_results = []

        if self.progress_tracker:
            self.progress_tracker.update_stage(
                f"Starting task optimization: {task.name}"
            )

        print(f"Running optimization for task: {task.name}")
        print(f"Number of experiments: {len(task.experiment)}")

        for exp_idx, experiment in enumerate(task.experiment):
            # Check if optimization should stop
            if stop_callback and stop_callback():
                print(f"🛑 Optimization stopped by user request at experiment {exp_idx + 1}")
                break

            if self.progress_tracker:
                self.progress_tracker.update_stage(
                    f"Experiment [{exp_idx + 1}/{len(task.experiment)}]: {experiment.name}"
                )

            exp_result = self.run_single_experiment_optimization(
                task=task,
                experiment=experiment,
                population_size=population_size,
                seed=seed,
                use_prompts=use_prompts,
                prompts_path=prompts_path,
                stop_callback=stop_callback,
            )

            experiment_results.append(exp_result)

        task_total_time = time.time() - task_start_time

        # Aggregate results
        total_slices = sum(r["processed_slices"] for r in experiment_results)
        avg_dice = np.mean(
            [r["avg_dice"] for r in experiment_results if r["avg_dice"] > 0]
        )
        avg_jaccard = np.mean(
            [r["avg_jaccard"] for r in experiment_results if r["avg_jaccard"] > 0]
        )
        avg_score = np.mean(
            [r["avg_score"] for r in experiment_results if r["avg_score"] > 0]
        )

        final_results = {
            "task_name": task.name,
            "total_time": task_total_time,
            "total_processed_slices": total_slices,
            "num_experiments": len(experiment_results),
            "avg_dice": avg_dice if not np.isnan(avg_dice) else 0,
            "avg_jaccard": avg_jaccard if not np.isnan(avg_jaccard) else 0,
            "avg_score": avg_score if not np.isnan(avg_score) else 0,
            "experiment_results": experiment_results,
        }

        if self.progress_tracker:
            self.progress_tracker.log_final_summary(
                {"name": task.name, **final_results}
            )

        return final_results
