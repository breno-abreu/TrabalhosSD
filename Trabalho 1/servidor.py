from requisicao import Requisicao

class Servidor(object):
    def __init__(self):
        self.usuarios = []
        self.caronas_pedidas = []
        self.caronas_oferecidas = []
        self.cont = 0
        

    def cadastrar_usuario(self, usuario):
        self.usuarios.append(usuario)


    def registrar_interesse_pedido(self, nome, telefone, origem, destino, data):
        self.cont += 1
        requisicao = Requisicao(self.cont, nome, telefone, origem, destino, data)
        self.caronas_pedidas.append(requisicao)
        self.procurar_ofertas(requisicao)
        return self.cont


    def registrar_interesse_oferta(self, nome, telefone, origem, destino, data, n_passageiros):
        self.cont += 1
        requisicao = Requisicao(self.cont, nome, telefone, origem, destino, data, n_passageiros)
        self.caronas_oferecidas.append(requisicao)
        self.procurar_pedidos(requisicao)
        return self.cont


    def cancelar_pedido(self, id_req):
        for carona in self.caronas_pedidas:
            if carona.id_req == id_req:
                self.caronas_pedidas.remove(carona)
                return
        
        print("[ERRO] ID de registro de carona não encontrado!")
           
                
    def cancelar_oferta(self, id_req):
        for carona in self.caronas_oferecidas:
            if carona.id_req == id_req:
                self.caronas_oferecidas.remove(carona)
                return
        
        print("[ERRO] ID de registro de carona não encontrado!")
    

    def procurar_pedidos(self, oferta):
        usr_o = self.get_usuario(oferta.nome)
        usr_p = None

        for pedido in self.caronas_pedidas:
            if(pedido.origem == oferta.origem and
               pedido.destino == oferta.destino and
               pedido.data == oferta.data):

                usr_p = self.get_usuario(pedido.nome)

                usr_o.notificar_pedido(pedido.nome, 
                                       pedido.telefone, 
                                       pedido.origem, 
                                       pedido.destino, 
                                       pedido.data)

                usr_p.notificar_oferta(oferta.nome, 
                                       oferta.telefone, 
                                       oferta.origem, 
                                       oferta.destino, 
                                       oferta.data)


    def procurar_ofertas(self, pedido):
        usr_p = self.get_usuario(pedido.nome)
        usr_o = None

        for oferta in self.caronas_oferecidas:
            if(oferta.origem == pedido.origem and
               oferta.destino == pedido.destino and
               oferta.data == pedido.data):

                usr_o = self.get_usuario(oferta.nome)

                usr_p.notificar_oferta(oferta.nome, 
                                       oferta.telefone, 
                                       oferta.origem, 
                                       oferta.destino, 
                                       oferta.data)

                usr_o.notificar_pedido(pedido.nome, 
                                       pedido.telefone, 
                                       pedido.origem, 
                                       pedido.destino, 
                                       pedido.data)

    def get_usuario(self, nome):
        for usuario in self.usuarios:
            if usuario.nome == nome:
                return usuario
        
        return None