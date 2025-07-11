# Probe Metamodel and Model Project

This project contains the Eclipse EMF project with the `probe.ecore` metamodel and its graphical visualization `probe.aird` and model `/probe/model/PROBE_coronacases_optimization.xmi` model.

## 1. Workspace Configuration

To work with this project, you need to install the Eclipse IDE for Java Developers and the Eclipse Modeling Tools package. You can download it from the [Eclipse Downloads page](https://www.eclipse.org/downloads/). After installing Eclipse, you can import this project into your workspace by following these steps:

1. Open Eclipse IDE.
2. Go to `File` > `Import...`.
3. Select `Projects from Folder or Archive` and click `Next`.
4. Browse to the location of this project and select the `probe` folder and click `Finish`.
5. (Optional) If not done yet, right-click on the project in the Project Explorer and select `Configure` > `Convert to Modelling Project`.

## 2. Metamodel and Model definition

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

## License

This project is licensed under the [MIT License](LICENSE).
