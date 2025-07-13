# Python Application for PROBE Project

This project contains the Python application that uses the generated code from the Acceleo project. The main script is located at `python_application/probe_demo.py`.

## 1. Requirements

- Python 3.10
- Cuda 12.1.0
- Torch 2.5.0
- SAM and SAM2 Installation
- Required Python packages (see `requirements.txt`)

## 2. Workspace Configuration

Although this project has been developed with PyCharm and Visual Studio Code on Windows, taking advantage of the WSL allows you to work on the Linux subsystem.
The following instructions are based on a Linux environment.
Below you can find the steps to configure a Windows environment.
Change what you need for your platform.

1. Install miniconda to manage Python virtual environments:

    ```shell
    curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh
    ```

2. Create and activate a new environment:

    ```shell
    conda create --name probe python=3.10 --yes
    conda activate probe
    ```

3. Clean conda and pip caches:

    ```shell
    conda clean --all --yes
    pip cache purge
    ```

    This step will prevent you from retrieving libraries from the conda or pip caches, which may be incompatible with the project's requirements.
    If you are sure that the libraries in the cache are compatible, you can skip this step.

4. [Install CUDA][cuda_installation] specific version to use SAM 1 and SAM 2:

    ```shell
    conda install nvidia/label/cuda-12.1.0::cuda --yes
    ```

    [cuda_installation]: https://anaconda.org/nvidia/cuda "CUDA Installation"

5. Install PyTorch, Torchvision, and Torchaudio:

    ```shell
    pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
    ```
   
6. Install this project's requirements:

    ```shell
    pip install -r requirements.txt
    ```

7. Execute the python script **image_segmentation/download/download_model_checkpoints.py** to get SAM's (SAM 1 and SAM 2) model checkpoints:

    ```shell
    python -m python_application.static_code.download.download_model_checkpoints
    ```
   
8. Configure PyCharm.
    If you are working on Windows, make sure you use WSL and that your interpreter is also based on WSL.

    > **Note:** Be careful with the EOL configuration in your IDE. Always choose LF instead of CRLF to avoid compatibility issues, as this is a multiplatform project.

> **Note:** If you no longer need the Conda environment, just deactivate it with `conda deactivate` and delete it with `conda remove -n probe --all --yes`.

### 2.1 SAM 1 Installation

- [Install SAM 1][sam_installation]: to install SAM 1 version, execute the following command, based on the [official installation instructions][sam_installation].

    ```shell
    pip install git+https://github.com/facebookresearch/segment-anything.git
    ```

    [sam_installation]: https://github.com/facebookresearch/segment-anything/?tab=readme-ov-file#installation "SAM 1 Installation"

### 2.2 SAM 2 Installation

- [Install SAM 2][sam2_installation]: to install the SAM 2 version, execute the following command, based on the [official installation instructions][sam2_installation].

  - Via SSH: you need a public SSH key in your GitHub account.

    ```shell
    git clone git@github.com:facebookresearch/segment-anything-2.git
    cd segment-anything-2
    pip install .
    pip install ".[demo]"
    ```

  - Via HTTPS: you don't need a public SSH key in your GitHub account.

    ```shell
    git clone https://github.com/facebookresearch/segment-anything-2.git
    cd segment-anything-2
    pip install .
    pip install ".[demo]"
    ```

    > **Note**: In the previous steps, I understand that the second **pip** does the same as the first but installs more stuff.
    I'm not sure, so I leave them both.
    During the video prediction process, a warning appears:
    Skipping the post-processing step due to the error above. You can still use SAM 2 ignoring the error above, although some post-processing functionality may be limited.

    [sam2_installation]: https://github.com/facebookresearch/segment-anything-2/?tab=readme-ov-file#installation "SAM 2 Installation"

  - Copy SAM 2 configuration profiles to the root folder of this project:
    
    ```shell
    cd ..
    mkdir sam2_configs
    cp segment-anything-2/sam2/configs/sam2/* sam2_configs
    cp segment-anything-2/sam2/configs/sam2.1/* sam2_configs
     ```

  [sam2_installation]: https://github.com/facebookresearch/segment-anything-2/?tab=readme-ov-file#installation "SAM 2 Installation"
  [warning_web_page]: https://github.com/facebookresearch/segment-anything-2/blob/main/INSTALL.md#building-the-sam-2-cuda-extension "Building the SAM 2 CUDA extension"

## 3. Download Covid-19 Dataset

To download the Covid-19 dataset, execute the python script **download_covid_dataset.py** from the root folder of this project:

```shell
python -m python_application.static_code.download.download_covid_dataset
```

## 4. Use the PROBE GUI demo

To use the PROBE GUI demo, execute the python script **probe_demo.py** from the root folder of this project:

```shell
python -m python_application.generated_code.probe_demo
```

## Project Structure

The project is structured as follows:

```
phd2_code/
│
└── python_application/            # Python application
    │
    ├── generated_code/            # Generated code from Acceleo
    │   ├── enumerations/          # Enumerations
    │   ├── model/                 # Model classes
    │   └── probe_demo.py          # Main script for the demo
    │
    ├── static_code/               # Static code
    │   ├── download/              # Download scripts
    │   ├── model/                 # Model definitions
    │   ├── genetic_algorithm/     # Genetic algorithm implementation
    │   └── probe_interface/       # Interface for the PROBE GUI
    │
    └── README.md                  # Project documentation
```

## License

This project is licensed under the [MIT License](LICENSE).
