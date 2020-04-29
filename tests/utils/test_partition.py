import pytest

from web.utils import partition


@pytest.mark.parametrize(
    "mapping, key, expected",
    [
        (
            {1: "a", 2: "b", 3: None},
            lambda v: v is not None,
            ({1: "a", 2: "b"}, {3: None}),
        ),
    ],
)
def test_partition(mapping, key, expected):
    assert partition(mapping, key=key) == expected


def test_partition_with_bad_key():
    d = {1: "foo"}

    with pytest.raises(ValueError):
        partition(d)
