import logging
from collections import deque

CRLF = b"\r\n"  # Standard RESP terminator
CRLF_LEN = 2


class ProtocolError(Exception):
    pass


class Parser:
    """A synchronous, stateful RESP parser."""

    def __init__(self, is_client=False) -> None:
        self._is_client = is_client
        self._buffer = bytearray()
        self._commands = deque()
        self._try_parse = self._try_parse_client if self._is_client else self._try_parse_server

    def feed(self, data: bytes) -> None:
        """Adds raw network data to the internal buffer."""
        self._buffer.extend(data)
        self._try_parse()

    def get_command(self) -> list[str] | None:
        """Returns a fully parsed command, or None if none are ready."""
        if self._commands:
            return self._commands.popleft()
        return None

    def _try_parse_client(self):
        while True:
            if not self._buffer:
                break

            # Find the position of the first delimiter
            first_crlf_pos = self._buffer.find(CRLF)
            if first_crlf_pos == -1:
                break

            first_byte = self._buffer[0:1]
            match bytes(first_byte):
                case b"*":
                    command, consumed_bytes = self._parse_array(self._buffer)
                    if command is None:
                        break
                    self._commands.append(command)
                    self._buffer = self._buffer[consumed_bytes:]
                case b"$":  # Bulk string
                    parsed_bulk_string, consumed_bytes = self._parse_bulk_string(self._buffer)
                    if parsed_bulk_string is None:
                        break
                    self._commands.append(parsed_bulk_string)
                    self._buffer = self._buffer[consumed_bytes:]
                case b"+":  # Simple string
                    parsed_simple_string, consumed_bytes = self._parse_simple_string(self._buffer)
                    if parsed_simple_string is None:
                        break
                    self._commands.append(parsed_simple_string)
                    self._buffer = self._buffer[consumed_bytes:]
                case b"-":  # Simple error
                    parsed_simple_error, consumed_bytes = self._parse_simple_error(self._buffer)
                    if parsed_simple_error is None:
                        break
                    self._commands.append(parsed_simple_error)
                    self._buffer = self._buffer[consumed_bytes:]
                case b":":  # Integer
                    parsed_integer, consumed_bytes = self._parse_simple_error(self._buffer)
                    if parsed_integer is None:
                        break
                    self._commands.append(parsed_integer)
                    self._buffer = self._buffer[consumed_bytes:]

    def _try_parse_server(self):
        """
        Internal method to parse as many full commands from the buffer as possible.
        This is the core of the state machine.
        """
        crlf = CRLF
        crlf_len = CRLF_LEN
        while True:
            # Parsing until the buffer is exhausted or an incomplete command is found.
            if not self._buffer:
                break

            # Find the position of the first delimiter
            first_crlf_pos = self._buffer.find(crlf)
            if first_crlf_pos == -1:
                # Not even a full line in the buffer yet, wait for more data.
                break

            first_byte = self._buffer[0:1]

            if first_byte == b"*":
                # It's an array, the start of a command.
                command, consumed_bytes = self._parse_array(self._buffer)
                if command is None:
                    # The full array data isn't in the buffer yet.
                    break

                # A full command was parsed. Add it to our queue.
                self._commands.append(command)
                # And remove the consumed bytes from the buffer.
                self._buffer = self._buffer[consumed_bytes:]
            else:
                # For now, we only support arrays as the top-level type for commands.
                # In a real Redis parser, you would handle other types here too.
                raise ProtocolError(f"Unsupported request type: {first_byte!r}")

    def _parse_array(self, buffer: bytearray) -> tuple[list[str] | None, int]:
        """
        Parses a RESP array from the buffer.
        Returns the parsed array and the number of bytes consumed.
        If the command is incomplete, returns (None, 0).
        """
        crlf = CRLF
        crlf_len = CRLF_LEN
        first_crlf_pos = buffer.find(crlf)
        line = buffer[1:first_crlf_pos]

        try:
            array_len = int(line)
        except ValueError:
            raise ProtocolError(f"Invalid array length: {line!r}") from None

        command_parts = []
        current_pos = first_crlf_pos + crlf_len

        for _ in range(array_len):
            # Try to parse one bulk string for each element in the array.
            element, consumed = self._parse_bulk_string(buffer[current_pos:])
            if element is None:
                # The buffer doesn't contain the full bulk string yet.
                return None, 0

            command_parts.append(element)
            current_pos += consumed

        # If we get here, the full command was parsed successfully.
        return command_parts, current_pos

    def _parse_bulk_string(self, buffer: bytearray) -> tuple[str | None, int]:
        """
        Parses a single RESP Bulk String.
        Returns the string and the number of bytes consumed.
        """
        crlf = CRLF
        crlf_len = CRLF_LEN
        first_crlf_pos = buffer.find(crlf)
        if first_crlf_pos == -1:
            return None, 0

        line = buffer[1:first_crlf_pos]

        try:
            str_len = int(line)
        except ValueError:
            raise ProtocolError(f"Invalid bulk string length: {line!r}") from None

        # The bulk string data starts after the CRLF of its length prefix
        str_start = first_crlf_pos + crlf_len
        str_end = str_start + str_len

        # Check if the full bulk string data (including its final CRLF) is in the buffer
        if len(buffer) < str_end + crlf_len:
            return None, 0

        # Extract the bulk string and decode it
        bulk_str = buffer[str_start:str_end].decode("utf-8")

        # Total bytes consumed is the end of the string + its final CRLF
        consumed_bytes = str_end + crlf_len

        return bulk_str, consumed_bytes

    def _parse_simple_string(self, buffer: bytearray) -> tuple[str | None, int]:
        first_crlf_pos = buffer.find(CRLF)
        if first_crlf_pos == -1:
            return None, 0

        sstring = buffer[1:first_crlf_pos].decode("utf-8")
        return sstring, len(sstring) + CRLF_LEN + 1

    def _parse_simple_error(self, buffer: bytearray) -> tuple[str | None, int]:
        first_crlf_pos = buffer.find(CRLF)
        if first_crlf_pos == -1:
            return None, 0

        serror = buffer[1:first_crlf_pos].decode("utf-8")
        return serror, len(serror) + CRLF_LEN + 1

    def _parse_integer(self, buffer: bytearray) -> tuple[str | None, int]:
        first_crlf_pos = buffer.find(CRLF)
        if first_crlf_pos == -1:
            return None, 0

        parsed_int = buffer[1:first_crlf_pos].decode("utf-8")
        return parsed_int, len(parsed_int) + CRLF_LEN + 1


def encode_simple_string(string: str) -> bytes:
    return f"+{string}\r\n".encode()


def encode_bulk_string(string: str | None) -> bytes:
    if not string:
        return b"$-1\r\n"
    return f"${len(string)}\r\n{string}\r\n".encode()


def encode_integer(integer: int) -> bytes:
    return f":{integer}\r\n".encode()


def encode_simple_error(error_message, error_prefix="ERR") -> bytes:
    return f"-{error_prefix} {error_message}\r\n".encode()


def encode_array(strings: list[str]):
    out = f"*{len(strings)}\r\n"
    for string in strings:
        out += f"${len(string)}\r\n{string}\r\n"
    return out.encode()
