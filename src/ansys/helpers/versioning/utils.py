"""A module containing various utilities."""

from ansys.helpers.versioning.exceptions import VersionSyntaxError


def sanitize_version_string(version_string):
    """Sanitize a version string number by adding additional zeros.

    Parameters
    ----------
    version_string : str
        A string representing a semantic version.

    Returns
    -------
    str
        A string representing a semantic version.

    Examples
    --------
    >>> sanitize_version_string("0")
    '0.0.0'
    >>> sanitize_version_string("1.2")
    '1.2.0'
    >>> sanitize_version_string("0.3.4")
    '0.3.4'

    """
    version_list = version_string.split(".")
    while len(version_list) < 3:
        version_list.append("0")
    return ".".join(version_list)


def sanitize_version_tuple(version_tuple):
    """Sanitize a version number by adding additional zeros.

    Parameters
    ----------
    version_tuple : tuple
        A tuple representing a semantic version.

    Returns
    -------
    tuple
        A tuple representing a semantic version.

    Examples
    --------
    >>> sanitize_version_tuple((0,))
    (0, 0, 0)
    >>> sanitize_version_tuple((1, 2))
    (1, 2, 0)
    >>> sanitize_version_tuple((0, 3, 4))
    (0, 3, 4)

    """
    version_list = list(version_tuple)
    while len(version_list) < 3:
        version_list.append(0)
    return tuple(version_list)


def version_string_as_tuple(version_string):
    """Convert a semantic version string into a tuple.

    Parameters
    ----------
    version_string : str
        A string representing a semantic version.

    Returns
    -------
    version_tuple : tuple
        A tuple representing a semantic version.

    Examples
    --------
    >>> version_string_as_tuple("0.3.4")
    (0, 3, 4)
    >>> version_string_as_tuple("1.2")
    (1, 2, 0)


    """
    try:
        # Check version string numbers are numeric by converting to integers
        version_tuple = tuple(map(int, version_string.split(".")))

        # Check version numbers are positive integers
        if not all(num >= 0 for num in version_tuple):
            raise ValueError

    except ValueError:
        raise VersionSyntaxError(
            "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning."
        )

    return sanitize_version_tuple(version_tuple)


def version_tuple_as_string(version_tuple):
    """Convert a semantic version tuple into a string.

    Parameters
    ----------
    version_tuple : tuple
        A tuple representing a semantic version.

    Returns
    -------
    str
        A string representing a semantic version.

    Examples
    --------
    >>> version_tuple_as_string((0, 3, 4))
    '0.3.4'
    >>> version_tuple_as_string((1, 2))
    '1.2.0'

    """
    try:
        # Check version numbers are positive integers
        if not all(isinstance(num, int) and num >= 0 for num in version_tuple):
            raise ValueError

    except ValueError:
        raise VersionSyntaxError(
            "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning."
        )

    version_string = ".".join(tuple(map(str, version_tuple)))
    return sanitize_version_string(version_string)


def server_meets_version(server_version, required_version):
    """Check if server meets the required version.

    Parameters
    ----------
    server_version : str, tuple
        A string or tuple representing the server version.
    required_version : str, tuple
        A string or tuple representing the version to be meet.

    Returns
    -------
    bool
        ``True`` if server version meets required version, ``False`` if not.

    Examples
    --------
    >>> server_version, required_version = "1.2.0", "1.3.0"
    >>> server_meets_version(server_version, required_version)
    False
    >>> server_version, required_version = (1, 2, 0), (1, 3, 0)
    >>> server_meets_version(server_version, required_version)
    False
    >>> server_version, required_version = "2.3.0", "1.3.0"
    >>> server_meets_version(server_version, required_version)
    True
    >>> server_version, required_version = (2, 3, 0), (1, 3, 0)
    >>> server_meets_version(server_version, required_version)
    True
    >>> server_version, required_version = (0, 0, 0), (0, 0, 0)
    >>> server_meets_version(server_version, required_version)
    True

    """
    # Sanitize server and required version inputs
    servers_version, required_version = [
        version_string_as_tuple(version)
        if isinstance(version, str)
        else sanitize_version_tuple(version)
        for version in [server_version, required_version]
    ]

    # Compare both version numbers
    for server_version_number, required_version_number in zip(server_version, required_version):

        if server_version_number < required_version_number:
            return False

    return True
