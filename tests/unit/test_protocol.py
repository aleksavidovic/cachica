from cachica.protocol import parse_command


def test_parse_ping_command():
    resp = parse_command(b"PING\r\n")
    assert resp == ("PING", [])


def test_parse_echo_command():
    resp = parse_command(b"ECHO\r\n")
    assert resp == ("ECHO", [])


def test_parse_bulk_string():
    """
        Bulk strings

        A bulk string represents a single binary string. 
        The string can be of any size, but by default, 
        Redis limits it to 512 MB 
        (see the proto-max-bulk-len configuration directive).

        RESP encodes bulk strings in the following way:

        $<length>\r\n<data>\r\n

            The dollar sign ($) as the first byte.
            One or more decimal digits (0..9) as the string's length, in bytes, as an unsigned, base-10 value.
            The CRLF terminator.
            The data.
            A final CRLF.

        So the string "hello" is encoded as follows:
        $5\r\nhello\r\n
        The empty string's encoding is:
        $0\r\n\r\n
    """
    resp = parse_command(b"$5\r\nhello\r\n")
    assert resp == (None, ["hello"])
