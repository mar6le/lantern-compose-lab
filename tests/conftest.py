import pytest

from verify_lantern import load_target


@pytest.fixture(scope="session")
def lantern_target():
    return load_target()
