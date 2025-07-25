# Generated from PROBE using Acceleo
from python_application.generated_code.model.StopCondition import StopCondition


class MaxIterations(StopCondition):
    """Represents a MaxIterations object."""

    def __init__(self, numIterations: int):
        """
        :param numIterations: numIterations of the MaxIterations
        """
        self.numIterations = numIterations
