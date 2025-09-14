import socket

from cachica import protocol


class Client:
    def __init__(self, host="127.0.0.1", port=8888):
        self._server_host = host
        self._server_port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._server_host, self._server_port))

    def PING(self, message=None):
        arr = ["PING"]
        if message is not None:
            arr.append(message)
        self._socket.sendall(protocol.encode_array(arr))

    def SET(self, key, value):
        self._socket.sendall(protocol.encode_array(["SET", key, value]))

    def GET(self, key):
        self._socket.sendall(protocol.encode_array(["GET", key]))

    def DEL(self, keys):
        pass

    def recv(self, num_bytes=1024):
        return self._socket.recv(num_bytes)


def main():
    client = Client()
    while True:
        prompt = input("cachica> ").strip().split(" ")
        match prompt[0].upper():
            case "SET":
                if len(prompt) != 3:
                    print("Incorrect number of args for 'set' command")
                    continue
                client.SET(*prompt[1:])
            case "GET":
                if len(prompt) != 2:
                    print("Incorrect number of args for 'get' command")
                    continue
                client.GET(prompt[1])
            case "PING":
                if len(prompt) > 2:
                    print("Incorrect number of args for 'PING' command")
                    continue
                if len(prompt) == 1:
                    client.PING()
                else:
                    client.PING(prompt[1])
            case _:
                print("Unknown command.")
                continue
        data = client.recv()
        print(data.decode().strip())


if __name__ == "__main__":
    main()
