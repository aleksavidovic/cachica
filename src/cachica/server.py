import os
from dotenv import load_dotenv
load_dotenv()
import uvloop
import asyncio
import functools
import logging
import logging.config
from asyncio import StreamReader, StreamWriter

from cachica.config import get_logging_config
from cachica.datastore import DataStore
from cachica.protocol import Parser, ProtocolError

# --- LOGGING CONFIG ---
log_level_from_env = os.getenv("LOG_LEVEL", "INFO")
logging_config = get_logging_config(log_level_from_env)
logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)


async def handle_client(datastore: DataStore, reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info("Client connected from: %s", addr)

    parser = Parser()

    try:
        while not reader.at_eof():
            data = await reader.read(1024)
            if not data:
                break

            parser.feed(data)
            # pdb.set_trace()

            while True:
                command = parser.get_command()
                if command is None:
                    break

                logger.info("Processing command: %s", command)

                response = datastore.process(command)

                writer.write(response)
                await writer.drain()

    except ConnectionResetError:
        logger.warning("Connection reset by client: %s", addr)
    except ProtocolError as e:
        logger.error("Protocol Error from %s: %s", addr, e)
        writer.write(f"-ERR {e}\r\n".encode("utf-8"))           # TODO: Questionable?
        await writer.drain()
    except Exception as e:
        logger.exception("An unexpected error occurred with client %s: %s", addr, e)
    finally:
        logger.info("Closing the connection with %s", addr)
        writer.close()
        await writer.wait_closed()


async def eviction_loop(datastore: DataStore):
    while True:
        await asyncio.sleep(0.1)
        datastore.evict_expired_keys()


async def run_server():
    datastore = DataStore()
    client_handler = functools.partial(handle_client, datastore)

    server = await asyncio.start_server(client_handler, "0.0.0.0", 8888)
    asyncio.create_task(eviction_loop(datastore))
    addr = server.sockets[0].getsockname()
    logger.info("Serving on %s", addr)

    async with server:
        await server.serve_forever()


def main():
    """The synchronous entry point for the application script."""
    try:
        uvloop.run(run_server())
        # asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutting down.")


if __name__ == "__main__":
    main()
