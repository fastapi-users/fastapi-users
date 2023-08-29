def test_global_fixture(dummy_fixture: int) -> None:
    expected_fixture_val = 2
    assert dummy_fixture == expected_fixture_val
