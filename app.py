from peer import Peer


class Application:
    def __init__(self) -> None:
        self.known_peers = {}
    def run(self) -> None:
        pass
    def add_known_peer(self, peer: Peer) -> None:
        self.known_peers[peer.uid] = peer
    def remove_known_peer(self, uid: str) -> None:
        del self.known_peers[uid]
    def get_known_peer(self, uid: str) -> Peer:
        return self.known_peers[uid]