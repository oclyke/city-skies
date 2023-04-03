from tests.fixtures import client

def test_global_variables(client):
    vars = client.global_variables

    # ensure proper type
    assert type(vars == dict)

    # ensure expected keys
    for key in ("brightness", "palette"):
        assert key in vars.keys()

def test_global_variable_set(client):
    for value in ["0.1", "0.9"]:
        client.global_variables["brightness"].value = value
        assert client.global_variables["brightness"].value == value
