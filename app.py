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
        self.files = []
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
                    state = MenuState.PEERLIST
                elif option == 2:
                    state = MenuState.PEERADD
                elif option == 3:
                    state = MenuState.PEERREMOVE
            elif state == MenuState.FILEMANAGEMENT:
                option = Menu.menu_filemanagement(self)
                if option == 0:
                    state = MenuState.MAIN
                elif option == 1:
                    state = MenuState.FILELIST
                elif option == 2:
                    state = MenuState.FILESEARCH
                elif option == 3:
                    state = MenuState.FILESETDIR
            elif state == MenuState.PEERLIST:
                option = Menu.menu_listpeers(self)
                if option == 0:
                    state = MenuState.PEERMANAGEMENT
            elif state == MenuState.PEERADD:
                option = Menu.menu_addpeer(self)
                if option == 0:
                    state = MenuState.PEERMANAGEMENT
                elif option == 1:
                    state = MenuState.PEERADDMANUAL
                elif option == 2:
                    state = MenuState.PEERADDDISCOVERY
            elif state == MenuState.PEERREMOVE:
                option = Menu.menu_removepeer(self)
                if option == 0:
                    state = MenuState.PEERMANAGEMENT
            elif state == MenuState.FILELIST:
                option = Menu.menu_listfiles(self)
                if option == 0:
                    state = MenuState.FILEMANAGEMENT
            elif state == MenuState.FILESEARCH:
                option = Menu.menu_searchfile(self)
                if option == 0:
                    state = MenuState.FILEMANAGEMENT
            elif state == MenuState.FILESETDIR:
                option = Menu.menu_setfiledir(self)
                if option == 0:
                    state = MenuState.FILEMANAGEMENT
            elif state == MenuState.PEERADDMANUAL:
                option = Menu.menu_addpeer_manual(self)
                if option == 0:
                    state = MenuState.PEERADD
            elif state == MenuState.PEERADDDISCOVERY:
                option = Menu.menu_addpeer_discovery(self)
                if option == 0:
                    state = MenuState.PEERADD
            else:
                raise Exception('Invalid MenuState')