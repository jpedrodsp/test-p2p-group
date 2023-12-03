from enum import Enum

class MenuState(Enum):
    MAIN = 0
    PEERMANAGEMENT = 1
    FILEMANAGEMENT = 2

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
        print('0 - Sair')
        return Menu.read_option(2, True)
    @staticmethod
    def menu_peermanagement(ctx: 'Application') -> int:
        print('1 - Listar Pares')
        print('2 - Adicionar Par')
        print('3 - Remover Par')
        print('0 - Voltar')
        return Menu.read_option(3, True)
    @staticmethod
    def menu_filemanagement(ctx: 'Application') -> int:
        print('1 - Listar Arquivos')
        print('2 - Buscar Arquivo')
        print('3 - Definir Pasta de Arquivos')
        print('0 - Voltar')
        return Menu.read_option(3, True)