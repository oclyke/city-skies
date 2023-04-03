from tests.fixtures import client
from tools.interface import Stack

def test_active_stack(client):
    assert type(client.stacks.active) == Stack

def test_stack_layers(client):
    assert type(client.stacks.active.layers) == list
