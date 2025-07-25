# Generated from PROBE using Acceleo
from typing import List
from python_application.generated_code.enumerations.OptimizationAlgorithm import OptimizationAlgorithm
from python_application.generated_code.model.Metric import Metric
from python_application.generated_code.model.FoundationModel import FoundationModel
from python_application.generated_code.model.Metric import Metric
from python_application.generated_code.model.Experiment import Experiment


class OptimizationTask:
    """Represents a OptimizationTask object."""
    def __init__(self
, name: str, description: str, algorithm: OptimizationAlgorithm, performance_metric: List[Metric]
, foundation_model: FoundationModel
, optimization_metric: Metric
, experiment: List[Experiment]
):
        """
        :param name: name of the OptimizationTask
        :param description: description of the OptimizationTask
        :param algorithm: algorithm of the OptimizationTask
        :param performance_metric: performance_metric of the OptimizationTask
        :param foundation_model: foundation_model of the OptimizationTask
        :param optimization_metric: optimization_metric of the OptimizationTask
        :param experiment: experiment of the OptimizationTask
        """
        self.name = name
        self.description = description
        self.algorithm = algorithm
        self.performance_metric = performance_metric
        self.foundation_model = foundation_model
        self.optimization_metric = optimization_metric
        self.experiment = experiment
