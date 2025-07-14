# Generated from PROBE using Acceleo
from python_application.generated_code.enumerations.PointType import PointType
from python_application.generated_code.model.Coordinates import Coordinates


class Point:
    """Represents a Point object."""

    def __init__(self, type: PointType, coordinates: Coordinates):
        """
        :param type: type of the Point
        :param coordinates: coordinates of the Point
        """
        self.type = type
        self.coordinates = coordinates
