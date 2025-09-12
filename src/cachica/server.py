import pdb
import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from collections import deque

import protocol 
import datastore

logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    format="{asctime} [{name}] [{levelname}] {filename}:{lineno:d} - {message}",
)

logger = logging.getLogger(__name__)


async def handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info(f"Client connected from: {addr}")
    parser = protocol.Parser()
    ds = datastore.DataStore()  
    try:
        while True:
            data = await reader.read(1024)
            parser.feed(data)
            # pdb.set_trace()
            command = parser.get_command()
            if command:
                print(f"`{command}` sent for processing")
                res = ds.process(command)
                writer.write(res.encode('ascii'))
            if reader.at_eof():
                break
    except ConnectionResetError:
        logger.warning(f"Connection reset by client {addr}")
    except Exception as e:
        logger.critical(f"Parsing failed: {e}")
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
