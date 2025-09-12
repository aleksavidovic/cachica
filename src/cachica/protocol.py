from collections import deque
import logging
import pdb

logger = logging.getLogger(__name__)

CRLF = b'\r\n' # Standard RESP terminator

class ProtocolError(Exception):
    pass

class Parser:
    """A synchronous, stateful RESP parser."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._commands = deque() 

    def feed(self, data: bytes) -> None:
        """Adds raw network data to the internal buffer."""
        self._buffer.extend(data)
        self._try_parse()

    def get_command(self) -> list[str] | None:
        """Returns a fully parsed command, or None if none are ready."""
        if self._commands:
            return self._commands.popleft()
        return None
        
    def _try_parse(self):
        """
        Internal method to parse as many full commands from the buffer as possible.
        This is the core of the state machine.
        """
        while True:
            # Keep parsing until the buffer is exhausted or an incomplete command is found.
            if not self._buffer:
                break
            
            # Find the position of the first delimiter
            first_crlf_pos = self._buffer.find(CRLF)
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
        first_crlf_pos = buffer.find(CRLF)
        line = buffer[1:first_crlf_pos]
        
        try:
            array_len = int(line)
        except ValueError:
            raise ProtocolError(f"Invalid array length: {line!r}")
        
        command_parts = []
        current_pos = first_crlf_pos + len(CRLF)

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
        first_crlf_pos = buffer.find(CRLF)
        if first_crlf_pos == -1:
            return None, 0

        line = buffer[1:first_crlf_pos]

        try:
            str_len = int(line)
        except ValueError:
            raise ProtocolError(f"Invalid bulk string length: {line!r}")
        
        # The bulk string data starts after the CRLF of its length prefix
        str_start = first_crlf_pos + len(CRLF)
        str_end = str_start + str_len

        # Check if the full bulk string data (including its final CRLF) is in the buffer
        if len(buffer) < str_end + len(CRLF):
            return None, 0
        
        # Extract the bulk string and decode it
        bulk_str = buffer[str_start:str_end].decode("utf-8")
        
        # Total bytes consumed is the end of the string + its final CRLF
        consumed_bytes = str_end + len(CRLF)
        
        return bulk_str, consumed_bytes

