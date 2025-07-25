# [Thesis Title]

This project contains the code projects for the thesis titled "[Thesis Title]". The code is organized into the following directories, each one corresponding to a different project nature:

- `probe` - Contains the Eclipse EMF project with the `probe.ecore` metamodel and its graphical clas diagram visualization `probe.aird` and its model xml instance file `probe/model/PROBE_coronacases_optimization.xmi`.


- `probe_code_generation` - Contains the Acceleo code generation project with the code transformations in the mtl file `probe_code_generation/src/probe_Acceleo_code_generation/main/generate.mtl`.


- `python_application` - Contains the Python application that uses the generated code from Acceleo and the static one. The main script is located at `python_application/ProbeDemo.py`.

> **Note:** The project instructions are provided in the respective `README.md` files within each project directory.

## Probe Metamodel

You can appreciate the metamodel of the PROBE project in the following image:

![Probe Metamodel](probe/metamodel/images/ProbeMM.png)


## Project Structure

The project is structured as follows:

```
phd2_code/
├── probe/                             # Eclipse EMF project
│   ├── metamodel/
│   │   ├── probe.aird                 # Graphical visualization
│   │   └── probe.ecore                # Metamodel definition
│   ├── model/                         # Model folder
│   │   └── PROBE_coronacases_optimization.xmi  # Example model
│   └── README.md                      # Project documentation
│
├── probe_code_generation/             # Acceleo code generation project
│   ├── src/
│   │   └── probe_Acceleo_code_generation/
│   │       └── main/
│   │           └── generate.mtl       # Code transformations
│   └── README.md                      # Project documentation
│
├── python_application/                # Python application
│   ├── generated_code/                # Generated code from Acceleo
│   │   ├── enumerations/              # Enumerations
│   │   ├── model/                     # Model classes
│   │   └── ProbeDemo.py              # Main script for the demo
│   │
│   ├── static_code/                   # Static code
│   │   └── ...                        # Interface for the PROBE GUI
│   └── README.md                      # Project documentation
│   
├── resources/                         # Resources folder
│   └── images/                        # Images used in the project
│
├── .gitignore                         # Git ignore file
├── README.md                          # General repository documentation
├── requirements.txt                   # Python package requirements
└── TODO                               # Project license
```

## License

This project is licensed under the [MIT License](LICENSE).
