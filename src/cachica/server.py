import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from collections import deque

from protocol import BadRequest, parse_request_from_stream_reader

logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    format="{asctime} [{name}] [{levelname}] {filename}:{lineno:d} - {message}",
)

logger = logging.getLogger(__name__)


async def handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info(f"Client connected from: {addr}")

    try:
        # Loop indefinitely to handle multiple commands from the same client
        while True:
            command_dq: deque | None = await parse_request_from_stream_reader(reader)
            if command_dq is None:
                break
            command_str = " ".join(command_dq)
            writer.write(command_str.encode(encoding="ascii"))
            await writer.drain()
            logger.info(f"Echoed '{command_str}' back to {addr}")

    except ConnectionResetError:
        logger.warning(f"Connection reset by client {addr}")
    except BadRequest:
        logger.critical("Request must start with b'*'")
    finally:
        logger.info(f"Closing the connection with {addr}")
        writer.close()
        await writer.wait_closed()


async def run_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 8888)

    addr = server.sockets[0].getsockname()
    logger.info(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run_server())
