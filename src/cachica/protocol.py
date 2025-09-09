def parse_command(req: bytes):
    data = req.decode("utf-8")
    return data[:4], [] 
