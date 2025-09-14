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

    def SET(self, *args):
        self._socket.sendall(protocol.encode_array(["SET", *args]))

    def GET(self, key):
        self._socket.sendall(protocol.encode_array(["GET", key]))

    def DEL(self, keys: list[str]):
        self._socket.sendall(protocol.encode_array(["DEL", *keys]))

    def recv(self, num_bytes=1024):
        return self._socket.recv(num_bytes)


def main():
    client = Client()
    while True:
        prompt = input("cachica> ").strip().split(" ")
        match prompt[0].upper():
            case "SET":
                match len(prompt):
                    case 3:
                        client.SET(*prompt[1:])
                    case 5:
                        if prompt[3].upper() in ("PX", "EX") and prompt[4].isdigit():
                            client.SET(*prompt[1:]) 
                    case _:
                        print("Incorrect args for 'set' command")
                        continue
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
            case "DEL":
                if len(prompt) < 2:
                    print("Incorrect number of args for 'del' command")
                    continue
                else:
                    client.DEL(prompt[1:])
            case _:
                print("Unknown command.")
                continue
        data = client.recv()
        print(data.decode().strip())


if __name__ == "__main__":
    main()
