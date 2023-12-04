from enum import Enum
import os

class MenuState(Enum):
    MAIN = 0
    PEERMANAGEMENT = 1
    FILEMANAGEMENT = 2
    PEERLIST = 3
    PEERADD = 4
    PEERREMOVE = 5
    FILELIST = 6
    FILESEARCH = 7
    FILESETDIR = 8
    PEERADDMANUAL = 9
    PEERADDDISCOVERY = 10
    SYSTEMINFO = 11
    PEERUPDATE = 12
    

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
    def menu_main(ctx: 'Application') -> int:
        print('1 - Gerenciamento de Pares')
        print('2 - Gerenciamento de Arquivos')
        print('3 - Informações do Sistema')
        print('0 - Sair')
        return Menu.read_option(3, True)
    @staticmethod
    def menu_peermanagement(ctx: 'Application') -> int:
        print('1 - Listar Pares')
        print('2 - Adicionar Par')
        print('3 - Remover Par')
        print('4 - Atualizar Pares')
        print('0 - Voltar')
        return Menu.read_option(4, True)
    @staticmethod
    def menu_filemanagement(ctx: 'Application') -> int:
        print('1 - Listar Arquivos')
        print('2 - Buscar Arquivo')
        print('3 - Definir Pasta de Arquivos')
        print('0 - Voltar')
        return Menu.read_option(3, True)
    @staticmethod
    def menu_addpeer(ctx: 'Application') -> int:
        print('1 - Adicionar Par Manualmente')
        print('2 - Adicionar Par via Descoberta')
        print('0 - Voltar')
        return Menu.read_option(2, True)
    @staticmethod
    def menu_removepeer(ctx: 'Application') -> int:
        print('Pares Conhecidos:')
        for peer in ctx.known_peers.values():
            print(f'\t{peer}')
        print('Digite o ID do par a ser removido:')
        remove_id = input()
        print('0 - Voltar')
        return Menu.read_option(1, True)
    @staticmethod
    def menu_listpeers(ctx: 'Application') -> int:
        print('Pares Conhecidos:')
        if len(ctx.known_peers) == 0:
            print('\tNenhum par conhecido.')
        else:
            for peer in ctx.known_peers.values():
                print(f'\t{peer}')
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_listfiles(ctx: 'Application') -> int:
        print('Arquivos Disponíveis:')
        if len(ctx.files) == 0:
            print('\tNenhum arquivo disponível.')
        else:
            for file in ctx.files:
                print(f'\t{file}')
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_searchfile(ctx: 'Application') -> int:
        print('Digite o nome do arquivo desejado:')
        filename = input()
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_setfiledir(ctx: 'Application') -> int:
        skip = False
        print('Digite o caminho da pasta de arquivos:')
        print(f'Pasta atual: {ctx.file_dir}')
        path = input(f'Nova pasta: ')
        if path == '':
            print('Operação cancelada.')
            skip = True
        if skip != True:
            if os.path.exists(path) == False:
                print('Pasta não encontrada. Tente novamente.')
                skip = True
            else:
                path = os.path.abspath(path)
                ctx.set_file_dir(path)
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_addpeer_manual(ctx: 'Application') -> int:
        peer_ip: str = ''
        peer_port: int = 0
        skip = False
        if skip != True:
            while True:
                print('Digite o IP do par:')
                peer_ip = input()
                if peer_ip == '':
                    skip = True
                    break
                break
        if skip != True:
            while True:
                print('Digite a porta do par:')
                peer_port = input()
                if peer_port == '':
                    skip = True
                    break
                if peer_port.isnumeric() == False:
                    print('Porta inválida. Tente novamente.')
                    continue
                peer_port = int(peer_port)
                break
        
        if skip != True:
            res = ctx.manual_peer_add(peer_ip, peer_port)
            if res == True:
                print('Par adicionado com sucesso.')
            else:
                print('Erro ao adicionar par.')
        
        if skip == True:
            print('Operação cancelada.')
        
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_addpeer_discovery(ctx: 'Application') -> int:
        print('Realizando descoberta de pares...')
        discovered_peer_count: int = 0
        print(f'{discovered_peer_count} par(es) descobertos.')
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_systeminfo(ctx: 'Application') -> int:
        print('Informações do Sistema:')
        print(f'\tID: {ctx.uid}')
        print(f'\tIP: {ctx.friendly_network_host}')
        print(f'\tPorta: {ctx.network_address[1]}')
        print(f'\tPares Conhecidos: {len(ctx.known_peers)}')
        print(f'\tArquivos Disponíveis: {len(ctx.files)}')
        print('0 - Voltar')
        return Menu.read_option(0, True)
    @staticmethod
    def menu_updatepeers(ctx: 'Application') -> int:
        print('Atualizando pares...')
        ctx.update_peer_list()
        print('Pares atualizados.')
        print('0 - Voltar')
        return Menu.read_option(0, True)
