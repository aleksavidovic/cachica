import pytest

from cachica import protocol
from cachica.protocol import Parser


@pytest.fixture
def parser():
    return Parser()


def test_parse_ping_command(parser):
    parser.feed(b"*1\r\n$4\r\nPING\r\n")
    assert parser.get_command() == ["PING"]


@pytest.mark.parametrize(
    "req, expected",
    [(b"*1\r\n$4\r\nECHO\r\n", ["ECHO"]), (b"*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n", ["ECHO", "hello"])],
)
def test_parse_echo_command(parser, req, expected):
    parser.feed(req)
    assert parser.get_command() == expected


@pytest.mark.parametrize(
    "req, expected",
    [
        (b"*3\r\n$3\r\nSET\r\n$4\r\nname\r\n$6\r\naleksa\r\n", ["SET", "name", "aleksa"]),
        (b"*3\r\n$3\r\nSET\r\n$8\r\nusername\r\n$8\r\nfleksicc\r\n", ["SET", "username", "fleksicc"]),
    ],
)
def test_parse_set(parser, req, expected):
    parser.feed(req)
    assert parser.get_command() == expected


@pytest.mark.parametrize("string, encoded", [("PONG", b"+PONG\r\n"), ("OK", b"+OK\r\n")])
def test_encode_simple_string(string, encoded):
    res = protocol.encode_simple_string(string)
    assert res == encoded


@pytest.mark.parametrize(
    "error_message, error_prefix, expected",
    [
        (
            "wrong number of arguments for 'echo' command",
            "ERR",
            b"-ERR wrong number of arguments for 'echo' command\r\n",
        ),
    ],
)
def test_encode_simple_error_with_provided_prefix(error_message, error_prefix, expected):
    error_response = protocol.encode_simple_error(error_message, error_prefix=error_prefix)
    assert error_response == expected


def test_encode_bulk_string():
    bulk_string = "hello world"
    res = protocol.encode_bulk_string(bulk_string)
    assert res == b"$11\r\nhello world\r\n"
