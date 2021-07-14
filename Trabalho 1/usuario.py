from servidor import Servidor

class Usuario(object):
    def __init__(self, servidor):
        self.nome = None
        self.telefone = None
        self.ids_pedidos = []
        self.ids_ofertas = []

        #AUX
        self.servidor = servidor

        self.cadastrar_usuario()


    def get_variavel(self, nome):
        variavel = ''

        while True:
            variavel = input("{0}: ".format(nome))
            if(len(variavel) == 0):
                print("[ERRO] Campo \'{0}\' é obrigatório!".format(nome))
                continue
            else:
                break
        
        return variavel


    def cadastrar_usuario(self):

        self.nome = self.get_variavel("Nome")
        self.telefone = self.get_variavel("Telefone")
        
        #Pyro4 - chave pública
        self.servidor.cadastrar_usuario(self)


    def requerir_carona(self):
        while True:
            print("Escolha uma opção:\n( 1 ) - Pedir carona\n( 2 ) - Oferecer carona")
            opcao = input("Opção: ")
            if(opcao != '1' and opcao != '2'):
                print("[ERRO] Opção inválida!")
                continue
            else:
                break
        
        if opcao == '1':
            self.registrar_pedido()
        else:
            self.registrar_oferta()


    def registrar_pedido(self):
        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")

        #Pyro4 - chave pública
        id_req = self.servidor.registrar_interesse_pedido(self.nome, 
                                                          self.telefone, 
                                                          origem, 
                                                          destino, 
                                                          data)

        self.ids_pedidos.append(id_req)

    
    def registrar_oferta(self):
        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")
        n_passageiros = self.get_variavel("Número de Passageiros")

        #Pyro4 - chave pública
        id_req = self.servidor.registrar_interesse_oferta(self.nome, 
                                                          self.telefone, 
                                                          origem, 
                                                          destino, 
                                                          data,
                                                          n_passageiros)

        self.ids_ofertas.append(id_req)
        

    def cancelar_carona(self):
        while True:
            print("Escolha uma opção:\n( 1 ) - Cancelar Pedido\n( 2 ) - Cancelar Oferta")
            opcao = input("Opção: ")
            if(opcao != '1' and opcao != '2'):
                print("[ERRO] Opção inválida!")
                continue
            else:
                break

        id_viagem = self.get_variavel("ID da Requisição")
        
        if opcao == '1':
            self.cancelar_pedido(id_viagem)
        else:
            self.cancelar_oferta(id_viagem)


    def cancelar_pedido(self, id_requisicao):
        id_req = int(id_requisicao)
        if id_req in self.ids_pedidos:
            #Pyro4 - chave pública
            self.servidor.cancelar_pedido(id_req)
            self.ids_pedidos.remove(id_req)
        else:
            print("[ERRO] ID de registro de carona não existente!")


    def cancelar_oferta(self, id_requisicao):
        id_req = int(id_requisicao)
        if id_req in self.ids_ofertas:
            #Pyro4 - chave pública
            self.servidor.cancelar_oferta(id_req)
            self.ids_ofertas.remove(id_req)
        else:
            print("[ERRO] ID de registro de carona não existente!")


    #Pyro4 
    def notificar_oferta(self, nome, telefone, origem, destino, data):
        print("[NOTIFICAÇÃO] O usuário {0} está interessado em te oferecer carona!".format(nome))
        print("""Informações:\nTelefone do usuário: {0}\nOrigem: {1}\nDestino: {2}\nData: {3}""".format(telefone, origem, destino, data))


    #Pyro4 
    def notificar_pedido(self, nome, telefone, origem, destino, data):
        print("[NOTIFICAÇÃO] O usuário {0} está interessado em sua carona!".format(nome))
        print("""Informações:\nTelefone do usuário: {0}\nOrigem: {1}\nDestino: {2}\nData: {3}""".format(telefone, origem, destino, data))