"""A module containing custom exceptions."""


class VersionSyntaxError(Exception):
    """An exception to be raised when an invalid version syntaxt is found."""

    def __init__(self, msg):
        """Initialize the exception.

        Parameters
        ----------
        msg : str
            The message to be raised for the exception.

        """
        super().__init__(msg)


class VersionError(Exception):
    """An exception to be raised when a version is not valid."""

    def __init__(self, msg):
        """Initialize the exception.

        Parameters
        ----------
        msg : str
            The message to be raised for the exception.

        """
        super().__init__(msg)
