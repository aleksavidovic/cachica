
class DataStore:
    def __init__(self):
        pass

    def process(self, command: str):
        match  command[0]:
            case "PING":
                return "PONG"
            case "SET":
                res = self._set(command[1], command[2])
                if res:
                    return "success"
                else:
                    return "SET command failed"

    def _set(self, k, v):
        return 1

