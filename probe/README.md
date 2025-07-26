# PROBE Metamodel and Model Project

This project contains the Eclipse EMF project with the `probe.ecore` metamodel and its graphical visualization `probe.aird` and model `/probe/model/PROBE_coronacases_optimization.xmi` model.

## Table of Contents

1. [Workspace Configuration](#workspace-configuration)
2. [Metamodel and Model definition](#metamodel-and-model-definition)
3. [Project Structure](#project-structure)
4. [Citing This Work](#citing-this-work)

## Workspace Configuration

To work with this project, you need to install the Eclipse IDE for Java Developers and the Eclipse Modeling Tools package. You can download it from the [Eclipse Downloads page](https://www.eclipse.org/downloads/). After installing Eclipse, you can import this project into your workspace by following these steps:

1. Open Eclipse IDE.
2. Go to `File` > `Import...`.
3. Select `Projects from Folder or Archive` and click `Next`.
4. Browse to the location of this project and select the `probe` folder and click `Finish`.
5. (Optional) If not done yet, right-click on the project in the Project Explorer and select `Configure` > `Convert to Modelling Project`.

## Metamodel and Model definition

You can appreciate the metamodel of the PROBE project in the following image:

![Probe Metamodel](metamodel/images/ProbeMM.png)

The metamodel is defined in the `probe.ecore` file, and the graphical visualization is provided in the `probe.aird` file. The example model instance is located in the `model` folder as `PROBE_coronacases_optimization.xmi`.
In the following image, you can see the graphical representation of the probe example model:

![Probe Metamodel](../resources/images/probe_model.png)

## Project Structure

The project is structured as follows:

```
phd2_code/
└── probe/                                      # Eclipse EMF project
    │
    ├── metamodel/
    │   ├── images/                             # Images used in the metamodel
    │   ├── probe.aird                          # Graphical visualization
    │   └── probe.ecore                         # Metamodel definition
    │
    ├── model/                                  # Model folder
    │   └── PROBE_coronacases_optimization.xmi  # Example model
    │
    └── README.md                               # Project documentation
```

## Citing This Work

If you use this work in your research, please cite us with the following BibTeX entry:

```
@phdthesis{gutierrez2025,
  author       = {Juan Diego Gutiérrez Gallardo},
  title        = {PROBE: un metamodelo software para explorar los límites de los modelos fundacionales de segmentación de imágenes aplicados al dominio médico},
  school       = {Universidad de Extremadura},
  year         = {2025},
  address      = {Cáceres, España},
  month        = {jul},
  type         = {Tesis Doctoral},
  note         = {Dirigida por Dr. Roberto Rodríguez Echeverría y Dr. José María Conejero Manzano},
  url          = {https://github.com/andyuex/phd2_code},
  abstract     = {Esta tesis doctoral presenta PROBE, un metamodelo software para explorar los límites de rendimiento de modelos fundacionales de segmentación de imágenes mediante técnicas de optimización de prompts. La investigación se centra en el uso del modelo Segment Anything Model (SAM) en tareas de segmentación médica sin necesidad de reentrenamiento, proponiendo una metodología para cuantificar el techo de rendimiento alcanzable mediante algoritmos genéticos. A partir de casos de uso con imágenes médicas (CT, rayos X, MRI), se construye un marco formal que permite sistematizar el uso eficiente de estos modelos en escenarios de recursos limitados. Como contribuciones, se incluyen tres artículos científicos, artefactos software publicados en GitHub, un metamodelo reutilizable y validación empírica del enfoque propuesto.},
  keywords     = {modelos fundacionales, segmentación de imágenes médicas, prompts, SAM, algoritmos genéticos, metamodelos, inteligencia artificial médica},
  language     = {Spanish}
}
```
