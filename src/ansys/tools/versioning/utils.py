"""A module containing various utilities."""
from typing import Iterable, Union

from ansys.tools.versioning.exceptions import VersionError, VersionSyntaxError


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
    version_list = [VersionNumber(num) for num in version_list]
    while len(version_list) < 3:
        version_list.append(VersionNumber(0))
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
        version_tuple = tuple(map(VersionNumber, version_string.split(".")))

        # Check version numbers are positive integers
        if not all(num >= VersionNumber(0) for num in version_tuple):
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
        if not all(
            (isinstance(num, int) and num >= 0)
            or (isinstance(num, str) and "dev" in num and len(num) <= 6)
            for num in version_tuple
        ):
            raise ValueError

    except ValueError:
        raise VersionSyntaxError(
            "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning "
            "or a string containing 'dev' and a number of characters less than 6."
        )

    version_string = ".".join(tuple(map(str, version_tuple)))
    return sanitize_version_string(version_string)


def server_meets_version(server_version, required_version):
    """Check if server meets the required version.

    Parameters
    ----------
    server_version : str, tuple, obj
        A string or tuple representing the server version.
        If it is an object different from the previous ones, it must have a '_server_version' attribute.

    required_version : str, tuple
        A string or tuple representing the version to be meet.

    Returns
    -------
    bool
        ``True`` if server version meets required version, ``False`` if not.

    Raises
    ------
    ValueError
        If the 'server_version' object does not have '_server_version' attribute.

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
    >>> class MyServer:
            def __init__(self):
                self._server_version = "1.2.0"
    >>> server = MyServer()
    >>> server_version, required_version = server, "1.3.0"
    >>> server_meets_version(server, required_version)

    """
    # If the 'server_version' object is not a string, let's check for
    # '_server_version' attribute
    if not isinstance(server_version, (str, tuple)):
        if hasattr(server_version, "_server_version"):
            server_version = server_version._server_version
        else:
            raise ValueError(
                "The 'server_version' object must be a string or have a '_server_version' attribute."
            )

    # Sanitize server and required version inputs
    server_version, required_version = [
        version_string_as_tuple(version)
        if isinstance(version, str)
        else sanitize_version_tuple(version)
        for version in [server_version, required_version]
    ]

    for ith_num, (server_version_number, required_version_number) in enumerate(
        zip(server_version, required_version), start=1
    ):

        # Keep comparing if both numbers are the same
        if server_version_number == required_version_number and ith_num != 3:
            continue

        # If all numbers are the same, server and required version are exactly
        # the same
        elif server_version_number == required_version_number and ith_num == 3:
            return True

        # If a server version number is higher, the iteration stops
        elif server_version_number > required_version_number:
            return True

        # If a version number is lower, stop the iteration
        elif server_version_number < required_version_number:
            return False


def requires_version(version, VERSION_MAP=None):
    """Ensure the method called matches a certain version.

    Parameters
    ----------
    version : str, tuple
        A string or tuple representing the minimum required version.
    VERSION_MAP : dict, optional
        A dictionary relating server version and ANSYS unified install version.

    Raises
    ------
    AttributeError
        Decorated class method requires ``_server_version`` attribute.
    VersionError
        Decorated class method is not supported by server version.

    """

    def decorator(func):

        # Sanitize input version
        min_version = (
            sanitize_version_tuple(version)
            if isinstance(version, tuple)
            else version_string_as_tuple(version)
        )

        def wrapper(self, *args, **kwargs):
            """Call the original function."""
            # Check that the object has a '_server_version' attribute
            if not hasattr(self, "_server_version"):
                raise AttributeError(
                    "Decorated class method must have ``_server_version`` attribute."
                )

            # Raise exceptions if server version is not valid
            if not server_meets_version(self._server_version, min_version):

                # Provide a generic version error message
                if not VERSION_MAP:
                    raise VersionError(
                        f"Class method ``{func.__name__}`` requires server version >= {version_tuple_as_string(min_version)}."
                    )

                # Provide a better error message if VERSION_MAP is provided
                raise VersionError(
                    f"Class method ``{func.__name__}`` requires server version >= {VERSION_MAP[min_version]}."
                )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class VersionNumber:
    """Class for version comparison.

    This class can be instantiated from a string or an integer.
    The constructor will choose the corresponding class.

    Any combination of 'dev' and integers will be considered as a string.
    'dev' is considered as the highest version number possible.

    Examples
    --------
    >>> from ansys.tools.versioning.utils import VersionNumber
    >>> VersionNumber(1)
    1
    >>> VersionNumber("dev")
    'dev'
    >>> VersionNumber(1) <= VersionNumber("dev")
    True
    >>> VersionNumber(99999) >= VersionNumber("dev")
    False
    >>> VersionNumber("dev") == VersionNumber("dev1")
    False
    >>> VersionNumber("dev") != VersionNumber("dev1")
    True
    """

    def __new__(cls, value: Union[str, int]) -> Union[str, int]:
        """Create and return a new object.

        Args:
            value (str or int):

        Returns:
            str, int: Returns a subclass of str or int depending on value.
        """
        if isinstance(value, str):
            if value.strip().isdigit():
                return myint.__new__(myint, int(value.strip()))
            else:
                if valid_version_string(value):
                    return mystr.__new__(mystr, value)
                else:
                    raise ValueError(
                        "This version is not allowed. Only 'dev' is allowed with any combination numbers."
                    )
        elif isinstance(value, int):
            return myint.__new__(myint, value)


class VersionMeta:
    """Metaclass for version comparison.

    Implements modification to magic methods.
    """

    def __le__(self, __x: Union[str, int]) -> bool:
        """Less equal.

        If compared against a string which contains 'dev' it will always evaluate to True.
        If compared against an int, it will perform a classic 'less equal' operation.
        """
        if isinstance(__x, str):
            if "dev" in __x and isinstance(self, str) and "dev" in self:
                raise ValueError("Two 'dev' versions cannot be compared against.")
            elif "dev" in __x:
                return True
            else:
                raise ValueError("Invalid version string")
        else:
            return super().__le__(__x)

    def __lt__(self, __x: Union[str, int]) -> bool:
        """Less than.

        If compared against a string which contains 'dev' it will always evaluate to True.
        If compared against an int, it will perform a classic 'less than' operation.
        """
        if isinstance(__x, str):
            if "dev" in __x and isinstance(self, str) and "dev" in self:
                raise ValueError("Two 'dev' versions cannot be compared against.")
            elif "dev" in __x:
                return True
            else:
                raise ValueError("Invalid version string")
        else:
            return super().__lt__(__x)

    def __ge__(self, __x: Union[str, int]) -> bool:
        """Greater equal.

        If compared against a string which contains 'dev' it will always evaluate to False.
        If compared against an int, it will perform a classic 'greater equal' operation.
        """
        if isinstance(__x, str):
            if "dev" in __x and isinstance(self, str) and "dev" in self:
                raise ValueError("Two 'dev' versions cannot be compared against.")
            elif "dev" in __x:
                return False
            else:
                raise ValueError("Invalid version string")
        else:
            return super().__ge__(__x)

    def __gt__(self, __x: Union[str, int]) -> bool:
        """Greater than.

        If compared against a string which contains 'dev' it will always evaluate to False.
        If compared against an int, it will perform a classic 'greater than' operation.
        """
        if isinstance(__x, str):
            if "dev" in __x and isinstance(self, str) and "dev" in self:
                raise ValueError("Two 'dev' versions cannot be compared against.")
            elif "dev" in __x:
                return False
            else:
                raise ValueError("Invalid version string")
        else:
            return super().__gt__(__x)

    def __eq__(self, __x: object) -> bool:
        """Equal method.

        If compared against a string which contains 'dev' it will always evaluate to False.
        If compared against an int, it will perform a classic 'equal' operation.
        """
        if isinstance(self, str) and isinstance(__x, str) and "dev" in self and "dev" in __x:
            return str(self) == str(__x)

        elif isinstance(__x, str):
            return False
        else:
            return super().__eq__(__x)

    def __ne__(self, __x: object) -> bool:
        """Not equal.

        If compared against a string which contains 'dev' it will always evaluate to not
        'equal' operation (True). If compared against an int, it will perform a classic 'not equal' operation.
        """
        if isinstance(__x, str):
            return not self.__eq__(__x)
        else:
            return super().__ne__(__x)

    def __hash__(self) -> int:
        """Call the underlying __hash__ method."""
        return super().__hash__()


def valid_version_string(version):
    """Check if version string is valid."""
    if isinstance(version, str) and (
        version.lower().replace("dev", "").replace(".", "").isdigit() or version.lower() == "dev"
    ):
        return True
    elif isinstance(version, int):
        return True
    else:
        return False


def valid_semantic_version(iterable):
    """Check if a semantic version is valid."""
    valid_major_minor = all(
        isinstance(each, int) or (isinstance(each, str) and each.isdigit()) for each in iterable[:2]
    )
    valid_patch = valid_version_string(iterable[2])

    if valid_major_minor and valid_patch:
        return True
    else:
        return False


class SemanticVersion(tuple):
    """
    Class for semantic versioning.

    It is a subclass of tuple and can be instantiated from a string or a tuple.

    You can use 'dev' in the patch version, but nowhere else.

    Parameters
    ----------
    tuple : _type_
        _description_
    """

    def __new__(cls: type, __iterable: Iterable = None, major=None, minor=None, patch=None):
        """Construct class.

        Parameters
        ----------
        cls : type
            Class type
        __iterable : Iterable[str, int], optional
            Iterable with major, minor and patch numbers as str or int, by default None
        major : _type_, optional
            Major version digit, by default None
        minor : _type_, optional
            Minor version digit, by default None
        patch : _type_, optional
            Patch version digit, by default None

        Returns
        -------
        myint, mystr
            Depending on the input, the output will be a myint or a mystr class.

        """
        if __iterable is None:
            if major and minor and patch:
                __iterable = (major, minor, patch)
            else:
                raise ValueError("Semantic version must have 3 components (major, minor, patch)")

        if isinstance(__iterable, str):
            if not valid_version_string(__iterable):
                raise ValueError(
                    "Semantic version not allow characters other than numbers, 'dev' and dots"
                )
            __iterable = __iterable.split(".")

        if len(__iterable) != 3:
            raise ValueError("Semantic version must have 3 components (major, minor, patch)")

        if not valid_semantic_version(__iterable):
            raise ValueError(
                "Semantic version format is incorrect. Only integers are allowed, and for patch also a string containing 'dev' is allowed"
            )

        __iterable = tuple(VersionNumber(i) for i in __iterable)
        return super().__new__(cls, __iterable)

    @property
    def major(self):
        """Return major version number"""
        return self[0]

    @property
    def minor(self):
        """Return minor version number"""
        return self[1]

    @property
    def patch(self):
        """Return patch version number"""
        return self[2]

    def as_string(self):
        """Return the version as string"""
        return ".".join(str(i) for i in self)

    def as_tuple(self):
        """Return the version as tuple"""
        return tuple(self)

    def as_list(self):
        """Return the version as list"""
        return list(self)

    def as_dict(self):
        """Return the version as dict"""
        return {"major": self.major, "minor": self.minor, "patch": self.patch}


class mystr(VersionMeta, str):
    """Custom class to hold strings for versioning"""
    pass


class myint(VersionMeta, int):
    """Custom class to hold integers for versioning"""
    pass
