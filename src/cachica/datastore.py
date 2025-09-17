import logging
import pdb
import time
from random import sample
from dataclasses import dataclass
from cachica import protocol
from enum import Enum, auto
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)

class DataType(Enum):
    STRING = auto()
    LIST = auto()

@dataclass
class CacheValue:
    __slots__ = ('value_type', 'value')
    value_type: DataType
    value: Any

class DataStore:
    def __init__(self):
        self._data: dict[str, CacheValue] = {}
        self._expiry: dict[str, float] = {}
        self._commands = {
            "PING": self._handle_ping,
            "ECHO": self._handle_echo,
            "SET": self._handle_set,
            "GET": self._handle_get,
            "DEL": self._handle_del,
            "LPUSH": self._handle_lpush,
            "LPOP": self._handle_lpop,
        }

    def _handle_lpush(self, args: list):
        logger.debug("LPUSH with args %s", args)
        if len(args) < 2:
            return protocol.encode_simple_error("wrong number of args")
        if args[0] in self._data.keys():
            if self._data[args[0]].value_type == DataType.LIST:
                self._data[args[0]].value.appendleft(args[1])
                return protocol.encode_integer(len(args)-1)
        else:
            self._data[args[0]] = CacheValue(DataType.LIST, deque(args[1:]))
            return protocol.encode_integer(len(args[1:]))
        return protocol.encode_simple_error("wrong type")

    def _handle_lpop(self, args: list):
        logger.debug("LPOP with args %s", args)
        if len(args) != 1:
            return protocol.encode_simple_error("wrong number of args")
        if args[0] in self._data.keys():
            if self._data[args[0]].value_type == DataType.LIST and len(self._data[args[0]].value) > 0:
                val = self._data[args[0]].value.popleft()
                return protocol.encode_simple_string(val)
            return protocol.encode_simple_error("wrong type")
        return protocol.encode_simple_error("wrong key")



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
        if len(args) not in (2, 4):
            return protocol.encode_simple_error("wrong number of arguments for 'set' command", error_prefix="ERR")
        if len(args) == 2:
            # if args == 2 => no expiry time is set => write only to _data not to _expiry
            key, value = args
            self._set(key, CacheValue(DataType.STRING, value))
        elif len(args) == 4:
            (key, value, expire_type, expire_value) = args
            if expire_type in ("EX", "PX") and expire_value.isdigit():
                ttl = 0
                if expire_type == "EX":
                    ttl = time.monotonic() + int(expire_value)
                elif expire_type == "PX":
                    ttl = time.monotonic() + (int(expire_value) / 1000)  # /1000 to get s from ms
                self._set_expiry(key, ttl)
                self._set(key, CacheValue(DataType.STRING, value))
            else:
                return protocol.encode_simple_error("Incorrect args")
        return protocol.encode_simple_string("OK")

    def _handle_get(self, args: list) -> bytes:
        if len(args) != 1:
            return protocol.encode_simple_error("wrong number of arguments for 'get' command", error_prefix="ERR")
        key = args[0]
        # check _expiry
        if key in self._expiry and time.monotonic() > self._expiry[key]:
            logger.debug("PASSIVE EVICTION: deleting expired key %s", key)
            del self._expiry[key]
            del self._data[key]
            return protocol.encode_bulk_string(None)

        value: str | None = self._get(key)
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

    def _set_expiry(self, key: str, ex: float):
        self._expiry[key] = ex

    def _set(self, key: str, value: CacheValue):
        self._data[key] = value

    def _get(self, key: str) -> str | None:
        entry = self._data.get(key)
        if entry is not None and entry.value_type != DataType.LIST:
            return entry.value
        return None

    def evict_expired_keys(self):
        len_keys = len(self._expiry.keys())
        if len_keys == 0:
            return
        sample_size = 10
        keys_to_check = sample(list(self._expiry.keys()), sample_size)

        now = time.monotonic()
        for key in keys_to_check:
            expiry_time = self._expiry.get(key)
            if expiry_time is not None and now > expiry_time:
                logger.debug("ACTIVE EVICTION: deleting expired key %s", key)
                del self._expiry[key]
                del self._data[key]
