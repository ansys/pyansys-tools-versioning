from hypothesis import given
import hypothesis.strategies as st
import pytest

from ansys.tools.versioning.exceptions import VersionSyntaxError
from ansys.tools.versioning.utils import (
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
        "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning."
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
