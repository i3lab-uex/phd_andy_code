"""
Common utilities for SAM optimization with genetic algorithms.
This module contains shared classes and functions between covidExp.py and covidExpPrompts.py.
"""

import os
import gc
import warnings
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import Problem
from skimage.measure import regionprops
from pymoo.core.callback import Callback
from segment_anything import SamPredictor
from typing import Tuple, List, Dict, Any, Union

from python_application.static_code.metrics.MetricCalculation import (
    compare_original_and_predicted_masks_mod_jaccard,
    compare_original_and_predicted_masks_mod_dice,
)
from python_application.static_code.visualization.VisualHelpers import (
    show_points,
    show_mask,
    show_box,
)

warnings.filterwarnings("default")


class SAMOptimizationProblem(Problem):
    """SAM optimization problem using genetic algorithms."""

    def __init__(
        self,
        coordinates: np.ndarray,
        input_box: np.ndarray,
        predictor: SamPredictor,
        input_label: np.ndarray,
        original_mask_as_bool: np.ndarray,
        objective: str,
        multimask: bool = False,
        population_size: int = 100,
    ) -> None:
        """
        Initialize the optimization problem.

        Args:
            coordinates (np.ndarray): Point coordinates
            input_box (np.ndarray): Bounding box coordinates
            predictor (SamPredictor): SAM predictor instance
            input_label (np.ndarray): Point labels
            original_mask_as_bool (np.ndarray): Original mask as boolean array
            objective (str): Objective function ('score', 'jaccard', 'dice')
            multimask (bool, optional): Whether to use multiple masks. Defaults to False.
            population_size (int, optional): Population size. Defaults to 100.
        """
        self.predictor = predictor
        self.input_label = input_label
        self.input_box = input_box
        self.original_mask_as_bool = original_mask_as_bool
        self.objective = objective
        self.multimask = multimask
        self.population_size = population_size
        self.best_mask = None
        self.best_score = None

        # Calculate bounding box limits
        cxl = float(min(input_box[0], input_box[2]))
        cxu = float(max(input_box[0], input_box[2]))
        cyl = float(min(input_box[1], input_box[3]))
        cyu = float(max(input_box[1], input_box[3]))

        # Create limits dynamically based on number of coordinates
        xl = np.tile([cxl, cyl], len(coordinates) // 2)
        xu = np.tile([cxu, cyu], len(coordinates) // 2)

        super().__init__(n_var=len(coordinates), n_obj=1, xl=xl, xu=xu)

    def _evaluate(self, x: np.ndarray, out: Dict[str, Any], *args, **kwargs) -> None:
        """
        Evaluate the objective function for a population.

        Args:
            x (np.ndarray): Population array
            out (Dict[str, Any]): Output dictionary for results
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        objectives = []
        best_objective = float("inf")

        for i in range(self.population_size):
            input_point = x[i].reshape(-1, 2)

            # SAM prediction
            if self.multimask:
                masks, scores, _ = self.predictor.predict(
                    point_coords=input_point,
                    point_labels=self.input_label,
                    box=self.input_box[None, :],
                    multimask_output=True,
                )
                mask = masks[np.argmax(scores), :, :]
                score = np.max(scores)
            else:
                mask, score, _ = self.predictor.predict(
                    point_coords=input_point,
                    point_labels=self.input_label,
                    box=self.input_box[None, :],
                    multimask_output=False,
                )

            # Calculate objective value
            objective_value = self._calculate_objective(mask, score)
            objectives.append(objective_value)

            # Save best result
            if objective_value < best_objective:
                best_objective = objective_value
                self.best_mask = mask
                self.best_score = float(score)

        out["F"] = objectives

    def _calculate_objective(self, mask: np.ndarray, score: float) -> float:
        """
        Calculate the objective function value.

        Args:
            mask (np.ndarray): Predicted mask
            score (float): SAM confidence score

        Returns:
            float: Negative objective value (for minimization)
        """
        if self.objective == "score":
            return -score
        elif self.objective == "jaccard":
            jaccard = compare_original_and_predicted_masks_mod_jaccard(
                self.original_mask_as_bool, mask
            )
            return -jaccard
        else:  # dice
            dice = compare_original_and_predicted_masks_mod_dice(
                self.original_mask_as_bool, mask
            )
            return -dice


class OptimizationCallback(Callback):
    """Callback for tracking optimization history."""

    def __init__(self) -> None:
        """Initialize the callback."""
        super().__init__()
        self.n_evals = []
        self.opt_f = []
        self.opt_x = []

    def notify(self, algorithm) -> None:
        """
        Notify about algorithm progress.

        Args:
            algorithm: The optimization algorithm instance
        """
        self.n_evals.append(algorithm.evaluator.n_eval)
        opt = algorithm.opt[0]
        self.opt_f.append(opt.get("F"))
        self.opt_x.append(opt.get("X"))


def find_bounding_box(mask: np.ndarray) -> Union[Tuple[int, int, int, int], None]:
    """
    Find the bounding box around a mask.

    Args:
        mask (np.ndarray): Input mask

    Returns:
        Union[Tuple[int, int, int, int], None]: Bounding box coordinates or None if no contours
    """
    labels = np.unique(mask)

    if labels.size > 1:
        print("Finding bounding box around the mask.")
        binary_mask = np.where(mask > 0, 1, 0).astype(np.int16)
        regions_properties = regionprops(binary_mask)

        if regions_properties:
            region_properties = regions_properties[0]
            bounding_box = region_properties.bbox
            print(f"Bounding box: {bounding_box}")
            return bounding_box

    print("No mask contours to work with.")
    return None


def process_image_slice(image_slice: np.ndarray, windowing: bool = True) -> np.ndarray:
    """
    Process an image slice for SAM.

    Args:
        image_slice (np.ndarray): Image slice
        windowing (bool, optional): Whether to apply CT windowing. Defaults to True.

    Returns:
        np.ndarray: Processed image in RGB format
    """
    processed_image = np.copy(image_slice)

    if windowing:
        # CT windowing configuration
        window_level = -650
        window_width = 1500
        processed_image = processed_image.clip(
            window_level - window_width // 2, window_level + window_width // 2
        )

    # Normalization
    processed_image = (
        (processed_image - processed_image.min())
        / (processed_image.max() - processed_image.min())
        * 255
    )
    processed_image = processed_image.astype(np.uint8)

    # Convert to RGB
    return np.stack((processed_image,) * 3, axis=-1)


def create_input_labels(
    pos_coordinates: List[float], neg_coordinates: List[float]
) -> np.ndarray:
    """
    Create input labels for points.

    Args:
        pos_coordinates (List[float]): Positive point coordinates
        neg_coordinates (List[float]): Negative point coordinates

    Returns:
        np.ndarray: Array of labels
    """
    input_label = []
    input_label.extend([1] * (len(pos_coordinates) // 2))  # Positive points
    input_label.extend([0] * (len(neg_coordinates) // 2))  # Negative points
    return np.array(input_label)


def save_optimization_history(
    history_callback: OptimizationCallback, output_file: str, objective: str
) -> None:
    """
    Save optimization history to a file.

    Args:
        history_callback (OptimizationCallback): Callback with history
        output_file (str): Output file path
        objective (str): Objective function used
    """
    try:
        with open(output_file, "w") as f:
            f.write(f"num_evals\tObjective ({objective})\tCoordinates\n")

            for i in range(len(history_callback.n_evals)):
                coords_str = ",".join([str(j) for j in history_callback.opt_x[i]])
                f.write(
                    f"{history_callback.n_evals[i]}\t"
                    f"{history_callback.opt_f[i][0]}\t"
                    f"{coords_str}\n"
                )
    except IOError as e:
        print(f"Could not create file {output_file}: {e}")


def create_visualization(
    processed_image: np.ndarray,
    mask: np.ndarray,
    input_box: np.ndarray,
    coordinates: np.ndarray,
    input_label: np.ndarray,
    objective: str,
    score: float,
    jaccard: float,
    dice: float,
    output_file: str,
) -> None:
    """
    Create and save a visualization of the results.

    Args:
        processed_image (np.ndarray): Processed image
        mask (np.ndarray): Predicted mask
        input_box (np.ndarray): Bounding box
        coordinates (np.ndarray): Point coordinates
        input_label (np.ndarray): Point labels
        objective (str): Objective function
        score (float): SAM score
        jaccard (float): Jaccard index
        dice (float): Dice coefficient
        output_file (str): Output file path
    """
    fig = plt.figure(figsize=(10, 10))
    try:
        plt.imshow(processed_image)
        show_mask(mask, plt.gca())
        show_box(input_box, plt.gca())

        points = coordinates.reshape(-1, 2)
        show_points(points, input_label, plt.gca())

        # Dynamic title based on objective function
        if objective == "score":
            title = f"SCORE: {score:.3f}, Jaccard: {jaccard:.3f}, Dice: {dice:.3f}"
        elif objective == "jaccard":
            title = f"JACCARD: {jaccard:.3f}, Dice: {dice:.3f}, Score: {score:.3f}"
        else:
            title = f"DICE: {dice:.3f}, Jaccard: {jaccard:.3f}, Score: {score:.3f}"

        plt.title(title, fontsize=18)
        plt.axis("on")
        fig.savefig(output_file)

    except Exception as e:
        print(f"Error creating visualization: {e}")
    finally:
        plt.close(fig)
        plt.close("all")
        gc.collect()


def write_statistics(
    output_file: str,
    jaccard_list: List[float],
    dice_list: List[float],
    score_list: List[float],
    time_list: List[float],
    total_time: float,
) -> None:
    """
    Write final statistics to the output file.

    Args:
        output_file (str): Output file path
        jaccard_list (List[float]): List of Jaccard values
        dice_list (List[float]): List of Dice values
        score_list (List[float]): List of score values
        time_list (List[float]): List of time values
        total_time (float): Total execution time
    """
    try:
        with open(output_file, "a") as f:
            # Jaccard statistics
            if jaccard_list:
                f.write(f"\nMinimum Jaccard: {np.min(jaccard_list)}\n")
                f.write(f"Maximum Jaccard: {np.max(jaccard_list)}\n")
                f.write(f"Average Jaccard: {np.mean(jaccard_list)}\n")
                f.write(f"Standard Deviation Jaccard: {np.std(jaccard_list)}\n\n")
            else:
                f.write("No Jaccard metrics available - no valid slices processed\n\n")

            # Dice statistics
            if dice_list:
                f.write(f"Minimum Dice: {np.min(dice_list)}\n")
                f.write(f"Maximum Dice: {np.max(dice_list)}\n")
                f.write(f"Average Dice: {np.mean(dice_list)}\n")
                f.write(f"Standard Deviation Dice: {np.std(dice_list)}\n\n")
            else:
                f.write("No Dice metrics available - no valid slices processed\n\n")

            # Score statistics
            if score_list:
                f.write(f"Minimum Score: {np.min(score_list)}\n")
                f.write(f"Maximum Score: {np.max(score_list)}\n")
                f.write(f"Average Score: {np.mean(score_list)}\n")
                f.write(f"Standard Deviation Score: {np.std(score_list)}\n\n")
            else:
                f.write("No Score metrics available - no valid slices processed\n\n")

            # Time statistics
            if time_list:
                f.write(f"Minimum individual Time: {np.min(time_list)}\n")
                f.write(f"Maximum individual Time: {np.max(time_list)}\n")
                f.write(f"Average individual Times: {np.mean(time_list)}\n")
                f.write(f"Standard Deviation individual Times: {np.std(time_list)}\n\n")
                f.write(f"Sum of individual Times: {np.sum(time_list)}\n")
            else:
                f.write("No timing metrics available - no valid slices processed\n\n")

            f.write(f"Total Execution Time (s): {total_time}\n")

    except IOError as e:
        print(f"Error writing statistics: {e}")


def ensure_output_directory(output_path: str) -> bool:
    """
    Ensure that the output directory exists.

    Args:
        output_path (str): Output directory path

    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        os.makedirs(output_path, exist_ok=True)
        return True
    except OSError as e:
        print(f"Could not create directory {output_path}: {e}")
        return False
