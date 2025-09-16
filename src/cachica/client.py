import socket

from cachica import protocol


class Client:
    def __init__(self, client_id="cachica-client", host="127.0.0.1", port=8888):
        self._client_id = client_id
        self._server_host = host
        self._server_port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._server_host, self._server_port))
        self._parser = protocol.Parser(is_client=True)

    def PING(self, message=None):
        arr = ["PING"]
        if message is not None:
            arr.append(message)
        self._socket.sendall(protocol.encode_array(arr))
        return self._recv()

    def SET(self, *args):
        self._socket.sendall(protocol.encode_array(["SET", *args]))
        return self._recv()

    def GET(self, key):
        self._socket.sendall(protocol.encode_array(["GET", key]))
        return self._recv()

    def DEL(self, keys: list[str]):
        self._socket.sendall(protocol.encode_array(["DEL", *keys]))
        return self._recv()

    def _recv(self, num_bytes=1024):
        resp_data = self._socket.recv(num_bytes)
        self._parser.feed(resp_data)
        return self._parser.get_command()


def main():
    client = Client()
    while True:
        prompt = input("cachica> ").strip().split(" ")
        match prompt[0].upper():
            case "SET":
                match len(prompt):
                    case 3:
                        resp = client.SET(*prompt[1:])
                    case 5:
                        if prompt[3].upper() in ("PX", "EX") and prompt[4].isdigit():
                            resp = client.SET(*prompt[1:])
                    case _:
                        print("Incorrect args for 'set' command")
                        continue
            case "GET":
                if len(prompt) != 2:
                    print("Incorrect number of args for 'get' command")
                    continue
                resp = client.GET(prompt[1])
            case "PING":
                if len(prompt) > 2:
                    print("Incorrect number of args for 'PING' command")
                    continue
                if len(prompt) == 1:
                    resp = client.PING()
                else:
                    resp = client.PING(prompt[1])
            case "DEL":
                if len(prompt) < 2:
                    print("Incorrect number of args for 'del' command")
                    continue
                else:
                    resp = client.DEL(prompt[1:])
            case _:
                print("Unknown command.")
                continue
        print(resp)


if __name__ == "__main__":
    main()
