class Peer:
    def __init__(self, uid: str, ip: str, port: int) -> None:
        self.uid = uid
        self.ip = ip
        self.port = port
        self.files = []
    def add_file(self, filename : str):
        self.files.append(filename)
    def remove_file(self, filename: str):
        self.files.remove(filename)
    def __str__(self) -> str:
        return f'Peer {self.uid} ({self.ip}:{self.port})'