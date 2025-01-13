# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from ansys.tools.versioning.exceptions import VersionError


def test_not_implemented_server_version_attribute(server_without_server_version_attribute):
    """Test if server instance has a ``_server_version`` attribute."""
    with pytest.raises(AttributeError) as excinfo:
        server_without_server_version_attribute.foo()
    assert (
        "AttributeError: Decorated class method must have ``_server_version`` attribute."
        in excinfo.exconly()
    )


def test_server_meets_all_version_requirements(server_with_all_methods_available):
    """Test no raised exceptions for a server instance matching all version requirements."""
    server_with_all_methods_available.foo()
    server_with_all_methods_available.bar()


def test_server_outdated_method_and_version_map(server_with_outdated_foo_method):
    """Test server partially outdated version with ``VERSION_MAP`` variable."""
    with pytest.raises(VersionError) as excinfo:
        server_with_outdated_foo_method.foo()
    assert (
        "VersionError: Class method ``foo`` requires server version >= 20XYRZ." in excinfo.exconly()
    )


def test_server_outdated_method_and_without_version_map(server_with_outdated_methods):
    """Test server outdated version without ``VERSION_MAP`` variable."""
    with pytest.raises(VersionError) as excinfo:
        server_with_outdated_methods.bar()
    assert (
        "VersionError: Class method ``bar`` requires server version >= 0.1.0." in excinfo.exconly()
    )
