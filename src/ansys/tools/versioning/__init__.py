"""
PyAnsys Tools Versioning.

Utilities for backwards and forwards server support.
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

from ansys.tools.versioning.utils import requires_version

__version__ = importlib_metadata.version("pyansys-tools-versioning")
__all__ = ["requires_version"]
