import asyncio
import functools
import logging
from asyncio import StreamReader, StreamWriter

from cachica.datastore import DataStore
from cachica.protocol import Parser, ProtocolError

logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    format="{asctime} [{name}] [{levelname}] {filename}:{lineno:d} - {message}",
)

logger = logging.getLogger(__name__)


async def handle_client(datastore: DataStore, reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info(f"Client connected from: {addr}")

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

                logger.info(f"Processing command: {command}")

                response = datastore.process(command)

                writer.write(response)
                await writer.drain()

    except ConnectionResetError:
        logger.warning(f"Connection reset by client {addr}")
    except ProtocolError as e:
        logger.error(f"Protocol Error from {addr}: {e}")
        writer.write(f"-ERR {e}\r\n".encode("utf-8"))
        await writer.drain()
    except Exception as e:
        logger.exception(f"An unexpected error occurred with client {addr}: {e}")
    finally:
        logger.info(f"Closing the connection with {addr}")
        writer.close()
        await writer.wait_closed()


async def run_server():
    datastore = DataStore()
    client_handler = functools.partial(handle_client, datastore)

    server = await asyncio.start_server(client_handler, "0.0.0.0", 8888)

    addr = server.sockets[0].getsockname()
    logger.info(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


def main():
    """The synchronous entry point for the application script."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutting down.")


if __name__ == "__main__":
    main()
