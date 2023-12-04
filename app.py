from peer import Peer
from menu import Menu, MenuState
import uuid
import threading
import os
import time
import json
import socket, socketserver
from datetime import datetime

MESSAGE_SEPARATOR = b'|||'
LISTENER_TIMEOUT = 1.0
PEERUPDATE_TIMEOUT = 2.0
FILEUPDATE_TIMEOUT = 2.0

def generate_uid() -> str:
    return uuid.uuid4().hex.upper()[:8]

def get_file_dir() -> str:
    return 'files/'

def get_network_port() -> int:
    starting_ip = 51000
    actual_ip = starting_ip
    while True:
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.settimeout(LISTENER_TIMEOUT)
            srv.bind((get_network_host(), actual_ip))
            srv.close()
            return actual_ip
        except:
            actual_ip += 1
            if actual_ip >= 52000:
                raise Exception('Could not find a valid port.')

def get_network_host() -> str:
    return '0.0.0.0'

def get_friendly_network_host() -> list:
    """
    Return a list of all available IP addresses.
    
    Returns:
    - LAN IP: Obtained by connecting to a broadcast address and retrieving the sender's IP.
    - Loopback Defined IP: Obtained by resolving the hostname.
    - Loopback Default IP: Always 127.0.0.1 by default (localhost).
    """
    ips = []
    lan_ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect(('<broadcast>', 0))
        lan_ip = s.getsockname()[0]
        ips.append(lan_ip)
    except:
        pass
    try:
        loopback_ip = socket.gethostbyname(socket.gethostname())
        ips.append(loopback_ip)
    except:
        pass
    loopback_main_ip = '127.0.0.1'
    if loopback_main_ip not in ips:
        ips.append(loopback_main_ip)
    return ips

def get_network_address() -> (str, int):
    return (get_network_host(), get_network_port())

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
    content = f'[{end - start:.3f}s] {msg}'
    with open('log.txt', 'a') as f:
        f.write(content + '\n')
    # print(content, *args, **kwargs)

class Application:
    def __init__(self) -> None:
        self._start = time.time()
        log(self._start, '-' * 40)
        log(self._start, f'Today is {time.strftime("%d/%m/%Y")} at {time.strftime("%H:%M:%S")}')
        self.uid = generate_uid()
        self._knownpeers_lock = threading.Lock()
        self.known_peers = {}
        self._fileupdate_lock = threading.Lock()
        self.file_dir = get_file_dir()
        self.update_file_list()
        self.network_address = get_network_address()
        self.friendly_network_host = get_friendly_network_host()
        log(self._start, f'Network address: {self.network_address[0]}:{self.network_address[1]}')
        self._listen = True
        self._listener_thread = threading.Thread(target=self._listener)
        self._listener_thread.start()
        self._fileupdate_enabled = True
        self._fileupdate_thread = threading.Thread(target=self._fileupdate)
        self._fileupdate_thread.start()
        self._peerupdate_enabled = True
        self._peerupdate_thread = threading.Thread(target=self._peerupdate)
        self._peerupdate_thread.start()
    def run(self) -> None:
        log(self._start, 'Validating network address.')
        if validate_address(self.network_address[0], self.network_address[1]) != True:
            log(self._start, 'Could not validate network address.')
            raise Exception('Already in use or invalid network address.')
        log(self._start, 'Initializing application.')
        self.menuloop()
        self.stop()
    def stop(self) -> None:
        self._listen = False
        self._fileupdate_enabled = False
        self._peerupdate_enabled = False
        self._listener_thread.join()
        self._fileupdate_thread.join()
        self._peerupdate_thread.join()
    def add_known_peer(self, peer: Peer) -> None:
        self._knownpeers_lock.acquire()
        self.known_peers[peer.uid] = peer
        self._knownpeers_lock.release()
    def remove_known_peer(self, uid: str) -> None:
        self._knownpeers_lock.acquire()
        del self.known_peers[uid]
        self._knownpeers_lock.release()
    def get_known_peer(self, uid: str) -> Peer:
        self._knownpeers_lock.acquire()
        peer = self.known_peers[uid]
        self._knownpeers_lock.release()
        return peer
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
            b'ADDME': self.handle_addme,
            b'BROADCASTREQUEST': self.handle_broadcast_request,
            b'FILELIST': self.handle_filelist,
        }
        switcher[header](connection, message)
    def handle_hello(self, connection: socket.socket, message: bytes) -> None:
        """
        Handles the HELLO message.
        Hello messages are used to validate if the peer is available.
        """
        msg = b'HELLOBACK'
        connection.send(msg)
    def handle_addme(self, connection: socket.socket, message: bytes) -> None:
        """
        Handles the ADDME message.
        AddMe messages are used to add a peer to the known peers. The peer must respond with ACK or NACK, depending on the validation result.
        ACK means the peer was added successfully.
        NACK means the peer was not added due to validation issues, like NAT or firewall.
        """
        addr = connection.getpeername()
        client_uid = message.split(MESSAGE_SEPARATOR)[1].decode()
        client_ip = addr[0]
        client_port = int(message.split(MESSAGE_SEPARATOR)[2].decode())
        # Try connecting back to prevent NAT issues.
        res = validate_address(client_ip, client_port)
        if res != True:
            log(self._start, f'Client {client_uid} ({client_ip}:{client_port}) could not be validated.')
            msg = b'NACK'
            connection.send(msg)
            log(self._start, f'Sent: {msg}')
        else:
            log(self._start, f'Client {client_uid} ({client_ip}:{client_port}) connected. Adding to known peers.')
            peer = Peer(client_uid, client_ip, client_port)
            self.add_known_peer(peer)
            msg = b'ACK' + MESSAGE_SEPARATOR + self.uid.encode()
            connection.send(msg)
            log(self._start, f'Sent: {msg}')
    def handle_broadcast_request(self, connection: socket.socket, message: bytes) -> None:
        """
        Handles the BROADCASTREQUEST message.
        BroadcastRequest messages are used to request the known peers list.
        Response is a BROADCASTRESPONSE message.
        """
        my_peers = []
        for peer in self.known_peers.values():
            my_peers.append(
                (peer.uid, peer.ip, peer.port)
            )
        peerstr = json.dumps(my_peers)
        msg = b'BROADCASTRESPONSE' + MESSAGE_SEPARATOR + peerstr.encode()
        connection.send(msg)
    def handle_filelist(self, connection: socket.socket, message: bytes) -> None:
        """
        Handles the FILELIST message.
        FileList messages are used to request the file list.
        Response is a FILELISTRESPONSE message.
        """
        filestr = json.dumps(self.files)
        msg = b'FILELISTRESPONSE' + MESSAGE_SEPARATOR + self.uid.encode() + MESSAGE_SEPARATOR + filestr.encode()
        connection.send(msg)
    def manual_peer_add(self, ip: str, port: int) -> bool:
        # Send a ADDME message to the peer.
        # If the peer responds with ACK, add it to the known peers.
        clsck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clsck.settimeout(LISTENER_TIMEOUT)
        try:
            clsck.connect((ip, port))
            msg = b'ADDME' + MESSAGE_SEPARATOR + self.uid.encode() + MESSAGE_SEPARATOR + str(self.network_address[1]).encode()
            clsck.sendall(msg)
            rsp = b''
            data = clsck.recv(1024)
            if not data:
                pass
            rsp += data
            log(self._start, f'Received message: {rsp}')
            if rsp.split(MESSAGE_SEPARATOR)[0] == b'ACK':
                clsck.close()
                uid = rsp.split(MESSAGE_SEPARATOR)[1].decode()
                peer = Peer(uid, ip, port)
                self.add_known_peer(peer)
                return True
            elif rsp.split(MESSAGE_SEPARATOR)[0] == b'NACK':
                clsck.close()
                return False
            else:
                raise Exception('Invalid response.')
        except Exception as e:
            clsck.close()
            return False
    def broadcast_peer_discovery(self) -> None:
        """
        Broadcasts a peer discovery message to all known peers.
        If a peer responds with ACK, add it to the known peers.
        """
        known_peers = self.known_peers.copy()
        for peer in known_peers.values():
            clsck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clsck.settimeout(LISTENER_TIMEOUT)
            try:
                clsck.connect((peer.ip, peer.port))
                msg = b'BROADCASTREQUEST'
                clsck.sendall(msg)
                rsp = b''
                data = clsck.recv(1024)
                if not data:
                    pass
                rsp += data
                log(self._start, f'Received message: {rsp}')
                if rsp.split(MESSAGE_SEPARATOR)[0] == b'BROADCASTRESPONSE':
                    clsck.close()
                    peer_list = json.loads(rsp.split(MESSAGE_SEPARATOR)[1].decode())
                    for peer_data in peer_list:
                        if peer_data[0] not in self.known_peers:
                            self.manual_peer_add(peer_data[1], peer_data[2])
            except Exception as e:
                clsck.close()
                pass
    def list_files_on_network(self) -> dict:
        """
        Requests the file list from all known peers.
        """
        file_list = {}
        known_peers = self.known_peers.copy()
        for peer in known_peers.values():
            clsck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clsck.settimeout(LISTENER_TIMEOUT)
            try:
                clsck.connect((peer.ip, peer.port))
                msg = b'FILELIST'
                clsck.sendall(msg)
                rsp = b''
                data = clsck.recv(1024)
                if not data:
                    pass
                rsp += data
                log(self._start, f'Received message: {rsp}')
                if rsp.split(MESSAGE_SEPARATOR)[0] == b'FILELISTRESPONSE':
                    clsck.close()
                    peer_uid = rsp.split(MESSAGE_SEPARATOR)[1].decode()
                    peer_file_list = json.loads(rsp.split(MESSAGE_SEPARATOR)[2].decode())
                    file_list[peer_uid] = peer_file_list
            except Exception as e:
                clsck.close()
                pass
        return file_list
            
    def _fileupdate(self) -> None:
        while self._fileupdate_enabled == True:
            self.update_file_list()
            time.sleep(FILEUPDATE_TIMEOUT)
    def _peerupdate(self) -> None:
        while self._peerupdate_enabled == True:
            self.update_peer_list()
            time.sleep(PEERUPDATE_TIMEOUT)
    def update_peer_list(self) -> None:
        new_peers = {}
        self._knownpeers_lock.acquire()
        for peer in self.known_peers.values():
            if validate_address(peer.ip, peer.port) == True:
                new_peers[peer.uid] = peer
        self.known_peers = new_peers
        self._knownpeers_lock.release()
    def update_file_list(self) -> None:
        self._fileupdate_lock.acquire()
        self.files = get_files(self)
        self._fileupdate_lock.release()
    def set_file_dir(self, path: str) -> None:
        self._fileupdate_lock.acquire()
        self.file_dir = path
        self.files = get_files(self)
        self._fileupdate_lock.release()
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
                elif option == 4:
                    state = MenuState.PEERUPDATE
            elif state == MenuState.FILEMANAGEMENT:
                option = Menu.menu_filemanagement(self)
                if option == 0:
                    state = MenuState.MAIN
                elif option == 1:
                    state = MenuState.FILELISTLOCAL
                elif option == 2:
                    state = MenuState.FILELISTREMOTE
                elif option == 3:
                    state = MenuState.FILESEARCH
                elif option == 4:
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
            elif state == MenuState.FILELISTLOCAL:
                option = Menu.menu_listlocalfiles(self)
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
            elif state == MenuState.PEERUPDATE:
                option = Menu.menu_updatepeers(self)
                if option == 0:
                    state = MenuState.PEERMANAGEMENT
            elif state == MenuState.FILELISTREMOTE:
                option = Menu.menu_listremotefiles(self)
                if option == 0:
                    state = MenuState.FILEMANAGEMENT
            else:
                raise Exception('Invalid MenuState')