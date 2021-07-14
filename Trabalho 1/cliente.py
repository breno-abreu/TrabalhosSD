import Pyro4
from usuario import Usuario
import threading


def main():
    daemon = Pyro4.Daemon()
    usuario = Usuario()
    daemon.register(usuario)

    usuario2 = Usuario()
    daemon.register(usuario2)

    t = threading.Thread(target=daemon.requestLoop)
    t.start()

    usuario.cadastrar_usuario()
    usuario2.cadastrar_usuario()
    usuario.requisitar_carona()
    usuario2.requisitar_carona()
    


if __name__ == "__main__":
    main()