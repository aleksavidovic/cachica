from cachica.protocol import parse_command


def test_parse_ping_command():
    resp = parse_command(b"PING\r\n")
    assert resp == ("PING", [])
