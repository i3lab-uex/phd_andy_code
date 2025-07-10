# Generated from PROBE using Acceleo
from enumerations.ModelType import ModelType


class FoundationModel:
    """Represents a FoundationModel object."""
    def __init__(self
, name: str, version: float, description: str, checkpointFilepath: str, configuration: str, type: ModelType):
        """
        :param name: name of the FoundationModel
        :param version: version of the FoundationModel
        :param description: description of the FoundationModel
        :param checkpointFilepath: checkpointFilepath of the FoundationModel
        :param configuration: configuration of the FoundationModel
        :param type: type of the FoundationModel
        """
        self.name = name
        self.version = version
        self.description = description
        self.checkpointFilepath = checkpointFilepath
        self.configuration = configuration
        self.type = type
