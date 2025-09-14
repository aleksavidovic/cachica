import pytest

from cachica.datastore import DataStore


@pytest.fixture
def datastore():
    return DataStore()


def test_empty_command(datastore):
    resp = datastore.process([])
    assert resp == b"-ERR empty command\r\n"


def test_ping(datastore):
    resp = datastore.process(["PING"])
    assert resp == b"+PONG\r\n"
