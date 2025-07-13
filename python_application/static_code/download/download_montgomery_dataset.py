import os
import shutil
from pathlib import Path

from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

from python_application.static_code.download.download_helpers import download_file_with_progress, extract_zip


def download_montgomery_dataset() -> int:
    """
    Download the Montgomery dataset.

    :return: 1 if the dataset has already been downloaded, 0 if the download was successful,
    -1 if the download failed
    """
    # Set up the directory structure
    montgomery_dir = "datasets/montgomery"
    images_folder = Path('datasets/covid/COVID-19-CT-Seg_20cases')
    masks_folder = Path('datasets/covid/Lung_Mask')
    os.makedirs(montgomery_dir, exist_ok=True)

    # Check if the dataset has been previously downloaded and the dataset path exists. If so, return 1
    if (images_folder.exists() and masks_folder.exists() and any(images_folder.rglob('*.png')) and any(
            masks_folder.rglob('*.png'))):
        return 1

    # URL of the Montgomery dataset
    dataset_url = "https://openi.nlm.nih.gov/imgs/collections/NLM-MontgomeryCXRSet.zip"
    zip_path = os.path.join(montgomery_dir, "NLM-MontgomeryCXRSet.zip")

    try:
        # Download and extract the dataset
        print("Downloading Montgomery dataset...")
        download_file_with_progress(dataset_url, zip_path)
    except Exception as e:
        print(f"Download failed: {e}")
        return -1

    print("\nExtracting dataset...")
    extract_zip(zip_path, montgomery_dir)

    # Remove the ZIP file after extraction
    os.remove(zip_path)

    # Organize the dataset
    organize_montgomery_dataset()

    # The dataset has been downloaded successfully
    return 0


def organize_montgomery_dataset():
    """
    Organize the Montgomery dataset.
    """
    # Set up the directory structure
    montgomery_dir = "datasets/montgomery"
    masks_folder = Path('datasets/covid/Lung_Mask')
    base_path = os.path.join(montgomery_dir, "MontgomerySet")

    # Organize the dataset
    print("\nOrganizing Montgomery dataset...")
    for subdir in ["CXR_png", "ManualMask"]:
        shutil.move(os.path.join(base_path, subdir), montgomery_dir)
    shutil.move(os.path.join(base_path, "NLM-MontgomeryCXRSet-ReadMe.pdf"), montgomery_dir)

    # Cleanup
    shutil.rmtree(os.path.join(montgomery_dir, "MontgomerySet"))
    for file_name in ["CXR_png/Thumbs.db", "ManualMask/.DS_Store", "ManualMask/leftMask/Thumbs.db"]:
        file_path = os.path.join(montgomery_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Get the list of files in the left and right mask directories
    left_mask_dir = os.path.join(masks_folder, 'leftMask')
    right_mask_dir = os.path.join(masks_folder, 'rightMask')
    left_masks = sorted(os.listdir(left_mask_dir))
    right_masks = sorted(os.listdir(right_mask_dir))
    # Ensure both directories have the same number of files
    assert len(left_masks) == len(right_masks), "Masks in both directories must have the same number of files."

    # Process and combine the masks
    for left_mask_name, right_mask_name in zip(left_masks, right_masks):
        # Load the left and right mask images
        left_mask_path = os.path.join(left_mask_dir, left_mask_name)
        right_mask_path = os.path.join(right_mask_dir, right_mask_name)

        left_mask = np.array(Image.open(left_mask_path))
        right_mask = np.array(Image.open(right_mask_path))

        # Assert both images have the same size
        assert left_mask.shape == right_mask.shape, (f"Masks {left_mask_name} and {right_mask_name}"
                                                     f" must have the same size.")

        # Combine the masks using a logical OR operation
        combined_mask = np.maximum(left_mask, right_mask)

        # Save the combined mask in the output directory
        output_path = os.path.join(masks_folder, left_mask_name)
        plt.imsave(output_path, combined_mask, cmap='gray')

    # Remove the original left and right masks directories
    shutil.rmtree(left_mask_dir)
    shutil.rmtree(right_mask_dir)

    # Remove every directory other than the images and masks directories
    for root, dirs, files in os.walk(montgomery_dir):
        for dir_name in dirs:
            if dir_name not in ['CXR_png', 'ManualMask']:
                shutil.rmtree(os.path.join(root, dir_name))


if __name__ == "__main__":
    result = download_montgomery_dataset()
    if result == 0:
        print("Montgomery dataset downloaded and organized successfully.")
    elif result == 1:
        print("Montgomery dataset already exists.")
    else:
        print("Failed to download Montgomery dataset.")
