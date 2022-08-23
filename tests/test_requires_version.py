import pytest

from ansys.helpers.versioning.exceptions import VersionError


def test_not_implemented_server_version_attribute(server_without_server_version_attribute):
    with pytest.raises(AttributeError) as excinfo:
        server_without_server_version_attribute.foo()
    assert (
        "AttributeError: Decorated class method must have ``_server_version`` attribute."
        in excinfo.exconly()
    )


def test_server_meets_all_version_requirements(server_with_all_methods_available):
    server_with_all_methods_available.foo()
    server_with_all_methods_available.bar()


def test_server_outdated_method_and_version_map(server_with_outdated_foo_method):
    with pytest.raises(VersionError) as excinfo:
        server_with_outdated_foo_method.foo()
    assert (
        "VersionError: Class method ``foo`` requires server version >= 20XYRZ." in excinfo.exconly()
    )


def test_server_outdated_method_and_without_version_map(server_with_outdated_methods):
    with pytest.raises(VersionError) as excinfo:
        server_with_outdated_methods.bar()
    assert (
        "VersionError: Class method ``bar`` requires server version >= 0.1.0." in excinfo.exconly()
    )
