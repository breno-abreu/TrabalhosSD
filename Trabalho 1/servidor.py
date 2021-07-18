from requisicao import Requisicao
import threading

# Importa a classe Pyro4 para possibilitar o acesso a objetos remotos
import Pyro4

# Importa as classes do projeto PyCryptodome para realizar a assinatura digital
# de uma mensagem
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15 as pk

# Variáveis globias que permitem armazenar listas de usuários
# e requisições de caronas. Não foi possível utilizá-las dentro da classe
# 'Servidor' pois, por alguma razão, acabavam sendo resetadas a cada nova requisição
usuarios = []
caronas_pedidas = []
caronas_oferecidas = []
cont = 0


class Servidor(object):
    """ Classe para o servidor do sistema que irá proporcionar métodos
        que podem ser acessados remotamente por clientes.
        Popula as listas com usuários e requisições """

    def validar_assinatura(self, nome, mensagem, assinatura):
        """ Ao receber uma mensagem e uma assinatura, valida a mensagem
            utilizando a chave pública de um usuário """

        # Cria o hash de uma mensagem utilizando o algoritmo SHA256
        mensagem_hash = SHA256.new(mensagem.encode())

        # Localiza o usuário referente à mensagem recebida
        usuario = self.get_usuario(nome)

        # Faz o casting da assinatura que está em string para bytes
        # O enconding 'latin1' foi utilizado pois o 'utf-8' não funcionou
        # para a assinatura digital
        assinatura = bytes(assinatura, 'latin1')

        try:
            # Verifica se a mensagem é válida utilizando seu hash,
            # a assinatura recebida e a chave pública do usuário que a enviou
            pk.new(usuario["chave"]).verify(mensagem_hash, assinatura)
            return True
        except:
            return False
        

    @Pyro4.expose
    def cadastrar_usuario(self, nome, usuario, chave):
        """ Cadastra um novo usuário adicionando-o à lista global """

        # Faz o casting da chave pública recebida de string para bytes
        chave_publica = bytes(chave, 'utf-8')

        # Cria um novo objeto RSA que contém a chave pública
        chave_publica = RSA.import_key(chave_publica)

        # Popula um dicionário com as informações recebidas e inclue-o na lista
        novo = {"nome":nome, "referencia":usuario, "chave":chave_publica}
        global usuarios
        usuarios.append(novo)
        print("[SUCESSO] Novo usuário registrado! Nome: {0}".format(nome))
        print("[INFO] {0} usuários cadastrados".format(len(usuarios)))


    @Pyro4.expose
    def registrar_interesse_pedido(self, mensagem, assinatura):
        """ Registra um pedido de interesse em receber uma carona """

        global cont
        global caronas_pedidas

        # Separa a mensagem recebida em variáveis e adiciona-as em uma lista
        variaveis = mensagem.split(',')

        # Verifica se a mensagem recebida é válida através da assinatura recebida
        if(self.validar_assinatura(variaveis[0], mensagem, assinatura)):
            cont += 1

            # Cria uma nova requisição e inclue-a em uma lista
            requisicao = Requisicao(cont, variaveis[0], variaveis[1], 
                                    variaveis[2], variaveis[3], variaveis[4])
            caronas_pedidas.append(requisicao)

            # Procura se já há algum usuário ofertando uma carona que está
            # de acordo com a requisição recebida
            self.procurar_ofertas(requisicao)

            print("[SUCESSO] Novo registro de interesse de pedido criado!")

            # Retorna o ID da requisição
            return cont
        
        else:
            print("[ERRO] Assinatura digital é inválida!")


    @Pyro4.expose
    def registrar_interesse_oferta(self, mensagem, assinatura):
        """ Registra um pedido de interesse em oferecer uma carona """

        global cont
        global caronas_oferecidas

        # Separa a mensagem recebida em variáveis e adiciona-as em uma lista
        variaveis = mensagem.split(',')

        # Verifica se a mensagem recebida é válida através da assinatura recebida
        if(self.validar_assinatura(variaveis[0], mensagem, assinatura)):
            cont += 1

            # Cria uma nova requisição e inclue-a em uma lista
            requisicao = Requisicao(cont, variaveis[0], variaveis[1], variaveis[2], 
                                    variaveis[3], variaveis[4], variaveis[5])
            caronas_oferecidas.append(requisicao)

            # Procura se já há algum usuário interessado em receber uma carona que está
            # de acordo com a requisição recebida
            self.procurar_pedidos(requisicao)

            print("[SUCESSO] Novo registro de interesse de oferta criado!")

            # Retorna o ID da requisição
            return cont
        
        else:
            print("[ERRO] Assinatura digital é inválida!")



    @Pyro4.expose
    def cancelar_pedido(self, id_req):
        """ Cancela uma requisição de pedido """

        global caronas_pedidas
        for carona in caronas_pedidas:
            if carona.id_req == id_req:

                # Encontra a requisição que possui o id recebido e a retira da lista
                caronas_pedidas.remove(carona)

                print("[SUCESSO] Carona com ID: {0} cancelada".format(id_req))
                return
        
        print("[ERRO] ID de registro de carona não encontrado!")
           

    @Pyro4.expose          
    def cancelar_oferta(self, id_req):
        """ Cancela uma requisição de oferta """

        global caronas_oferecidas
        for carona in caronas_oferecidas:
            if carona.id_req == id_req:

                # Encontra a requisição que possui o id recebido e a retira da lista
                caronas_oferecidas.remove(carona)

                print("[SUCESSO] Carona com ID: {0} cancelada".format(id_req))
                return
        
        print("[ERRO] ID de registro de carona não encontrado!")
    

    def procurar_pedidos(self, oferta):
        """ Procura uma requisição de pedido que esteja de acordo com uma oferta """

        # Encontra o usuário que realizou a oferta
        usr_o = self.get_usuario(oferta.nome)
        usr_p = None
        global caronas_pedidas

        for pedido in caronas_pedidas:
            if(pedido.origem == oferta.origem and
               pedido.destino == oferta.destino and
               pedido.data == oferta.data):

                # Caso haja um pedido que bate com uma oferta, 
                # encontra o usuário que realizou o pedido
                usr_p = self.get_usuario(pedido.nome)

                # Notifica o usuário que realizou a oferta e o usuário que
                # realizou o pedido sobre as informações um do outro
                if(usr_o["nome"] != usr_p["nome"]):
                    to = threading.Thread(self.notificar_pedido(usr_o["referencia"], pedido))
                    tp = threading.Thread(self.notificar_oferta(usr_p["referencia"], oferta))

                    to.start()
                    tp.start()


    def procurar_ofertas(self, pedido):
        """ Procura uma requisição de oferta que esteja de acordo com um pedido """

        # Encontra o usuário que realizou o pedido
        usr_p = self.get_usuario(pedido.nome)
        usr_o = None
        global caronas_oferecidas

        for oferta in caronas_oferecidas:
            if(oferta.origem == pedido.origem and
               oferta.destino == pedido.destino and
               oferta.data == pedido.data):

                # Caso haja uma oferta que bate com um pedido, 
                # encontra o usuário que realizou a oferta
                usr_o = self.get_usuario(oferta.nome)

                # Notifica o usuário que realizou a oferta e o usuário que
                # realizou o pedido sobre as informações um do outro
                if(usr_o["nome"] != usr_p["nome"]):
                    to = threading.Thread(self.notificar_pedido(usr_o["referencia"], pedido))
                    tp = threading.Thread(self.notificar_oferta(usr_p["referencia"], oferta))

                    to.start()
                    tp.start()


    def get_usuario(self, nome):
        """ Retorna o registro de um usuário através de seu nome """

        global usuarios
        for usuario in usuarios:
            if usuario["nome"] == nome:
                return usuario
        
        return None

    @Pyro4.expose
    @Pyro4.oneway
    def notificar_pedido(self, usuario, requisicao):
        """ Notifica um usuário sobre as informações de outro usuário
            interessado em pedir uma carona """

        try:
            usuario.notificar_pedido(requisicao.nome, 
                                     requisicao.telefone, 
                                     requisicao.origem, 
                                     requisicao.destino, 
                                     requisicao.data)
        
        except Exception as ex:
            print("[ERRO] Não foi possível enviar a notificação ao cliente")
            print("[EXCEPTION] " + str(ex)) 


    @Pyro4.expose
    @Pyro4.oneway
    def notificar_oferta(self, usuario, requisicao):
        """ Notifica um usuário sobre as informações de outro usuário
            interessado em ofertar uma carona """

        try:
            usuario.notificar_oferta(requisicao.nome, 
                                     requisicao.telefone, 
                                     requisicao.origem, 
                                     requisicao.destino, 
                                     requisicao.data)
        
        except Exception as ex:
            print("[ERRO] Não foi possível enviar a notificação ao cliente")
            print("[EXCEPTION] " + str(ex))


def main():
    # Registra a classe 'Servidor' no name server com o nome 'servidor'.
    # Inicia seu loop de requisições
    Pyro4.Daemon.serveSimple({Servidor: "servidor"})

if __name__ == "__main__":
    main()