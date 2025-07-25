# Generated from PROBE using Acceleo
from python_application.generated_code.enumerations.FileFormatType import FileFormatType


class Sample:
    """Represents a Sample object."""
    def __init__(self
, filename: str, extension: FileFormatType):
        """
        :param filename: filename of the Sample
        :param extension: extension of the Sample
        """
        self.filename = filename
        self.extension = extension
