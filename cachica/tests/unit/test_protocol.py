from cachica.protocol import parse_command


def test_parse_ping_command():
    resp = parse_command(b"PING\r\n")
    assert resp == ("PING", [])

def test_parse_echo_command():
    resp = parse_command(b"ECHO\r\n")
    assert resp == ("ECHO", [])
