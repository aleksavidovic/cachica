import asyncio
import logging
from asyncio import StreamReader, StreamWriter

logging.basicConfig(
    level=logging.DEBUG, style="{", format="[{threadName} ({thread})] {message}"
)


async def handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info("peername")
    logging.info(f"Client connected from: {addr}")

    try:
        # Loop indefinitely to handle multiple commands from the same client
        while True:
            # Use readline() to read data until a newline character is received.
            data = await reader.readline()

            # If readline() returns an empty bytes object, 
            # the client has closed the connection.
            if not data:
                break

            message = data.decode().strip()
            logging.info(f"Received '{message}' from {addr}")

            # Echo the received data back to the client.
            writer.write(data)
            await writer.drain()
            logging.info(f"Echoed '{message}' back to {addr}")

    except ConnectionResetError:
        logging.warning(f"Connection reset by client {addr}")
    finally:
        # Close the connection when the loop is broken.
        logging.info(f"Closing the connection with {addr}")
        writer.close()
        await writer.wait_closed()


async def run_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 8888)

    addr = server.sockets[0].getsockname()
    logging.info(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run_server())
