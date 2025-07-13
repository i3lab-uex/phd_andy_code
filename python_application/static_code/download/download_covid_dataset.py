
import os
from pathlib import Path

from python_application.static_code.download.download_helpers import download_file_with_progress, extract_zip


def download_covid_dataset() -> int:
    """
    Download the COVID-19 CT segmentation dataset.

    :return: 1 if the dataset has already been downloaded, 0 if the download was successful,
    -1 if the download failed
    """
    # Check if the dataset has been previously downloaded and the dataset path exists. If so, return 1
    if (Path('datasets/covid/COVID-19-CT-Seg_20cases').exists() and Path('datasets/covid/Lung_Mask') and
            any(Path('datasets/covid/COVID-19-CT-Seg_20cases').rglob('*.nii*')) and any(
                Path('datasets/covid/Lung_Mask').rglob('*.nii*'))):
        return 1

    # Create a folder for the datasets if it doesn't exist
    datasets_dir = './datasets/' + str(Path('covid'))
    os.makedirs(datasets_dir, exist_ok=True)

    # Download and unpack datasets
    for url in ['https://zenodo.org/record/3757476/files/COVID-19-CT-Seg_20cases.zip',
                'https://zenodo.org/record/3757476/files/Lung_Mask.zip']:
        if url is None:
            continue
        filename = url.split('/')[-1]
        local_path = os.path.join(datasets_dir, filename)

        try:
            print(f"Downloading {filename}...")
            download_file_with_progress(url, local_path)
        except Exception as e:
            print(f"Download failed: {e}")
            return -1

        print(f"\nExtracting {filename}...")
        extract_to = os.path.join(datasets_dir, filename.replace('.zip', ''))
        extract_zip(local_path, extract_to)

        # Remove the ZIP file after extraction
        os.remove(local_path)

    # The dataset has been downloaded successfully
    return 0


if __name__ == "__main__":
    result = download_covid_dataset()
    if result == 1:
        print("Dataset already downloaded.")
    elif result == 0:
        print("Dataset downloaded successfully.")
    else:
        print("Failed to download the dataset.")

