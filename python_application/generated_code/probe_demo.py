# Generated instance model for ProbeMM
from enumerations.DeviceType import DeviceType
from enumerations.MetricType import MetricType
from enumerations.PointType import PointType
from enumerations.FileFormatType import FileFormatType
from enumerations.DataType import DataType
from enumerations.ModelType import ModelType
from enumerations.OptimizationAlgorithm import OptimizationAlgorithm
from model.PROBE import PROBE
from model.Dataset import Dataset
from model.Metric import Metric
from model.FoundationModel import FoundationModel
from model.PromptForImage import PromptForImage
from model.OptimizationTask import OptimizationTask
from model.BoundingBox import BoundingBox
from model.Point import Point
from model.State import State
from model.Sample import Sample
from model.Subset import Subset
from model.Experiment import Experiment
from model.Prompt import Prompt
from model.PromptForText import PromptForText
from model.PromptForAudio import PromptForAudio
from model.StopCondition import StopCondition
from model.NoImprovement import NoImprovement
from model.TimeLimit import TimeLimit
from model.MaxIterations import MaxIterations
from model.Coordinates import Coordinates
from python_application.static_code.probe_interface import ProbeInterface

# Processing device
processing_device = DeviceType.NVIDIA

# Build datasets
datasets = [
    Dataset(
        name="Coronacases",
        description="Lung CT (Coronacases Dataset)",
        type=DataType.IMAGE,
        subset=[
            Subset(
                name="trainingSet",
                path="/mnt/c/Users/Usuario/PycharmProjects/mismef/datasets/covid",
                dataFolderName="COVID-19-CT-Seg_20cases",
                labelsFolderName="Lung_Mask",
                sample=[
                    Sample(
                        filename="coronacases_001.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_002.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_003.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_004.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_005.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_006.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_007.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_008.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_009.nii.gz",
                        extension=FileFormatType.NIFTI
                    ),
                    Sample(
                        filename="coronacases_010.nii.gz",
                        extension=FileFormatType.NIFTI
                    )                ]
            )        ]
    )]

# Build optimization tasks
optimization_task = [
    OptimizationTask(
        name="Genetic Algorithms",
        description="Tarea de optimización mediante el uso de algoritmos genéticos",
        algorithm=OptimizationAlgorithm.GENETIC,
        foundation_model=FoundationModel(
            name="vit_b",
            version=1.0,
            description="MedSAM ViT-B",
            checkpointFilepath="/mnt/c/Users/Usuario/PycharmProjects/mismef/model_checkpoints/medsam_vit_b_01ec64.pth",
            configuration="",
            type=ModelType.IMAGE_SEGMENTATION
        ),
        experiment=[
            Experiment(
                name="Experiment 1 - coronacases_001",
                initial_state=State(
                    description="Experiment 1 Initial State",
                    hasImproved=False,
                    prompt=PromptForImage(
                        bounding_box=[BoundingBox(min_coordinates=Coordinates(x=102, y=218), max_coordinates=Coordinates(x=400, y=437))],
                        point=[Point(type=PointType.POSITIVE, coordinates=Coordinates(x=347, y=325)), Point(type=PointType.POSITIVE, coordinates=Coordinates(x=166, y=327)), Point(type=PointType.NEGATIVE, coordinates=Coordinates(x=251, y=327))]
                    )
                ),
                stop_condition=[NoImprovement(), TimeLimit(minutesDuration=5.0), MaxIterations(numIterations=1000)],
                sample=Sample(
                    filename="coronacases_001.nii.gz",
                    extension=FileFormatType.NIFTI
                )
            )
,
            Experiment(
                name="Experiment 2 - coronacases_002",
                initial_state=State(
                    description="Experiment 1 Initial State",
                    hasImproved=False,
                    prompt=PromptForImage(
                        bounding_box=[BoundingBox(min_coordinates=Coordinates(x=102, y=218), max_coordinates=Coordinates(x=400, y=437))],
                        point=[Point(type=PointType.POSITIVE, coordinates=Coordinates(x=347, y=325)), Point(type=PointType.POSITIVE, coordinates=Coordinates(x=166, y=327)), Point(type=PointType.NEGATIVE, coordinates=Coordinates(x=251, y=327))]
                    )
                ),
                stop_condition=[NoImprovement()],
                sample=Sample(
                    filename="coronacases_002.nii.gz",
                    extension=FileFormatType.NIFTI
                )
            )
        ],
        optimization_metric=Metric(name="Sam Score as an optimization metric", type=MetricType.SAM_SCORE),
        performance_metric=[
            Metric(name="Jaccard Index", type=MetricType.JACCARD,
   ),
            Metric(name="Dice Coefficient", type=MetricType.DICE,
   ),
            Metric(name="SAM Score", type=MetricType.SAM_SCORE,
   )    ]
    )
,
    OptimizationTask(
        name="Swarm Algorithms",
        description="Tarea de optimización mediante el uso de algoritmos de enjambres (SWARM)",
        algorithm=OptimizationAlgorithm.PARTICLE_SWARM,
        foundation_model=FoundationModel(
            name="SAM 2 Large",
            version=2.0,
            description="MedSAM ViT-h",
            checkpointFilepath="/mnt/c/Users/Usuario/PycharmProjects/mismef/model_checkpoints/sam2_hiera_l.pt",
            configuration="sam2_hiera_l.yaml",
            type=ModelType.IMAGE_SEGMENTATION
        ),
        experiment=[
            Experiment(
                name="Experiment 1 - coronacases_001",
                initial_state=State(
                    description="Experiment 1 Initial State",
                    hasImproved=False,
                    prompt=PromptForImage(
                        bounding_box=[BoundingBox(min_coordinates=Coordinates(x=102, y=218), max_coordinates=Coordinates(x=400, y=437))],
                        point=[Point(type=PointType.POSITIVE, coordinates=Coordinates(x=347, y=325)), Point(type=PointType.POSITIVE, coordinates=Coordinates(x=166, y=327)), Point(type=PointType.NEGATIVE, coordinates=Coordinates(x=251, y=327))]
                    )
                ),
                stop_condition=[NoImprovement(), TimeLimit(minutesDuration=5.0), MaxIterations(numIterations=1000)],
                sample=Sample(
                    filename="coronacases_001.nii.gz",
                    extension=FileFormatType.NIFTI
                )
            )
        ],
        optimization_metric=Metric(name="Sam Score as an optimization metric", type=MetricType.SAM_SCORE),
        performance_metric=[
            Metric(name="Jaccard Index", type=MetricType.JACCARD,
   ),
            Metric(name="Dice Coefficient", type=MetricType.DICE,
   ),
            Metric(name="SAM Score", type=MetricType.SAM_SCORE,
   )    ]
    )
]

# Build the PROBE instance
probe = PROBE(
    device=processing_device,
    dataset=datasets,
    optimization_task=optimization_task
)


if __name__ == "__main__":
    # Create and launch the interface
    interface = ProbeInterface(probe)
    interface.launch()
