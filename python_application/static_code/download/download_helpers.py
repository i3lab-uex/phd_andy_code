from urllib.request import urlretrieve
from zipfile import ZipFile


def download_file_with_progress(url: str, local_filename: str):
    """
    Download the file and show a progress bar with size format

    Params:
    :param url: The URL of the file to download.
    :param local_filename: The local path to save the downloaded file.
    """
    urlretrieve(url, local_filename, reporthook=show_progress)


def extract_zip(zip_file_path: str, extract_to: str):
    """
    Extracts a ZIP file to the specified directory

    Params:
    :param zip_file_path: The path to the ZIP file to extract.
    :param extract_to: The directory to extract the ZIP file to.
    """
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def human_readable_size(size: int, decimal_places: int = 2):
    """
    Converts bytes to a more readable format (KB, MB, GB, TB)

    Params:
    :param size: (int) The size in bytes to convert.
    :param decimal_places: (int) The number of decimal places to include.
    :return: (str) The size in a more readable format.
    """
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def show_progress(block_num: int, block_size: int, total_size: int):
    """
    Displays a progress bar with more readable file size units

    params:
    :param block_num: The number of blocks downloaded.
    :param block_size: The size of each block.
    :param total_size: The total size of the file.
    """
    downloaded = block_num * block_size
    progress = min(int(50 * downloaded / total_size), 50)
    progress_bar = "=" * progress + "-" * (50 - progress)
    readable_downloaded = human_readable_size(downloaded)
    readable_total = human_readable_size(total_size)
    print(f"\r[{progress_bar}] {readable_downloaded}/{readable_total}        ", end="")
    if downloaded >= total_size:
        print()
