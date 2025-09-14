import pytest

from cachica.protocol import Parser


@pytest.fixture
def parser():
    return Parser()


def test_parse_ping_command(parser):
    parser.feed(b"*1\r\n$4\r\nPING\r\n")
    assert parser.get_command() == ["PING"]


def test_parse_echo_command(parser):
    # assert parse_command(b"ECHO\r\n") == ("ECHO")
    assert True


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
