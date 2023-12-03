from peer import Peer
from menu import Menu, MenuState
import uuid
import threading

MESSAGE_SEPARATOR = b'|||'

def generate_uid() -> str:
    return uuid.uuid4().hex.upper()[:8]

def get_file_dir() -> str:
    return 'files/'

def get_network_port() -> int:
    return 50000

def get_network_ip() -> str:
    return '0.0.0.0'

def get_network_address() -> (str, int):
    return (get_network_ip(), get_network_port())

def set_network_port(ctx: 'Application', port: int) -> None:
    previous_address = ctx.network_address
    ctx.network_address = (previous_address[0], port)
    
def set_network_ip(ctx: 'Application', ip: str) -> None:
    previous_address = ctx.network_address
    ctx.network_address = (ip, previous_address[1])

def set_network_address(ctx: 'Application', ip: str, port: int) -> None:
    ctx.network_address = (ip, port)

class Application:
    def __init__(self) -> None:
        self.uid = generate_uid()
        self.known_peers = {}
        self.files = []
        self.file_dir = get_file_dir()
        self.network_address = get_network_address()
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
                elif option == 3:
                    state = MenuState.SYSTEMINFO
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
            elif state == MenuState.SYSTEMINFO:
                option = Menu.menu_systeminfo(self)
                if option == 0:
                    state = MenuState.MAIN
            else:
                raise Exception('Invalid MenuState')