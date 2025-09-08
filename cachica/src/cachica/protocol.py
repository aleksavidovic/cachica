from typing import List

def parse_command(req: bytes) -> tuple[str, List]:
    print(req)
    return "PING", []
