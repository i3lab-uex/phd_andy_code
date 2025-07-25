# PROBE Code Generation Project

This project contains the Acceleo code generation project with the code transformations in the mtl file `/probe_code_generation/src/probe_Acceleo_code_generation/main/generate.mtl`.

## Table of Contents

1. [Workspace Configuration](#workspace-configuration)
2. [Code Generation](#code-generation)
3. [Project Structure](#project-structure)
4. [Citing This Work](#citing-this-work)

## Workspace Configuration

To work with this project, you need to install the Eclipse IDE for Java Developers and the Eclipse Modeling Tools package, as well as in the [Probe Metamodel and Model Project](../probe/README.md). You can download it from the [Eclipse Downloads page](https://www.eclipse.org/downloads/). Aditionally, you need to install the Acceleo plugin for Eclipse. You can do this in Eclipse IDE by going to `Help` > `Eclipse Marketplace...` and searching for "Acceleo". After installing the Acceleo plugin, you can import this project into your workspace by following these steps:

1. Open Eclipse IDE.
2. Go to `File` > `Import...`.
3. Select `Projects from Folder or Archive` and click `Next`.
4. Browse to the location of this project and select the `probe_code_generation` folder and click `Finish`.
5. (Optional) If not done yet, right-click on the project in the Project Explorer and select `Configure` > `Convert to Acceleo Project`.

## Code Generation

To generate the code from the Acceleo project, follow these steps:

1. Right-click on the `probe_code_generation` project in the Project Explorer.
2. Select `Run As` > `Launch Acceleo Application`.
3. In the dialog that appears, select the model file you want to use for code generation (e.g., `PROBE_coronacases_optimization.xmi` from the `probe/model` folder), filling the other fields the same way it is shown in the following image:
   

![Acceleo Code Generation](../resources/images/acceleo_code_generation_configuration.png)


4. Click `Apply` and then `Run`.
5. The generated code will be placed in the folder the user has specified in the `Target` field of the dialog, which is `python_application/generated_paper` by default.


## Project Structure

The project is structured as follows:

```
phd2_code/
└── probe_code_generation/            # Acceleo code generation project
    ├── src/
    │   └── probe_Acceleo_code_generation/
    │       └── main/
    │           └── generate.mtl      # Code transformations
    └── README.md                     # Project documentation
```


If you have any questions or suggestions, feel free to contact us.

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
