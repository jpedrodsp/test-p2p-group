from peer import Peer
import uuid

MESSAGE_SEPARATOR = b'|||'

def generate_uid() -> str:
    return uuid.uuid4().hex.upper()[:8]

class Application:
    def __init__(self) -> None:
        self.uid = generate_uid()
        self.known_peers = {}
    def run(self) -> None:
        pass
    def add_known_peer(self, peer: Peer) -> None:
        self.known_peers[peer.uid] = peer
    def remove_known_peer(self, uid: str) -> None:
        del self.known_peers[uid]
    def get_known_peer(self, uid: str) -> Peer:
        return self.known_peers[uid]
    def handle_message(self, message: bytes) -> None:
        header = message.split(MESSAGE_SEPARATOR)[0]
        switcher = {
            b'HELLO': self.handle_hello,
        }
        switcher[header](message)
    def handle_hello(self, message: bytes) -> None:
        pass