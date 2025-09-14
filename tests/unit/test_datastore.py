import pytest

from cachica.datastore import DataStore


@pytest.fixture
def datastore():
    return DataStore()


@pytest.fixture
def populated_datastore_factory():
    def _create_datastore(initial_data: dict[str, str]):
        ds = DataStore()
        for key, value in initial_data.items():
            ds._set(key, value)
        return ds

    return _create_datastore


def test_empty_command_returns_error(datastore):
    resp = datastore.process([])
    assert resp == b"-ERR empty command\r\n"


def test_unknown_command_returns_error(datastore):
    command = ["BEL", "key"]
    resp = datastore.process(command)
    assert resp == b"-ERR unknown command 'BEL'\r\n"


@pytest.mark.parametrize(
    "command, expected",
    [
        (["PING"], b"+PONG\r\n"),
        (["PING", "hola"], b"$4\r\nhola\r\n"),
        (["ECHO", "message"], b"$7\r\nmessage\r\n"),
    ],
)
def test_valid_simple_commands(datastore, command, expected):
    assert datastore.process(command) == expected


def test_ping_too_many_args_returns_error(datastore):
    command = ["PING", "hello", "there"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'ping' command\r\n"


def test_echo_no_args_returns_error(datastore):
    command = ["ECHO"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'echo' command\r\n"


def test_echo_too_many_args_returns_error(datastore):
    command = ["ECHO", "hello", "there"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'echo' command\r\n"


def test_valid_set(datastore):
    command = ["SET", "name", "cachica"]
    assert datastore.process(command) == b"+OK\r\n"


def test_set_no_args_returns_error(datastore):
    command = ["SET"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'set' command\r\n"


def test_set_too_few_args_returns_error(datastore):
    command = ["SET", "name"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'set' command\r\n"


def test_set_too_many_args_returns_error(datastore):
    command = ["SET", "name", "cachica", "server"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'set' command\r\n"


def test_valid_get(populated_datastore_factory):
    command = ["GET", "name"]
    datastore = populated_datastore_factory({"name": "cachica"})
    resp = datastore.process(command)
    assert resp == b"$7\r\ncachica\r\n"


def test_get_key_not_found(populated_datastore_factory):
    command = ["GET", "name"]
    datastore = populated_datastore_factory({"app": "cachica"})
    resp = datastore.process(command)
    assert resp == b"-1\r\n"


def test_get_no_args_returns_error(datastore):
    command = ["GET"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'get' command\r\n"


def test_get_too_many_args_returns_error(datastore):
    command = ["GET", "name", "cachica"]
    assert datastore.process(command) == b"-ERR wrong number of arguments for 'get' command\r\n"


def test_valid_del_one_key(populated_datastore_factory):
    command = ["DEL", "app"]
    datastore = populated_datastore_factory({"app": "redis"})
    resp = datastore.process(command)
    assert resp == b":1\r\n"


def test_valid_del_key_no_match_ignores(populated_datastore_factory):
    command = ["DEL", "app", "name"]
    datastore = populated_datastore_factory({"app": "redis", "fruit": "banana"})
    resp = datastore.process(command)
    assert resp == b":1\r\n"


def test_valid_del_no_keys_match_returns_zero(populated_datastore_factory):
    command = ["DEL", "vegetable", "name"]
    datastore = populated_datastore_factory({"app": "redis", "fruit": "banana"})
    resp = datastore.process(command)
    assert resp == b":0\r\n"


def test_del_no_args_returns_error(datastore):
    command = ["DEL"]
    resp = datastore.process(command)
    assert resp == b"-ERR wrong number of arguments for 'del' command\r\n"
