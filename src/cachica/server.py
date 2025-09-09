import asyncio
import logging
from asyncio import StreamReader, StreamWriter

logging.basicConfig(
    level=logging.DEBUG, style="{", format="[{threadName} ({thread})] {message}"
)


async def handle_client(reader: StreamReader, writer: StreamWriter):
    # Get client's address
    addr = writer.get_extra_info("peername")
    logging.debug(f"Client connected from: {addr}")

    # Read data from the client
    data_buffer: bytearray = bytearray()
    while True:
        data = await reader.read(512)
        logging.debug(f"recv: {data}")
        if not data:
            break
        data_buffer.extend(data)

    message = data_buffer.decode()
    print(f"Received {message} from {addr}")

    # Send the response back to the client
    writer.write(data_buffer)
    await writer.drain()

    # Close the connection
    print(f"Close the connection with {addr}")
    writer.close()


async def run_server():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    logging.info(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run_server())
