# Generated from PROBE using Acceleo
from typing import List
from model.Point import Point
from model.BoundingBox import BoundingBox
from model.Prompt import Prompt


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
