import pytest

from cachica.protocol import parse_command


def test_parse_ping_command():
    assert parse_command(b"PING\r\n") == ("PING")


def test_parse_echo_command():
    assert parse_command(b"ECHO\r\n") == ("ECHO")


@pytest.mark.parametrize(
    "req, expected",
    [
        (b"$5\r\nhello\r\n", ("$5", "hello")),
        (b"$0\r\n\r\n", ("$0")),
    ],
)
def test_parse_bulk_string(req, expected):
    """
    Bulk strings

    A bulk string represents a single binary string.
    The string can be of any size, but by default,
    Redis limits it to 512 MB
    (see the proto-max-bulk-len configuration directive).

    RESP encodes bulk strings in the following way:

    $<length>\r\n<data>\r\n

        The dollar sign ($) as the first byte.
        One or more decimal digits (0..9) as the string's length,
        in bytes, as an unsigned, base-10 value.
        The CRLF terminator.
        The data.
        A final CRLF.

    So the string "hello" is encoded as follows:
    $5\r\nhello\r\n
    The empty string's encoding is:
    $0\r\n\r\n
    """
    assert parse_command(req) == expected
