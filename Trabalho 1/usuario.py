# Importa a classe Pyro4 para possibilitar o acesso a objetos remotos
import Pyro4

# Importa as classes do projeto PyCryptodome para realizar a assinatura digital
# de uma mensagem
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15 as pk

class Usuario(object):
    """ Classe para um usuário que acessará métodos remotos no servidor """

    def __init__(self):
        self.nome = None
        self.telefone = None

        # IDs dos pedidos e ofertas de carona efetuadas
        self.ids_pedidos = []
        self.ids_ofertas = []

        # Cria as chaves necessárias para assinar uma mensagem
        self.par_chaves = None
        self.chave_publica = None
        self.gerar_chaves()

    def gerar_chaves(self):
        """ Gera a chave privada e pública do usuário utilizando o RSA """

        random_seed = Random.new().read
        self.par_chaves = RSA.generate(1024, random_seed)
        self.chave_publica = self.par_chaves.publickey()

    
    def get_assinatura(self, mensagem):
        """ Cria uma assinatura de uma mensagem utilizando a chave privada
            de um usuário """

        # Cria o hash da mensagem utilizando o algoritmo SHA256
        mensagem_hash = SHA256.new(mensagem.encode())

        # Cria a assinatura utilizando o hash da mensagem e sua chave privada
        assinatura = pk.new(self.par_chaves).sign(mensagem_hash)
        return assinatura


    def get_variavel(self, nome):
        """ Executa uma rotina que demanda que o usuário escreva um valor válido
            para uma variável intitulada com um nome recebido """

        variavel = ''

        while True:
            variavel = input("{0}: ".format(nome))

            # Verifica se a variável recebida não está vazia
            if(len(variavel) == 0):
                print("[ERRO] Campo \'{0}\' é obrigatório!".format(nome))
                continue
            else:
                break
        
        # Retorna a variável escrita pelo usuário
        return variavel


    def cadastrar_usuario(self):
        """ Cadastra um novo usuário enviando ao servidor seu nome, telefone
            e sua chave pública """

        self.nome = self.get_variavel("Nome")
        self.telefone = self.get_variavel("Telefone")

        # Exporta uma chave pública para o tipo bytes
        chave = self.chave_publica.export_key()

        # Faz o casting de uma chave para string
        chave = chave.decode('utf-8')
        
        try:
            # Tenta executar o método presente no servidor remotamente
            with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                servidor.cadastrar_usuario(self.nome, self, chave)

        except Exception as ex:
            print("[ERRO] Não foi possível se conectar ao servidor")
            print("[EXCEPTION] " + str(ex)) 


    def requisitar_carona(self):
        """ Mostra um menu de requisição de carona para o usuário e
            executa o método equivalente à sua escolha """

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
        """ Registra uma requisição de pedido de carona enviando ao servidor
            o nome e telefone do usuário e a origem, destino e data da carona """

        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")

        # Junta as variáveis em uma única string
        mensagem = self.nome + ',' + self.telefone + ',' + origem
        mensagem += ',' + destino + ',' + data

        # Cria a assinatura da mensagem 
        assinatura = self.get_assinatura(mensagem)
        assinatura = assinatura.decode('latin1')
        
        try:
            # Tenta executar o método presente no servidor remotamente
            with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                id_req = servidor.registrar_interesse_pedido(mensagem, assinatura)
                self.ids_pedidos.append(id_req)

        except Exception as ex:
            print("[ERRO] Não foi possível se conectar ao servidor")
            print("[EXCEPTION] " + str(ex)) 

        
    def registrar_oferta(self):
        """ Registra uma requisição de oferta de carona enviando ao servidor
            o nome e telefone do usuário e a origem, destino, data
            e número de passageiros da carona """

        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")
        n_passageiros = self.get_variavel("Número de Passageiros")

        # Junta as variáveis em uma única string
        mensagem = self.nome + ',' + self.telefone + ',' + origem
        mensagem += ',' + destino + ',' + data + ',' + n_passageiros

        # Cria a assinatura da mensagem
        assinatura = self.get_assinatura(mensagem)
        assinatura = assinatura.decode('latin1')

        try:
            # Tenta executar o método presente no servidor remotamente
            with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                id_req = servidor.registrar_interesse_oferta(mensagem, assinatura)
                self.ids_ofertas.append(id_req)

        except Exception as ex:
            print("[ERRO] Não foi possível se conectar ao servidor")
            print("[EXCEPTION] " + str(ex))
        

    def cancelar_carona(self):
        """ Mostra o menu de cancelamente de requisição para o usuário
            e executa seu método equivalente """

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
        """ Cancela uma requisição de pedido executando um método no
            servidor enviando o id de um pedido """

        id_req = int(id_requisicao)
        if id_req in self.ids_pedidos:
            try:
                # Tenta executar o método presente no servidor remotamente
                with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                    servidor.cancelar_pedido(id_req)
                    self.ids_pedidos.remove(id_req)

            except Exception as ex:
                print("[ERRO] Não foi possível se conectar ao servidor")
                print("[EXCEPTION] " + str(ex)) 
        else:
            print("[ERRO] ID de registro de carona não existente!")


    def cancelar_oferta(self, id_requisicao):
        """ Cancela uma requisição de pedido executando um método no
            servidor enviando o id de uma oferta """

        id_req = int(id_requisicao)
        if id_req in self.ids_ofertas:
            try:
                # Tenta executar o método presente no servidor remotamente
                with Pyro4.core.Proxy("PYRONAME:servidor") as servidor:
                    servidor.cancelar_oferta(id_req)
                    self.ids_ofertas.remove(id_req)

            except Exception as ex:
                print("[ERRO] Não foi possível se conectar ao servidor")
                print("[EXCEPTION] " + str(ex)) 
        else:
            print("[ERRO] ID de registro de carona não existente!")


    def mostrar_ids(self):
        """ Mostra para o usuário todos os ids de pedidos e ofertas registrados """

        print("IDs de pedidos: ")
        print(self.ids_pedidos)
        print("\nIDs de ofertas: ")
        print(self.ids_ofertas)


    @Pyro4.expose
    @Pyro4.callback
    def notificar_oferta(self, nome, telefone, origem, destino, data):
        """ Método executado remotamente pelo servidor para notificar
            um usuário que realizou um pedido a respeito de uma oferta
            mostrando as informações do usuário ofertante """

        print("\n[NOTIFICAÇÃO] O usuário {0} está interessado em te oferecer carona!".format(nome))
        print("\tInformações:\n\tNome do usuário: {0}\n\tTelefone: {1}".format(nome, telefone))
        print("\tOrigem: {0}\n\tDestino: {1}\n\tData: {2}".format(origem, destino, data))


    @Pyro4.expose
    @Pyro4.callback
    def notificar_pedido(self, nome, telefone, origem, destino, data):
        """ Método executado remotamente pelo servidor para notificar
            um usuário que realizou uma oferta a respeito de um pedido
            mostrando as informações do usuário pedinte """

        print("\n[NOTIFICAÇÃO] O usuário {0} está interessado em sua carona!".format(nome))
        print("\tInformações:\n\tNome do usuário: {0}\n\tTelefone: {1}".format(nome, telefone))
        print("\tOrigem: {0}\n\tDestino: {1}\n\tData: {2}".format(origem, destino, data))