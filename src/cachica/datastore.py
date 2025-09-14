from cachica import protocol


class DataStore:
    def __init__(self):
        self._data = {}

    def process(self, command: list[str]) -> bytes:
        """
        Processes a parsed command and returns a RESP-formatted byte response.
        """
        if not command:
            return b"-ERR empty command\r\n"

        command_name = command[0].upper()
        args = command[1:]

        # This is our command dispatcher.
        match command_name:
            case "PING":
                if len(args) == 0:
                    return protocol.encode_simple_string("PONG")
                elif len(args) == 1:
                    # Return the argument as a bulk string
                    message = args[0]
                    return f"${len(message)}\r\n{message}\r\n".encode()
                else:
                    return b"-ERR wrong number of arguments for 'ping' command\r\n"

            case "ECHO":
                if len(args) != 1:
                    return b"-ERR wrong number of arguments for 'ping' command\r\n"

                message = args[0]
                return f"${len(message)}\r\n{message}\r\n".encode()

            case "SET":
                if len(args) != 2:
                    return b"-ERR wrong number of arguments for 'set' command\r\n"
                key, value = args
                self._set(key, value)
                return protocol.encode_simple_string("OK")

            case "GET":
                if len(args) != 1:
                    return b"-ERR wrong number of arguments for 'get' command\r\n"
                key = args[0]
                value = self._get(key)
                if value is None:
                    # RESP Null
                    return b"$-1\r\n"
                else:
                    return f"${len(value)}\r\n{value}\r\n".encode()

            case _:
                return f"-ERR unknown command `{command_name}`\r\n".encode()

    def _set(self, key: str, value: str):
        self._data[key] = value

    def _get(self, key: str) -> str | None:
        return self._data.get(key)
