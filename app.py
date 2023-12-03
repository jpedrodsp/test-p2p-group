from peer import Peer
from menu import Menu, MenuState
import uuid

MESSAGE_SEPARATOR = b'|||'

def generate_uid() -> str:
    return uuid.uuid4().hex.upper()[:8]

class Application:
    def __init__(self) -> None:
        self.uid = generate_uid()
        self.known_peers = {}
    def run(self) -> None:
        self.menuloop()
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
    def menuloop(self) -> None:
        state: MenuState = MenuState.MAIN
        option: int = 0
        while True:
            if state == MenuState.MAIN:
                option = Menu.menu_main(self)
                if option == 0:
                    break
                elif option == 1:
                    state = MenuState.PEERMANAGEMENT
                elif option == 2:
                    state = MenuState.FILEMANAGEMENT
            elif state == MenuState.PEERMANAGEMENT:
                option = Menu.menu_peermanagement(self)
                if option == 0:
                    state = MenuState.MAIN
                elif option == 1:
                    pass
                elif option == 2:
                    pass
                elif option == 3:
                    pass
            elif state == MenuState.FILEMANAGEMENT:
                option = Menu.menu_filemanagement(self)
                if option == 0:
                    state = MenuState.MAIN
                elif option == 1:
                    pass
                elif option == 2:
                    pass
                elif option == 3:
                    pass
            else:
                raise Exception('Invalid MenuState')