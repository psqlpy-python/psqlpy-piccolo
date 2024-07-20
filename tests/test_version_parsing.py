import pytest

from psqlpy_piccolo import PSQLPyEngine


@pytest.mark.parametrize(
    (
        "version_to_parse",
        "expected_result",
    ),
    [("9.4", 9.4), ("9.4.1", 9.4), ("12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)", 12.4)],
)
def test_version_parsing(version_to_parse: str, expected_result: float) -> None:
    assert (
        PSQLPyEngine._parse_raw_version_string(
            version_string=version_to_parse,
        )
        == expected_result
    )
