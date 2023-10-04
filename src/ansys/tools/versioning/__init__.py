"""
PyAnsys Tools Versioning.

Utilities for backwards and forwards server support.
"""
import importlib.metadata as importlib_metadata

from ansys.tools.versioning.utils import requires_version, server_meets_version

__version__ = importlib_metadata.version("pyansys-tools-versioning")
__all__ = ["requires_version", "server_meets_version"]
