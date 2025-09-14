from cachica import protocol


class DataStore:
    def __init__(self):
        self._data = {}

    def process(self, command: list[str]) -> bytes:
        """
        Processes a parsed command and returns a RESP-formatted byte response.
        """
        if not command:
            return protocol.encode_simple_error("empty command", error_prefix="ERR")

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
                    return protocol.encode_bulk_string(message)
                else:
                    return protocol.encode_simple_error(
                        "wrong number of arguments for 'ping' command", error_prefix="ERR"
                    )

            case "ECHO":
                if len(args) != 1:
                    return protocol.encode_simple_error(
                        "wrong number of arguments for 'ping' command", error_prefix="ERR"
                    )

                message = args[0]
                return protocol.encode_bulk_string(message)

            case "SET":
                if len(args) != 2:
                    return protocol.encode_simple_error(
                        "wrong number of arguments for 'set' command", error_prefix="ERR"
                    )
                key, value = args
                self._set(key, value)
                return protocol.encode_simple_string("OK")

            case "GET":
                if len(args) != 1:
                    return protocol.encode_simple_error(
                        "wrong number of arguments for 'get' command", error_prefix="ERR"
                    )
                key = args[0]
                value = self._get(key)
                if value is None:
                    # RESP Null
                    return protocol.encode_bulk_string()
                else:
                    return protocol.encode_bulk_string(value)

            case _:
                return protocol.encode_simple_error(f"unknown command `{command_name}`", error_prefix="ERR")

    def _set(self, key: str, value: str):
        self._data[key] = value

    def _get(self, key: str) -> str | None:
        return self._data.get(key)
