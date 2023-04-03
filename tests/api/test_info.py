from tests.fixtures import client

def test_info(client):
    info = client.info
    assert type(info["hw_version"] == str)
    assert type(info["api_version"] == str)
