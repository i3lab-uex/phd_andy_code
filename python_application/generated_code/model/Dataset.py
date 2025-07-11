# Generated from PROBE using Acceleo
from typing import List
from enumerations.DataType import DataType
from model.Subset import Subset


class Dataset:
    """Represents a Dataset object."""
    def __init__(self
, name: str, description: str, type: DataType, subset: List[Subset]
):
        """
        :param name: name of the Dataset
        :param description: description of the Dataset
        :param type: type of the Dataset
        :param subset: subset of the Dataset
        """
        self.name = name
        self.description = description
        self.type = type
        self.subset = subset
