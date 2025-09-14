from cachica import protocol


class DataStore:
    def __init__(self):
        self._data = {}
        self._commands = {
            "PING": self._handle_ping,
            "ECHO": self._handle_echo,
            "SET": self._handle_set,
            "GET": self._handle_get,
            "DEL": self._handle_del,
        }

    def _handle_ping(self, args: list) -> bytes:
        if len(args) == 0:
            return protocol.encode_simple_string("PONG")
        elif len(args) == 1:
            # Return the argument as a bulk string
            message = args[0]
            return protocol.encode_bulk_string(message)
        else:
            return protocol.encode_simple_error("wrong number of arguments for 'ping' command", error_prefix="ERR")

    def _handle_echo(self, args: list) -> bytes:
        if len(args) != 1:
            return protocol.encode_simple_error("wrong number of arguments for 'echo' command", error_prefix="ERR")

        message = args[0]
        return protocol.encode_bulk_string(message)

    def _handle_set(self, args: list) -> bytes:
        if len(args) != 2:
            return protocol.encode_simple_error("wrong number of arguments for 'set' command", error_prefix="ERR")
        key, value = args
        self._set(key, value)
        return protocol.encode_simple_string("OK")

    def _handle_get(self, args: list) -> bytes:
        if len(args) != 1:
            return protocol.encode_simple_error("wrong number of arguments for 'get' command", error_prefix="ERR")
        key = args[0]
        value = self._get(key)
        if value is None:
            # RESP Null
            return protocol.encode_bulk_string(None)
        else:
            return protocol.encode_bulk_string(value)

    def _handle_del(self, args: list) -> bytes:
        if len(args) == 0:
            return protocol.encode_simple_error("wrong number of arguments for 'del' command", error_prefix="ERR")
        deleted = 0
        for key in args:
            if key in self._data:
                del self._data[key]
                deleted += 1
        return protocol.encode_integer(deleted)

    def process(self, command: list[str]) -> bytes:
        """
        Processes a parsed command and returns a RESP-formatted byte response.
        """
        if not command:
            return protocol.encode_simple_error("empty command", error_prefix="ERR")

        command_name = command[0].upper()
        args = command[1:]

        if command_name in self._commands:
            return self._commands[command_name](args)
        else:
            return protocol.encode_simple_error(f"unknown command '{command_name}'", error_prefix="ERR")

    def _set(self, key: str, value: str):
        self._data[key] = value

    def _get(self, key: str) -> str | None:
        return self._data.get(key)
