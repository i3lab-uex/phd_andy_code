# Generated from PROBE using Acceleo
from python_application.generated_code.model.StopCondition import StopCondition


class TimeLimit(StopCondition):
    """Represents a TimeLimit object."""
    def __init__(self
, minutesDuration: float):
        """
        :param minutesDuration: minutesDuration of the TimeLimit
        """
        self.minutesDuration = minutesDuration
