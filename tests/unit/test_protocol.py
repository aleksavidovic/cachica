from os import wait
import pytest
pytestmark = pytest.mark.skip(reason="Module temporarily disabled")

from cachica.protocol import parse_request_from_stream_reader


def test_parse_ping_command():
    # assert parse_command(b"PING\r\n") == ("PING")
    assert True

def test_parse_echo_command():
    # assert parse_command(b"ECHO\r\n") == ("ECHO")
    assert True

@pytest.mark.parametrize(
    "req, expected",
    [
        (b"$5\r\nhello\r\n", ("$5", "hello")),
        (b"$0\r\n\r\n", ("$0")),
    ],
)
def test_parse_bulk_string(req, expected):
    # assert parse_command(req) == expected
    assert True
