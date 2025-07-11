# Generated from PROBE using Acceleo
from typing import List
from python_application.generated_code.model.Point import Point
from python_application.generated_code.model.BoundingBox import BoundingBox
from python_application.generated_code.model.Prompt import Prompt


class PromptForImage(Prompt):
    """Represents a PromptForImage object."""
    def __init__(self
, point: List[Point]
, bounding_box: List[BoundingBox]
):
        """
        :param point: point of the PromptForImage
        :param bounding_box: bounding_box of the PromptForImage
        """
        self.point = point
        self.bounding_box = bounding_box
