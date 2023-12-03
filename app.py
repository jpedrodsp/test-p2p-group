from peer import Peer
from menu import Menu, MenuState
import uuid
import threading
import os
import time
import socket, socketserver

MESSAGE_SEPARATOR = b'|||'
LISTENER_TIMEOUT = 1.0

def generate_uid() -> str:
    return uuid.uuid4().hex.upper()[:8]

def get_file_dir() -> str:
    return 'files/'

def get_network_port() -> int:
    return 51000

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
    
def get_files(ctx: 'Application') -> [str]:
    if not os.path.exists(ctx.file_dir):
        os.makedirs(ctx.file_dir)
    files = os.listdir(ctx.file_dir)
    return files

def validate_address(host: str, port: int) -> bool:
    """
    Validates if the given address is valid and available.
    A valid address can handle the 'HELLO' message.
    """
    clsck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clsck.settimeout(LISTENER_TIMEOUT)
    try:
        clsck.connect((host, port))
        clsck.sendall(b'HELLO')
        rsp = b''
        data = clsck.recv(1024)
        if not data:
            pass
        rsp += data
        if rsp != b'HELLOBACK':
            raise Exception('Invalid response.')
        clsck.close()
        return True
    except:
        clsck.close()
        return False
    
def log(start: float, msg: str, *args, **kwargs) -> None:
    end = time.time()
    print(f'[{end - start:.3f}s] {msg}', *args, **kwargs)

class Application:
    def __init__(self) -> None:
        self._start = time.time()
        self.uid = generate_uid()
        self.known_peers = {}
        self.file_dir = get_file_dir()
        self.network_address = get_network_address()
        self.files = get_files(self)
        self._listen = True
        self._listener_thread = threading.Thread(target=self._listener)
        self._listener_thread.start()
        log(self._start, 'Application initialized.')
    def run(self) -> None:
        if validate_address(self.network_address[0], self.network_address[1]) != True:
            raise Exception('Already in use or invalid network address.')
        self.menuloop()
        self.stop()
    def stop(self) -> None:
        self._listen = False
        self._listener_thread.join()
    def add_known_peer(self, peer: Peer) -> None:
        self.known_peers[peer.uid] = peer
    def remove_known_peer(self, uid: str) -> None:
        del self.known_peers[uid]
    def get_known_peer(self, uid: str) -> Peer:
        return self.known_peers[uid]
    def _listener(self) -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.settimeout(LISTENER_TIMEOUT)
        srv.bind(self.network_address)
        srv.listen()
        while self._listen == True:
            try:
                conn, addr = srv.accept()
                msg = b''
                data = conn.recv(1024)
                if not data:
                    pass
                msg += data
                self.handle_message(conn, msg)
                conn.close()
            except socket.timeout:
                pass
        srv.close()
    def handle_message(self, connection: socket.socket, message: bytes) -> None:
        log(self._start, f'Received message: {message}')
        header = message.split(MESSAGE_SEPARATOR)[0]
        switcher = {
            b'HELLO': self.handle_hello,
        }
        switcher[header](connection, message)
    def handle_hello(self, connection: socket.socket, message: bytes) -> None:
        msg = b'HELLOBACK'
        connection.send(msg)
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