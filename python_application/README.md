# Python Application for PROBE Project

This project contains the Python application that uses the generated code from the Acceleo project. The main script is located at `python_application/probe_demo.py`.

## Table of Contents

1. [Requirements](#requirements)
2. [Workspace Configuration](#workspace-configuration)
   - [SAM 1 Installation](#sam-1-installation)
3. [Covid-19 Dataset Download](#covid-19-dataset-download)
4. [Generate Code from Acceleo](#generate-code-from-acceleo)
5. [Use the PROBE GUI demo](#use-the-probe-gui-demo)
6. [Project Structure](#project-structure)
7. [Citing This Work](#citing-this-work)

## Requirements

- Python 3.10
- Cuda 12.1.0
- Torch 2.5.0
- SAM Installation
- Required Python packages (see `requirements.txt`)

## Workspace Configuration

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

4. [Install CUDA][cuda_installation] specific version to use SAM:

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

7. Execute the python script **python_application/static_code/download/DownloadModelCheckpoints.py** to get SAM's model checkpoints:

    ```shell
    python -m python_application.static_code.download.DownloadModelCheckpoints
    ```
   
8. Configure PyCharm.
    If you are working on Windows, make sure you use WSL and that your interpreter is also based on WSL.

    > **Note:** Be careful with the EOL configuration in your IDE. Always choose LF instead of CRLF to avoid compatibility issues, as this is a multiplatform project.

> **Note:** If you no longer need the Conda environment, just deactivate it with `conda deactivate` and delete it with `conda remove -n probe --all --yes`.

### SAM Installation

- [Install SAM][sam_installation]: to install SAM version, execute the following command, based on the [official installation instructions][sam_installation].

    ```shell
    pip install git+https://github.com/facebookresearch/segment-anything.git
    ```

    [sam_installation]: https://github.com/facebookresearch/segment-anything/?tab=readme-ov-file#installation "SAM Installation"

## Download Covid-19 Dataset

To download the Covid-19 dataset, execute the python script **python_application/static_code/download/DownloadCovidDataset.py** from the root folder of this project:

```shell
python -m python_application.static_code.download.DownloadCovidDataset
```

## Generate Code from Acceleo

Generate python code from Acceleo following the instructions in the [Acceleo project README](../probe_code_generation/README.md).

## Format generated code using Ruff Code Formatter Linter

To format the generated code using Ruff, execute the following command from the root folder of this project:

```shell
ruff format python_application/generated_code
```

## Use the PROBE GUI demo

To use the PROBE GUI demo, execute the python script **ProbeDemo.py** from the root folder of this project:

```shell
python -m python_application.generated_code.PROBEDemo
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


## Citing This Work

If you use this work in your research, please cite us with the following BibTeX entry:

```
@ARTICLE{gutierrez25,
  author={Gutiérrez, Juan D. and Delgado, Emilio and Breuer, Carlos, Conejero, José M., and Rodriguez-Echeverria, Roberto},
  journal={Algorithms},
  title={Prompt Once, Segment Everything: Leveraging SAM 2 Potential for Infinite Medical Image Segmentation With a Single Prompt},
  year={2025},
  volume={},
  number={},
  pages={1-1},
  doi={10.1000/182}}

```
