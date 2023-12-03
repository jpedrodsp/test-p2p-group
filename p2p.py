"""
This project aims to create a Peer-to-Peer (P2P) application in Python using sockets for the Computer Networks discipline. The application will allow connection between at least 5 devices, facilitating the exchange of files and checking the availability of desired files on the network.
"""

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
    
class Menu:
    @staticmethod
    def read_option(option_count: int = 0, has_zero: bool = False) -> int:
        while True:
            try:
                option = int(input('Digite a opção desejada: '))
                if has_zero and option == 0:
                    return option
                if option < 1 or option > option_count:
                    raise ValueError
                return option
            except ValueError:
                print('Opção inválida. Tente novamente.')
    @staticmethod
    def menu_main() -> int:
        print('1 - Gerenciamento de Pares')
        print('2 - Gerenciamento de Arquivos')
        print('0 - Sair')
        return Menu.read_option(2, True)
    @staticmethod
    def menu_peermanagement() -> int:
        print('1 - Listar Pares')
        print('2 - Adicionar Par')
        print('3 - Remover Par')
        print('0 - Voltar')
        return Menu.read_option(3, True)
    @staticmethod
    def menu_filemanagement() -> int:
        print('1 - Listar Arquivos')
        print('2 - Buscar Arquivo')
        print('3 - Definir Pasta de Arquivos')
        print('0 - Voltar')
        return Menu.read_option(3, True)
    

if __name__ == '__main__':
    app = Application()
    app.run()