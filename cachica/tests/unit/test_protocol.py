import pytest
import cachica.protocol

def test_parse_ping_command():
    resp = parse_command(b"PING\r\n")
    assert resp == ("PING", [])
