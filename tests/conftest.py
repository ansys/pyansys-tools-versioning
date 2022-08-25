from copy import deepcopy

import pytest

from ansys.tools.versioning import requires_version

VERSION_MAP = {
    (0, 2, 1): "20XYRZ",
}
"""A dictionary relating server version and their unified install versions."""


class MockupServer:
    """A testing class for modelling servers."""

    def __init__(self, server_version):
        """Initialize a server instance being known its version."""
        self._server_version = server_version

    @requires_version("0.2.1", VERSION_MAP)
    def foo(self):
        """Calls ``foo`` method in the server side."""
        pass

    @requires_version((0, 1, 0))
    def bar(self):
        """Calls ``bar`` method in the server side."""
        pass


@pytest.fixture
def server_with_all_methods_available():
    return MockupServer(server_version="1.0.0")


@pytest.fixture
def server_without_server_version_attribute(server_with_all_methods_available):
    broken_server = deepcopy(server_with_all_methods_available)
    delattr(broken_server, "_server_version")
    return broken_server


@pytest.fixture
def server_with_outdated_foo_method():
    return MockupServer(server_version="0.2.0")


@pytest.fixture
def server_with_outdated_methods():
    return MockupServer(server_version=(0, 0, 1))
