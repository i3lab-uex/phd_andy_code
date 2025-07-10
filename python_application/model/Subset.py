# Generated from PROBE using Acceleo
from typing import List
from model.Sample import Sample


class Subset:
    """Represents a Subset object."""
    def __init__(self
, name: str, path: str, dataFolderName: str, labelsFolderName: str, sample: List[Sample]
):
        """
        :param name: name of the Subset
        :param path: path of the Subset
        :param dataFolderName: dataFolderName of the Subset
        :param labelsFolderName: labelsFolderName of the Subset
        :param sample: sample of the Subset
        """
        self.name = name
        self.path = path
        self.dataFolderName = dataFolderName
        self.labelsFolderName = labelsFolderName
        self.sample = sample
