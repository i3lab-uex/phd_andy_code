# Generated from PROBE using Acceleo
from enumerations.PointType import PointType
from model.Coordinates import Coordinates


class Point:
    """Represents a Point object."""
    def __init__(self
, type: PointType, coordinates: Coordinates
):
        """
        :param type: type of the Point
        :param coordinates: coordinates of the Point
        """
        self.type = type
        self.coordinates = coordinates
