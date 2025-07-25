# Generated from PROBE using Acceleo
from python_application.generated_code.enumerations.MetricType import MetricType


class Metric:
    """Represents a Metric object."""

    def __init__(self, name: str, type: MetricType, baseline: float = None):
        """
        :param name: name of the Metric
        :param type: type of the Metric
        :param baseline: baseline of the Metric
        """
        self.name = name
        self.type = type
        self.baseline = baseline
