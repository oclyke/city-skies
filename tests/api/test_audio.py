from tests.fixtures import client
from tools.interface import Audio, AudioSource

def test_audio_type(client):
    assert type(client.audio) == Audio

def test_audio_info(client):
    info = client.audio.info
    assert type(info) == dict
    assert "selected" in info.keys()

def test_audio_sources(client):
    assert type(client.audio.sources) == list

def test_audio_select_source(client):
    client.audio.select_source("NULL")
    assert client.audio.info["selected"] == None

def test_audio_get_source(client):
    source = client.audio.get_source("NULL")
    assert type(source) == AudioSource
    assert type(source.variables) == dict
    assert type(source.private_variables) == dict

def test_audio_source_variables(client):
    source = client.audio.get_source("NULL")
    for name, variable in source.variables.items():
        source.set_variable(name, variable.value)

def test_audio_source_private_variables(client):
    source = client.audio.get_source("NULL")
    for name, variable in source.private_variables.items():
        source.set_private_variable(name, variable.value)
