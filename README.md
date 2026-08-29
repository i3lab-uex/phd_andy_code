# PROBE: una propuesta conceptual de software dirigida por modelos para explorar los límites de los modelos fundacionales orientados a prompt aplicados a tareas específicas

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22159446.svg)](https://doi.org/10.5281/zenodo.22159446)

This project contains the code projects for the PhD work entitled "PROBE: una propuesta conceptual de software dirigida por modelos para explorar los límites de los modelos fundacionales orientados a prompt aplicados a tareas específicas".
The code is organized into the following directories, each one corresponding to a different project characteristic:

- `PROBE`: Contains the Eclipse EMF project with the `PROBE.ecore` metamodel, its graphical clas diagram visualization `PROBE.aird`, and its model XML instance file `PROBE/model/PROBE_coronacases_optimization.xmi`.
You can find the metamodel and model instructions in the corresponding [README.md](PROBE/README.md) file.

- `PROBE_code_generation`: Contains the Acceleo code generation project with the code transformations in the MTL file `PROBE_code_generation/src/PROBE_Acceleo_code_generation/main/generate.mtl`.
You can find the code generation instructions in the [README.md](PROBE_code_generation/README.md) file.

- `python_application`: Contains the Python application that uses the generated code from Acceleo and the static one.
The main script is located at `python_application/PROBEDemo.py`.
You can find the Python application instructions in the [README.md](python_application/README.md) file.

## Table of Contents

1. [PROBE Metamodel](#probe-metamodel)
2. [Project Structure](#project-structure)
3. [Citing This Work](#citing-this-work)

## PROBE Metamodel

The metamodel of the PROBE project is presented in the following image:

![PROBE Metamodel](PROBE/metamodel/images/PROBEMM.png)

## Project Structure

The project is structured as follows:

```
phd2_code/
├── PROBE/                             # Eclipse EMF project
│   ├── metamodel/
│   │   ├── PROBE.aird                 # Graphical visualization
│   │   └── PROBE.ecore                # Metamodel definition
│   ├── model/                         # Model folder
│   │   └── PROBE_coronacases_optimization.xmi  # Example model
│   └── README.md                      # Project documentation
│
├── PROBE_code_generation/             # Acceleo code generation project
│   ├── src/
│   │   └── PROBE_Acceleo_code_generation/
│   │       └── main/
│   │           └── generate.mtl       # Code transformations
│   └── README.md                      # Project documentation
│
├── python_application/                # Python application
│   ├── generated_code/                # Generated code from Acceleo
│   │   ├── enumerations/              # Enumerations
│   │   ├── model/                     # Model classes
│   │   └── PROBEDemo.py              # Main script for the demo
│   │
│   ├── static_code/                   # Static code
│   │   └── ...                        # Interface for the PROBE GUI
│   └── README.md                      # Project documentation
│   
├── resources/                         # Resources folder
│   └── images/                        # Images used in the project
│
├── .gitignore                         # Git ignore file
├── .pre-commit-config.yaml            # Pre-commit configuration file
├── CITATION.cff                       # Citation file for the project
├── README.md                          # General repository documentation
├── requirements.txt                   # Python package requirements
└── TODO                               # Project license
```

## Citing This Work

If you use this work in your research, please cite us with the following BibTeX entry:

```
@phdthesis{gutierrez2026,
  author       = {Juan Diego Gutiérrez Gallardo},
  title        = {PROBE: una propuesta conceptual de software dirigida por modelos para explorar los límites de los modelos fundacionales orientados a prompt aplicados a tareas específicas},
  school       = {Universidad de Extremadura},
  year         = {2026},
  address      = {Cáceres, España},
  month        = {jun},
  type         = {Tesis Doctoral},
  note         = {Dirigida por Dr. Roberto Rodríguez Echeverría y Dr. José María Conejero Manzano},
  url          = {https://github.com/andyuex/phd2_code},
  abstract     = {Los modelos fundacionales de inteligencia artificial (IA) orientados a prompt presentan un potencial sin precedentes para resolver tareas complejas, desde la generación de texto coherente hasta el reconocimiento de objetos en imágenes.
Sin embargo, su aplicación efectiva en dominios específicos sin incurrir en costosos procesos de reentrenamiento o ajuste fino (fine-tuning) constituye un desafío fundamental.
Además, no existe una metodología sistemática que permita evaluar su rendimiento al aplicarlos a una tarea específica, ni comparar el funcionamiento de diferentes versiones del mismo modelo.
Esta tesis aborda directamente dichas carencias, explorando tres cuestiones clave: 1) la viabilidad de aplicar un modelo de propósito general a una tarea específica (downstream task) mediante la optimización de la interacción (prompting), 2) la existencia y cuantificación de un techo de rendimiento inherente a esta aproximación no intrusiva, y 3) la transferencia directa de mejoras a la tarea específica cuando el modelo base evoluciona.
Para dar respuesta a estos desafíos de manera sistemática, se realiza una propuesta sistemática dirigida por modelos que formaliza un marco metodológico para la exploración y evaluación de los límites de rendimiento de modelos fundacionales orientados a prompts llamada PROBE (Prompt Optimization for Boundary Exploration, Optimización de Prompts para la Exploración de Límites).
Esta propuesta establece un proceso estructurado para determinar el máximo potencial de un modelo fundacional aplicado a una tarea especializada, permitiendo a los usuarios tomar decisiones informadas sobre su idoneidad y estrategia de implementación.
La propuesta se valida empíricamente a través de un caso de estudio en segmentación de imágenes, demostrando la capacidad de la propuesta para guiar la optimización y medir sus límites de forma efectiva.},
  keywords = {ingeniería dirigida por modelos, metamodelado, PROBE, modelos fundacionales, límites de rendimiento, transferencia zero-shot, optimización de prompts, algoritmos genéticos, SAM, segmentación de imágenes médicas},
  language     = {Spanish}
}
```
