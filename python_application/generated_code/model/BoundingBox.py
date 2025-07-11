# Generated from PROBE using Acceleo
from model.Coordinates import Coordinates
from model.Coordinates import Coordinates


class BoundingBox:
    """Represents a BoundingBox object."""
    def __init__(self
, min_coordinates: Coordinates
, max_coordinates: Coordinates
):
        """
        :param min_coordinates: min_coordinates of the BoundingBox
        :param max_coordinates: max_coordinates of the BoundingBox
        """
        self.min_coordinates = min_coordinates
        self.max_coordinates = max_coordinates
