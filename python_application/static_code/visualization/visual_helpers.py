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
    # Generate color using PyTorch tensors.
    color = (
        torch.cat([torch.rand(3), torch.tensor([0.6])])
        if random_color
        else torch.tensor([30 / 255, 144 / 255, 255 / 255, 0.6])
    )
    # Ensure mask is a PyTorch tensor.
    mask = mask if isinstance(mask, torch.Tensor) else torch.tensor(mask)
    # Get mask dimensions.
    h, w = mask.shape[-2:]
    # Adjust tensor shape for multiplication and visualize.
    mask_image = (mask.reshape(h, w, 1) * color.reshape(1, 1, -1)).numpy()
    ax.imshow(mask_image)


# Function taken from SAM's notebooks.
# https://github.com/facebookresearch/segment-anything/blob/main/notebooks/predictor_example.ipynb
def show_points(
    coords: torch.Tensor, labels: torch.Tensor, ax: plt.Axes, marker_size: int = 375
):
    """
    Show the positive and negative prompts in the image. The positive prompts
    are shown using green circles, the negative prompts are shown using red circles

    Params:
    :param coords: coordinates of the prompts (torch.Tensor)
    :param labels: labels of the prompts (torch.Tensor)
    :param ax: axes to show the prompts (matplotlib.axes.Axes)
    :param marker_size: size of the markers (int)
    :return:
    """
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(
        pos_points[:, 0],
        pos_points[:, 1],
        color="green",
        marker="*",
        s=marker_size,
        edgecolor="white",
        linewidth=1.25,
    )
    ax.scatter(
        neg_points[:, 0],
        neg_points[:, 1],
        color="red",
        marker="*",
        s=marker_size,
        edgecolor="white",
        linewidth=1.25,
    )


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
    ax.add_patch(
        plt.Rectangle((x0, y0), w, h, edgecolor="green", facecolor=(0, 0, 0, 0), lw=3)
    )
