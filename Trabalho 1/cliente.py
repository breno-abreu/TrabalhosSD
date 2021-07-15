import Pyro4
from usuario import Usuario
import threading

def main():
    """ Executa o menu de escolhas para um usuário """

    daemon = Pyro4.Daemon()
    usuario = Usuario()

    # Registra um objeto no Daemon criado pelo Pyro4
    daemon.register(usuario)

    # Cria uma thread para executar o loop de requisição do cliente
    t = threading.Thread(target=daemon.requestLoop)
    t.start()

    menu = "( 1 ) :: Cadastrar usuário\n"
    menu += "( 2 ) :: Requisitar carona\n"
    menu += "( 3 ) :: Cancelar carona\n"
    menu += "( 4 ) :: Mostrar ids das requisições\n"
    menu += "( 0 ) :: Sair"

    try:
        while True:
            print(menu)
            opcao = input("Escolha uma opção: ")
            if opcao == '0':
                break
            elif opcao == '1':
                usuario.cadastrar_usuario()
            elif opcao == '2':
                usuario.requisitar_carona()
            elif opcao == '3':
                usuario.cancelar_carona()
            elif opcao == '4':
                usuario.mostrar_ids()
            else:
                print("[ERRO] Opção inválida")

    except KeyboardInterrupt:
        print("[SAINDO] Desligando programa!")


if __name__ == "__main__":
    main()