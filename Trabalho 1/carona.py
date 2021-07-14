from usuario import Usuario
from servidor import Servidor

def main():
    servidor = Servidor()

    usuario = Usuario(servidor)
    usuario2 = Usuario(servidor)

    usuario.requerir_carona()
    usuario2.requerir_carona()

if __name__ == "__main__":
    main()