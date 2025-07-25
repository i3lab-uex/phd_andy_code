# Generated from PROBE using Acceleo
from python_application.generated_code.model.Prompt import Prompt


class State:
    """Represents a State object."""
    def __init__(self
, description: str, hasImproved: bool, prompt: Prompt
):
        """
        :param description: description of the State
        :param hasImproved: hasImproved of the State
        :param prompt: prompt of the State
        """
        self.description = description
        self.hasImproved = hasImproved
        self.prompt = prompt
