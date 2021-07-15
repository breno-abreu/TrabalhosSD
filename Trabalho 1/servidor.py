from requisicao import Requisicao
import Pyro4
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15 as pk

usuarios = []
caronas_pedidas = []
caronas_oferecidas = []
cont = 0


class Servidor(object):
    def __init__(self):
        #criar nova classse para essas iunformações, guardá-las fora do servidor
        self.j = 3
        

    @Pyro4.expose
    def cadastrar_usuario(self, nome, usuario, chave):
        chave_publica = bytes(chave, 'utf-8')
        chave_publica = RSA.import_key(chave_publica)
        novo = {"nome":nome, "referencia":usuario, "chave":chave_publica}
        global usuarios
        usuarios.append(novo)
        print("[SUCESSO] Novo usuário registrado! Nome: {0}".format(nome))


    @Pyro4.expose
    def registrar_interesse_pedido(self, nome, telefone, origem, destino, data):
        global cont
        global caronas_pedidas
        cont += 1
        requisicao = Requisicao(cont, nome, telefone, origem, destino, data)
        caronas_pedidas.append(requisicao)
        self.procurar_ofertas(requisicao)
        print("[SUCESSO] Novo registro de interesse de pedido criado!")
        return cont


    @Pyro4.expose
    def registrar_interesse_oferta(self, nome, telefone, origem, destino, data, n_passageiros):
        global cont
        global caronas_oferecidas
        cont += 1
        requisicao = Requisicao(cont, nome, telefone, origem, destino, data, n_passageiros)
        caronas_oferecidas.append(requisicao)
        self.procurar_pedidos(requisicao)
        print("[SUCESSO] Novo registro de interesse de oferta criado!")
        return cont


    @Pyro4.expose
    def cancelar_pedido(self, id_req):
        global caronas_pedidas
        for carona in caronas_pedidas:
            if carona.id_req == id_req:
                caronas_pedidas.remove(carona)
                print("[SUCESSO] Carona com ID: {0} cancelada".format(id_req))
                return
        
        print("[ERRO] ID de registro de carona não encontrado!")
           

    @Pyro4.expose          
    def cancelar_oferta(self, id_req):
        global caronas_oferecidas
        for carona in caronas_oferecidas:
            if carona.id_req == id_req:
                caronas_oferecidas.remove(carona)
                print("[SUCESSO] Carona com ID: {0} cancelada".format(id_req))
                return
        
        print("[ERRO] ID de registro de carona não encontrado!")
    

    def procurar_pedidos(self, oferta):
        usr_o = self.get_usuario(oferta.nome)
        usr_p = None
        global caronas_pedidas

        for pedido in caronas_pedidas:
            if(pedido.origem == oferta.origem and
               pedido.destino == oferta.destino and
               pedido.data == oferta.data):

                usr_p = self.get_usuario(pedido.nome)
                self.notificar_pedido(usr_o["referencia"], pedido)
                self.notificar_oferta(usr_p["referencia"], oferta)


    def procurar_ofertas(self, pedido):
        usr_p = self.get_usuario(pedido.nome)
        usr_o = None
        global caronas_oferecidas

        for oferta in caronas_oferecidas:
            if(oferta.origem == pedido.origem and
               oferta.destino == pedido.destino and
               oferta.data == pedido.data):

                usr_o = self.get_usuario(oferta.nome)
                self.notificar_oferta(usr_p["referencia"], oferta)
                self.notificar_pedido(usr_o["referencia"], pedido)


    def get_usuario(self, nome):
        global usuarios
        for usuario in usuarios:
            if usuario["nome"] == nome:
                return usuario
        
        return None

    
    @Pyro4.expose
    @Pyro4.oneway
    def notificar_pedido(self, usuario, requisicao):
        usuario.notificar_pedido(requisicao.nome, 
                                 requisicao.telefone, 
                                 requisicao.origem, 
                                 requisicao.destino, 
                                 requisicao.data)


    @Pyro4.expose
    @Pyro4.oneway
    def notificar_oferta(self, usuario, requisicao):
        usuario.notificar_oferta(requisicao.nome, 
                                 requisicao.telefone, 
                                 requisicao.origem, 
                                 requisicao.destino, 
                                 requisicao.data)


def main():
    Pyro4.Daemon.serveSimple({Servidor: "servidor"})


if __name__ == "__main__":
    main()