"""
    Exceptions raised in dtype handling
"""


class DTypeException(Exception):
    """
    Base data type exception.
    """


class NotADType(DTypeException):
    """
    Not a Spotlight data type.
    """


class UnsupportedDType(DTypeException):
    """
    This data type is not supported.
    """


class InvalidFile(Exception):
    """
    File does not exist or is not readable for the respective data type.
    """
