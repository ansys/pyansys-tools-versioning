from hypothesis import given
import hypothesis.strategies as st
import pytest

from ansys.tools.versioning.exceptions import VersionSyntaxError
from ansys.tools.versioning.utils import (
    SemanticVersion,
    VersionNumber,
    sanitize_version_string,
    sanitize_version_tuple,
    server_meets_version,
    version_string_as_tuple,
    version_tuple_as_string,
)

st_version_integers = st.lists(st.integers(0, 100), min_size=1, max_size=3)
st_non_valid_version_integers = st.lists(st.integers(-100, -1), min_size=1, max_size=3)
st_version_pairs = st.lists(
    st.tuples(st.integers(0, 100), st.integers(0, 100), st.integers(0, 100)), min_size=2, max_size=2
)


@given(st_version_integers)
def test_version_tuple_as_string(version_numbers):
    """Test version as tuple properly converts to string type."""
    expected_version_tuple = sanitize_version_tuple(tuple(version_numbers))
    assert (
        version_string_as_tuple(version_tuple_as_string(expected_version_tuple))
        == expected_version_tuple
    )


@given(st_non_valid_version_integers)
def test_version_tuple_as_strig_syntax_error(version_numbers):
    """Test invalid version tuple properly raises version syntax error."""
    expected_version_tuple = sanitize_version_tuple(tuple(version_numbers))
    with pytest.raises(VersionSyntaxError) as excinfo:
        version_tuple_as_string(expected_version_tuple)
    assert (
        "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning"
        in excinfo.exconly()
    )


@given(st_version_integers)
def test_version_string_as_tuple(version_numbers):
    """Test version as string properly converts to tuple type."""
    expected_version_string = sanitize_version_string(".".join(tuple(map(str, version_numbers))))
    assert (
        version_tuple_as_string(version_string_as_tuple(expected_version_string))
        == expected_version_string
    )


@given(st_non_valid_version_integers)
def test_version_string_as_tuple_syntax_error(version_numbers):
    """Test invalid version string properly raises version syntax error."""
    expected_version_string = sanitize_version_string(".".join(tuple(map(str, version_numbers))))
    with pytest.raises(VersionSyntaxError) as excinfo:
        version_string_as_tuple(expected_version_string)
    assert (
        "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning."
        in excinfo.exconly()
    )


def test_equal_version_is_valid():
    assert server_meets_version("0.0.0", "0.0.0") == True


class MyServer:
    def __init__(self, version):
        self._server_version = version


@pytest.mark.parametrize(
    "server_version,required_version,result",
    [
        pytest.param(MyServer(version="1.4.0"), "1.2.0", True, id="Normal successful class case."),
        pytest.param(
            MyServer(version=(1, 4, 0)),
            "1.2.0",
            True,
            id="Normal successful class case with tuple.",
        ),
        pytest.param(
            MyServer(version=(1, 4, 0)), "1.6.0", False, id="Normal unsuccessful class case."
        ),
        pytest.param((1, 2, 0), "1.2.0", True, id="Normal successful case."),
        pytest.param((1, 2, 1), "1.2.0", True, id="Normal successful case with minor."),
        pytest.param((1, 2, 0), "1.2.1", False, id="Unsuccessful case tuple-str."),
        pytest.param("1.2.2", "1.2.1", True, id="Successful case str-str."),
        pytest.param("1.2.0", "1.2.1", False, id="Unsuccessful case str-str."),
        pytest.param("1. 2. 3", "1.2.1", True, id="Successful case str with spaces-str."),
    ],
)
def test_server_meets_version(server_version, required_version, result):
    assert server_meets_version(server_version, required_version) == result


def test_server_meets_version_error():
    class MyObj:
        pass

    with pytest.raises(ValueError):
        server_meets_version(MyObj(), "1.2.1")


def test_dev_version_patch():
    my_version = "0.0.dev1"
    assert server_meets_version(my_version, "0.0.0") == True
    assert server_meets_version(my_version, "0.0.1") == True
    assert server_meets_version(my_version, "0.0.999") == True

    assert server_meets_version(my_version, "0.2.0") == False
    assert server_meets_version(my_version, "0.2.9999") == False

    assert server_meets_version(my_version, "3.1.0") == False
    assert server_meets_version(my_version, "3.1.9999") == False


def test_dev_version_minor():
    my_version = "0.dev.1"
    with pytest.raises(VersionSyntaxError):
        server_meets_version(my_version, "0.0.0")


def test_dev_version_major():
    my_version = "dev.1.1"
    with pytest.raises(VersionSyntaxError):
        assert server_meets_version(my_version, "0.0.0")


def test_version():
    assert VersionNumber(1) < VersionNumber("dev")
    assert VersionNumber(999999) < VersionNumber("dev")
    assert VersionNumber("dev") > VersionNumber("999999")

    assert VersionNumber(1) <= VersionNumber("dev")
    assert VersionNumber(999999) <= VersionNumber("dev")
    assert VersionNumber("dev") >= VersionNumber("999999")

    assert VersionNumber(1) != VersionNumber("dev")
    assert not (VersionNumber(1) == VersionNumber("dev"))

    # changing order
    assert VersionNumber("dev") > VersionNumber(1)
    assert VersionNumber("dev") > VersionNumber(999999)
    assert VersionNumber("999999") < VersionNumber("dev")

    assert VersionNumber("dev") >= VersionNumber(1)
    assert VersionNumber("dev") >= VersionNumber(999999)
    assert VersionNumber("999999") <= VersionNumber("dev")

    assert VersionNumber("dev") != VersionNumber(1)
    assert not (VersionNumber("dev") == VersionNumber(1))

    with pytest.raises(ValueError):
        assert VersionNumber("dev") > VersionNumber("-1")

    with pytest.raises(ValueError):
        assert VersionNumber("deva")


def test_semantic_version_definition():
    assert SemanticVersion((1, 2, 3))
    assert SemanticVersion(("1", "2", "dev"))
    assert SemanticVersion((1, "2", "dev"))

    assert SemanticVersion(major=1, minor=2, patch=3)
    assert SemanticVersion(major="1", minor="2", patch="3")
    assert SemanticVersion(major=1, minor="2", patch="dev")
    assert SemanticVersion(major=1, minor="2", patch="dev01")

    assert SemanticVersion("1.1.dev")
    assert SemanticVersion("1.1.dev1")

    with pytest.raises(VersionSyntaxError):
        SemanticVersion((1, 2))

    with pytest.raises(VersionSyntaxError):
        SemanticVersion(major=1, minor=2)

    with pytest.raises(VersionSyntaxError):
        SemanticVersion(major=1, minor=2, patch="dev.a")

    with pytest.raises(VersionSyntaxError):
        SemanticVersion(major=1, minor="dev", patch="dev1")

    with pytest.raises(VersionSyntaxError):
        SemanticVersion("1.1.deva")

    with pytest.raises(VersionSyntaxError):
        SemanticVersion("1.1")


def test_semantic_version_methods():
    ver = SemanticVersion("1.1.dev1")
    assert ver.major == 1
    assert ver.minor == 1
    assert ver.patch == "dev1"

    assert ver.as_string() == "1.1.dev1"
    assert ver.as_tuple() == (1, 1, "dev1")
    assert ver.as_dict() == {"major": 1, "minor": 1, "patch": "dev1"}
    assert ver.as_list() == [1, 1, "dev1"]


def test_semantic_version_comparison():
    assert SemanticVersion("1.1.1") < SemanticVersion((1, 1, 2))
    assert SemanticVersion("1.1.1") > SemanticVersion((1, 1, 0))

    assert SemanticVersion("1.1.1") <= SemanticVersion((1, 1, 2))
    assert SemanticVersion("1.1.1") >= SemanticVersion((1, 1, 0))

    assert SemanticVersion("1.1.1") <= SemanticVersion((1, 1, 1))
    assert SemanticVersion("1.1.1") >= SemanticVersion((1, 1, 1))

    assert SemanticVersion("1.1.2") == SemanticVersion((1, 1, 2))
    assert SemanticVersion("1.1.2") != SemanticVersion((1, 1, 3))

    # checking major minors
    assert SemanticVersion("1.1.1") < SemanticVersion((1, 2, 1))
    assert SemanticVersion("1.1.1") > SemanticVersion((1, 0, 1))

    assert SemanticVersion("1.1.1") < SemanticVersion((2, 1, 1))
    assert SemanticVersion("1.1.1") > SemanticVersion((0, 1, 1))


def test_semantic_version_comparison_dev():
    assert SemanticVersion("1.1.1") < SemanticVersion((1, 1, "dev"))
    assert SemanticVersion("1.1.1") < SemanticVersion((1, 1, "dev1"))
    assert SemanticVersion((1, 1, "dev")) > SemanticVersion("1.1.1")
    assert SemanticVersion((1, 1, "dev1")) > SemanticVersion("1.1.1")

    assert SemanticVersion("1.1.dev1") == SemanticVersion((1, 1, "dev1"))
    assert SemanticVersion("1.1.dev1") != SemanticVersion((1, 1, "dev0"))

    assert SemanticVersion((1, 1, "dev1")) == SemanticVersion("1.1.dev1")
    assert SemanticVersion((1, 1, "dev0")) != SemanticVersion("1.1.dev1")

    # checking major minors
    assert SemanticVersion((1, 2, "dev")) > SemanticVersion("1.1.1")
    assert SemanticVersion((1, 0, "dev1")) < SemanticVersion("1.1.1")

    with pytest.raises(ValueError, match="'dev' versions cannot be compared"):
        SemanticVersion("1.1.dev") < SemanticVersion((1, 1, "dev1"))

    with pytest.raises(ValueError, match="'dev' versions cannot be compared"):
        SemanticVersion("1.1.dev") > SemanticVersion((1, 1, "dev1"))

    with pytest.raises(ValueError, match="'dev' versions cannot be compared"):
        SemanticVersion("1.1.dev") <= SemanticVersion((1, 1, "dev1"))

    with pytest.raises(ValueError, match="'dev' versions cannot be compared"):
        SemanticVersion("1.1.dev") >= SemanticVersion((1, 1, "dev1"))
