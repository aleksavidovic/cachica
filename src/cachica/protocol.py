import collections
import logging
import pdb
from asyncio import StreamReader
from collections import deque

logger = logging.getLogger(__name__)
RESP_DELIMITER = b"\r\n"
SUPPORTED_RESP_COMMANDS = (
    "SET",
    "GET",
    "PING",
    "ECHO",
)  # I will expand the list once I implement these

HAS_SECOND_WORD = ("CLIENT",)  # A list of first word of two-word commands
# so i can parse one more if match is found
# This is just a placeholder for an idea,
# I might take a different approach


class BadRequest(Exception):
    pass


class UnknownCommandCode(Exception):
    pass


async def parse_request_from_stream_reader(reader: StreamReader) -> deque | None:
    header = await reader.readline()
    logger.debug(f"header: {header}")
    req_type = header[0]
    pdb.set_trace()
    if req_type is None:
        return None
    if req_type != 42:  # 42 is ascii for *
        raise BadRequest("Commands must start with b'*'")
    arr_len = int(header[1:-2])
    command_dq = deque(maxlen=arr_len)

    command_desc = await reader.readline()
    if command_desc[0] != 36:  # 36 is ascii for $
        raise BadRequest("Command name must be a bulk string ($)")
    command_strlen = int(command_desc[1:-2])
    command_bytes = await reader.readexactly(command_strlen + 2)  # +2 for CRLF
    command_name = command_bytes[:-2].decode("ascii").upper()
    if (
        len(command_name) != command_strlen
    ) or command_name not in SUPPORTED_RESP_COMMANDS:
        raise BadRequest(f"Invalid command: {command_name}")
    command_dq.append(command_name)
    match command_name:
        case "SET":
            return await parse_resp_set(reader, command_dq)
        case "PING":
            return await parse_resp_ping(reader, command_dq)
        case _:
            raise BadRequest(f"No match for command `{command_name}`.")


async def parse_resp_set(reader: StreamReader, command_dq: collections.deque):
    command_dq.extend(("dummy_key", "dummy_value"))
    return command_dq


async def parse_resp_ping(reader: StreamReader, command_dq):
    command_dq.append("dummy text")
    return command_dq
