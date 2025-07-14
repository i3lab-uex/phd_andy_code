import numpy as np
import matplotlib.pyplot as plt
import torch


# Function taken from SAM's notebooks.
# https://github.com/facebookresearch/segment-anything/blob/main/notebooks/predictor_example.ipynb
def show_mask(mask: torch.Tensor, ax, random_color: bool = False):
    """
    Show the mask in the image using a default color if random_color is False,
    or a random color if random_color is True

    :param mask: mask to show (torch.Tensor)
    :param ax: axes to show the mask (matplotlib.axes.Axes)
    :param random_color: if True, use a random color to show the mask (bool)
    """
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)


# Function taken from SAM's notebooks.
# https://github.com/facebookresearch/segment-anything/blob/main/notebooks/predictor_example.ipynb
def show_points(coords, labels, ax: plt.Axes, marker_size: int = 375):
    """
    Show the positive and negative prompts in the image. The positive prompts
    are shown using green circles, the negative prompts are shown using red circles

    Params:
    :param coords: coordinates of the prompts
    :param labels: labels of the prompts
    :param ax: axes to show the prompts (matplotlib.axes.Axes)
    :param marker_size: size of the markers (int)
    :return:
    """
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='lime', marker='o', s=marker_size, edgecolor='white',
               linewidth=0.75)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='o', s=marker_size, edgecolor='black',
               linewidth=0.75)


# Function taken from SAM's notebooks.
# https://github.com/facebookresearch/segment-anything/blob/main/notebooks/predictor_example.ipynb
def show_box(box, ax):
    """
    Show the bounding box in the image with an orange color

    :param box: contains the coordinates of the bounding box (list)
    :param ax: axes to show the bounding box (matplotlib.axes.Axes)
    """
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='orange', facecolor=(0, 0, 0, 0), lw=2))
