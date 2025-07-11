# Generated from PROBE using Acceleo
from typing import List
from python_application.generated_code.model.State import State
from python_application.generated_code.model.Sample import Sample
from python_application.generated_code.model.StopCondition import StopCondition


class Experiment:
    """Represents a Experiment object."""
    def __init__(self
, name: str, initial_state: State
, sample: Sample
, stop_condition: List[StopCondition]
):
        """
        :param name: name of the Experiment
        :param initial_state: initial_state of the Experiment
        :param sample: sample of the Experiment
        :param stop_condition: stop_condition of the Experiment
        """
        self.name = name
        self.initial_state = initial_state
        self.sample = sample
        self.stop_condition = stop_condition
