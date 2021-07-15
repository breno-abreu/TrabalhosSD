import Pyro4
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15 as pk

class Usuario(object):
    def __init__(self):
        self.nome = None
        self.telefone = None
        self.ids_pedidos = []
        self.ids_ofertas = []

        self.par_chaves = None
        self.chave_publica = None
        self.gerar_chaves()

    def gerar_chaves(self):
        random_seed = Random.new().read
        self.par_chaves = RSA.generate(1024, random_seed)
        self.chave_publica = self.par_chaves.publickey()


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
        chave = self.chave_publica.export_key()
        chave = chave.decode('utf-8')
        
        with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
            servidor.cadastrar_usuario(self.nome, self, chave)


    def requisitar_carona(self):
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

        
        with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
            id_req = servidor.registrar_interesse_pedido(self.nome, 
                                                         self.telefone, 
                                                         origem, 
                                                         destino, 
                                                         data)

        self.ids_pedidos.append(id_req)
        print(id_req)

    
    def registrar_oferta(self):
        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")
        n_passageiros = self.get_variavel("Número de Passageiros")

        with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
            id_req = servidor.registrar_interesse_oferta(self.nome, 
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
            with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                servidor.cancelar_pedido(id_req)

            self.ids_pedidos.remove(id_req)
        else:
            print("[ERRO] ID de registro de carona não existente!")


    def cancelar_oferta(self, id_requisicao):
        id_req = int(id_requisicao)
        if id_req in self.ids_ofertas:
            with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                servidor.cancelar_oferta(id_req)

            self.ids_ofertas.remove(id_req)
        else:
            print("[ERRO] ID de registro de carona não existente!")


    @Pyro4.expose
    @Pyro4.callback
    #trocar os argumentos por uma simples linha de texto
    def notificar_oferta(self, nome, telefone, origem, destino, data):
        print("[NOTIFICAÇÃO] O usuário {0} está interessado em te oferecer carona!".format(nome))
        print("""Informações:\nTelefone do usuário: {0}\nOrigem: {1}\nDestino: {2}\nData: {3}""".format(telefone, origem, destino, data))


    @Pyro4.expose
    @Pyro4.callback
    #trocar os argumentos por uma simples linha de texto
    def notificar_pedido(self, nome, telefone, origem, destino, data):
        print("[NOTIFICAÇÃO] O usuário {0} está interessado em sua carona!".format(nome))
        print("""Informações:\nTelefone do usuário: {0}\nOrigem: {1}\nDestino: {2}\nData: {3}""".format(telefone, origem, destino, data))