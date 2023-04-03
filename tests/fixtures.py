import pytest

from tools.interface import CitySkiesClient

@pytest.fixture
def client():
    return CitySkiesClient("localhost", 1337)
