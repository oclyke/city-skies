import pytest

from tools.skies import CitySkiesClient

@pytest.fixture
def client():
    return CitySkiesClient("localhost", 1337)
