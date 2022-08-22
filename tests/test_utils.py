from hypothesis import given
import hypothesis.strategies as st
import pytest

from ansys.helpers.versioning.exceptions import VersionSyntaxError
from ansys.helpers.versioning.utils import (
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
    expected_version_tuple = sanitize_version_tuple(tuple(version_numbers))
    assert (
        version_string_as_tuple(version_tuple_as_string(expected_version_tuple))
        == expected_version_tuple
    )


@given(st_non_valid_version_integers)
def test_version_tuple_as_strig_syntax_error(version_numbers):
    expected_version_tuple = sanitize_version_tuple(tuple(version_numbers))
    with pytest.raises(VersionSyntaxError) as excinfo:
        version_tuple_as_string(expected_version_tuple)
    assert (
        "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning."
        in excinfo.exconly()
    )


@given(st_version_integers)
def test_version_string_as_tuple(version_numbers):
    expected_version_string = sanitize_version_string(".".join(tuple(map(str, version_numbers))))
    assert (
        version_tuple_as_string(version_string_as_tuple(expected_version_string))
        == expected_version_string
    )


@given(st_non_valid_version_integers)
def test_version_string_as_tuple_syntax_error(version_numbers):
    expected_version_string = sanitize_version_string(".".join(tuple(map(str, version_numbers))))
    with pytest.raises(VersionSyntaxError) as excinfo:
        version_string_as_tuple(expected_version_string)
    assert (
        "Version string can only contain positive integers following <MAJOR>.<MINOR>.<PATCH> versioning."
        in excinfo.exconly()
    )


@given(st_version_pairs)
def test_server_meets_version(version_pairs):
    server_version, required_version = list(map(sanitize_version_tuple, map(tuple, version_pairs)))

    meets_version = True
    for server_version_number, required_version_number in zip(server_version, required_version):
        if server_version_number < required_version_number:
            meets_version = False
            break

    assert meets_version == server_meets_version(server_version, required_version)
