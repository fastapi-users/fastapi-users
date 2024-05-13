from filuta_fastapi_users import __version__


def test_import() -> None:
    """Test that package is installed."""


def test_version() -> None:
    assert __version__ == "12.1.1+2"


def test_global_fixture(dummy_fixture: int) -> None:
    expected_fixture_val = 2
    assert dummy_fixture == expected_fixture_val
