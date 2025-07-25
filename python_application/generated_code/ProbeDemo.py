# Generated instance model for ProbeMM
import os
from python_application.static_code.ProbeInterface import ProbeInterface
from python_application.generated_code.enumerations.DeviceType import DeviceType
from python_application.generated_code.enumerations.MetricType import MetricType
from python_application.generated_code.enumerations.PointType import PointType
from python_application.generated_code.enumerations.FileFormatType import FileFormatType
from python_application.generated_code.enumerations.DataType import DataType
from python_application.generated_code.enumerations.ModelType import ModelType
from python_application.generated_code.enumerations.OptimizationAlgorithm import OptimizationAlgorithm
from python_application.generated_code.model.PROBE import PROBE
from python_application.generated_code.model.Dataset import Dataset
from python_application.generated_code.model.Metric import Metric
from python_application.generated_code.model.FoundationModel import FoundationModel
from python_application.generated_code.model.PromptForImage import PromptForImage
from python_application.generated_code.model.OptimizationTask import OptimizationTask
from python_application.generated_code.model.BoundingBox import BoundingBox
from python_application.generated_code.model.Point import Point
from python_application.generated_code.model.State import State
from python_application.generated_code.model.Sample import Sample
from python_application.generated_code.model.Subset import Subset
from python_application.generated_code.model.Experiment import Experiment
from python_application.generated_code.model.Prompt import Prompt
from python_application.generated_code.model.PromptForText import PromptForText
from python_application.generated_code.model.PromptForAudio import PromptForAudio
from python_application.generated_code.model.StopCondition import StopCondition
from python_application.generated_code.model.NoImprovement import NoImprovement
from python_application.generated_code.model.TimeLimit import TimeLimit
from python_application.generated_code.model.MaxIterations import MaxIterations

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
                path=os.path.join(os.getcwd(), "datasets/covid"),
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
            name="vit_h",
            version=1.0,
            description="SAM ViT-H",
            checkpointFilepath=os.path.join(os.getcwd(), "model_checkpoints/sam_vit_h_4b8939.pth"),
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
                        bounding_box=[BoundingBox()],
                        point=[Point(type=PointType.POSITIVE), Point(type=PointType.POSITIVE), Point(type=PointType.NEGATIVE)]
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
                        bounding_box=[BoundingBox()],
                        point=[Point(type=PointType.POSITIVE), Point(type=PointType.POSITIVE), Point(type=PointType.NEGATIVE)]
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
            name="vit_b",
            version=1.0,
            description="MedSAM ViT-B",
            checkpointFilepath=os.path.join(os.getcwd(), "model_checkpoints/medsam_vit_b_01ec64.pth"),
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
                        bounding_box=[BoundingBox()],
                        point=[Point(type=PointType.POSITIVE), Point(type=PointType.POSITIVE), Point(type=PointType.NEGATIVE)]
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
    
    # Print the starting message
    print("🚀 Starting PROBE - SAM Optimization Interface...")
    print("📝 Press Ctrl+C to exit")

    # Create and launch the interface
    interface = ProbeInterface(probe)
    interface.launch()

