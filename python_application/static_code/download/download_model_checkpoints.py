import os
from urllib.request import urlretrieve
import time
import math
from image_segmentation.model.SegModel import SegModel
import gdown
from huggingface_hub import hf_hub_download

MODEL_CHECKPOINTS_DIR = './model_checkpoints'


def format_size(size: int) -> str:
    """
    Format the size in bytes into a human-readable format

    params:
    :param size: The size in bytes to format
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


def download_model_checkpoint_with_progress(url: str, local_filename: str):
    """
    Download the file with a predefined progress bar

    params:
    :param url: URL of the file to download
    :param local_filename: Local path to save the downloaded file
    """

    def show_progress(block_num: int, block_size: int, total_size: int):
        """
        Show the download progress

        :param block_num: (int) Number of blocks downloaded
        :param block_size: (int) Size of each block
        :param total_size: (int) Total size of the file
        :return:
        """
        downloaded = block_num * block_size
        progress = int(downloaded / total_size * 100)
        elapsed_time = time.time() - start_time
        speed = downloaded / elapsed_time if elapsed_time > 0 else 0
        remaining_time = (total_size - downloaded) / speed if speed > 0 else 0
        if remaining_time < 1:
            remaining_time_str = " < 1s"
        else:
            remaining_time_str = f"{math.floor(remaining_time)}s"

        progress_bar_length = 50
        done_length = int(progress_bar_length * progress / 100)
        remaining_length = progress_bar_length - done_length
        progress_bar = '=' * done_length + '>' + '.' * remaining_length

        print(f"\r[{progress_bar}] {progress}% "
              f"({format_size(downloaded)}/{format_size(total_size)}, "
              f"Speed: {format_size(speed)}/s, "
              f"Time Remaining: {remaining_time_str}        ", end='')

    start_time = time.time()
    urlretrieve(url, local_filename, reporthook=show_progress)
    print()  # End the line after download


def _download_model_with_check(model_urls, sam_model, model_type, download_func):
    """
    Helper function to handle common model download logic

    :param model_urls: Dictionary of model names and their URLs/IDs
    :param sam_model: Specific model to download (optional)
    :param model_type: Type of model (e.g., 'SAM', 'SAM-2', 'MedSAM')
    :param download_func: Function to use for downloading
    """
    for model_name, url in model_urls.items():
        if sam_model is not None and sam_model.name not in model_name:
            continue

        local_path = os.path.join(MODEL_CHECKPOINTS_DIR, model_name)
        if not os.path.exists(local_path):
            print(f"Starting download of {model_name} {model_type} model...")
            download_func(url, local_path)
            print(f"{model_type} {model_name} model download has been completed.")
        else:
            print(f"{model_type} {model_name} model has already been downloaded. Skipping download.")


def download_sam_model_checkpoints(sam_model: SegModel = None):
    """
    Download the model checkpoints for SAM model

    :param sam_model: SAM model to download
    """
    model_urls = {
        "sam_vit_b_01ec64.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
        # SAM-ViT-B
        "sam_vit_l_0b3195.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
        # SAM-ViT-L
        "sam_vit_h_4b8939.pth": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        # SAM-ViT-H
    }
    _download_model_with_check(model_urls, sam_model, "SAM", download_model_checkpoint_with_progress)


def download_sam2_model_checkpoints(sam_model: SegModel = None):
    """
    Download the model checkpoints for SAM2 model

    :param sam_model: SAM-2 specific model to download
    :return:
    """
    model_urls = {
        # SAM2-Hiera-Tiny
        "sam2_hiera_t.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_tiny.pt",
        # SAM2-Hiera-Small
        "sam2_hiera_s.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_small.pt",
        # SAM2-Hiera-Base+
        "sam2_hiera_b_plus.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_base_plus.pt",
        # SAM2-Hiera-Large
        "sam2_hiera_l.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_large.pt",
        # SAM2.1-Hiera-Tiny
        "sam2p1_hiera_t.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt",
        # SAM2.1-Hiera-Small
        "sam2p1_hiera_s.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt",
        # SAM2.1-Hiera-Base+
        "sam2p1_hiera_b_plus.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt",
        # SAM2.1-Hiera-Large
        "sam2p1_hiera_l.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt",
    }
    _download_model_with_check(model_urls, sam_model, "SAM-2", download_model_checkpoint_with_progress)


def download_medsam_model_checkpoints(sam_model: SegModel = None):
    """
    Download the model checkpoints for MedSAM model

    :param sam_model: MedSAM specific model to download
    """
    model_urls = {
        # MedSAM-ViT-B
        "medsam_vit_b_01ec64.pth": "1UAmWL88roYR7wKlnApw5Bcuzf2iQgk6_",
        # LiteMedSAM-ViT-B
        "lite_medsam.pth": "18Zed-TUTsmr2zc5CHUWd5Tu13nb6vq6z"
    }

    def download_from_gdrive(drive_id, local_path):
        gdown.download(f"https://drive.google.com/uc?id={drive_id}", local_path, quiet=False)

    _download_model_with_check(model_urls, sam_model, "MedSAM", download_from_gdrive)


def download_medsam2_model_checkpoints():
    # List of model filenames
    wanglab_model_files = [
        "MedSAM2_2411.pt",
        "MedSAM2_US_Heart.pt",
        "MedSAM2_MRI_LiverLesion.pt",
        "MedSAM2_CTLesion.pt",
        "MedSAM2_latest.pt"
    ]

    jiayuanz3_model_files = [
        "MedSAM2_pretrain.pth"
    ]

    # Download all models
    for model_file in wanglab_model_files:
        local_path = os.path.join(MODEL_CHECKPOINTS_DIR, model_file)
        hf_hub_download(
            repo_id="wanglab/MedSAM2",
            filename=model_file,
            local_dir=MODEL_CHECKPOINTS_DIR,
            local_dir_use_symlinks=False
        )
        print(f"Downloaded {model_file} to {local_path}")

    for model_file in jiayuanz3_model_files:
        local_path = os.path.join(MODEL_CHECKPOINTS_DIR, model_file)
        hf_hub_download(
            repo_id="jiayuanz3/MedSAM2_pretrain",
            filename=model_file,
            local_dir=MODEL_CHECKPOINTS_DIR,
            local_dir_use_symlinks=False
        )
        print(f"Downloaded {model_file} to {local_path}")


def main():
    # Create folder for the model checkpoints, if it doesn't exist
    os.makedirs(MODEL_CHECKPOINTS_DIR, exist_ok=True)

    # Download the model checkpoints for SAM
    download_sam_model_checkpoints()

    # Download the model checkpoints for MedSAM
    download_medsam_model_checkpoints()

    # Download the model checkpoints for SAM-2
    download_sam2_model_checkpoints()

    # Download the model checkpoints for MedSAM2
    download_medsam2_model_checkpoints()


if __name__ == "__main__":
    main()
