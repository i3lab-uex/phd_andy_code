from typing import Tuple

import numpy as np


def compare_original_and_predicted_masks(
        original_mask: np.array, predicted_mask: np.array
) -> Tuple[float, float]:
    """
    Compares the original segmentation mask with the one predicted. Returns a
    tuple with the Jaccard index and the Dice coefficient.

    :param original_mask: original segmentation mask.
    :param predicted_mask: predicted segmentation mask.

    :return: Jaccard index and the Dice coefficient of the masks provided.
    """

    original_mask_transformed = np.squeeze(original_mask)
    original_mask_as_bool = original_mask_transformed != 0

    intersection = original_mask_as_bool * predicted_mask
    union = (original_mask_as_bool + predicted_mask) > 0

    jaccard = intersection.sum() / float(union.sum())
    dice = intersection.sum() * 2 / (original_mask_as_bool.sum() + predicted_mask.sum())

    return jaccard, dice


def compare_original_and_predicted_masks_mod_jaccard(
        original_mask_as_bool: np.array, predicted_mask: np.array
) -> float:
    """
    Compares the original segmentation mask with the one predicted using a modified

    params:
    :param original_mask_as_bool: original segmentation mask as a boolean array.
    :param predicted_mask: predicted segmentation mask as a boolean array.

    :return: Jaccard index of the masks provided.
    """
    intersection = original_mask_as_bool * predicted_mask
    union = (original_mask_as_bool + predicted_mask) > 0

    jaccard = intersection.sum() / float(union.sum())

    return jaccard


def compare_original_and_predicted_masks_mod_dice(original_mask_as_bool: np.array, predicted_mask: np.array) -> float:
    """
    Compares the original segmentation mask with the one predicted using a modified

    params:
    :param original_mask_as_bool: original segmentation mask as a boolean array.
    :param predicted_mask: predicted segmentation mask as a boolean array.

    :return: Dice coefficient of the masks provided.
    """
    intersection = original_mask_as_bool * predicted_mask

    dice = intersection.sum() * 2 / (original_mask_as_bool.sum() + predicted_mask.sum())

    return dice
