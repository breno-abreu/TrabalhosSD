import servidor

class Usuario(object):
    def __init__(self):
        self.nome = None
        self.telefone = None
        self.ids_receber_carona = []
        self.ids_oferecer_carona = []
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
        servidor.cadastrar_usuario(self.nome, self.telefone)


    def consultar_carona(self):
        while True:
            print("Escolha uma opção:\n( 1 ) - Receber carona\n( 2 ) - Oferecer carona")
            opcao = input("Opção: ")
            if(opcao != 1 and opcao != 2):
                print("[ERRO] Opção inválida!")
                continue
            else:
                break
        
        if opcao == 1:
            self.registrar_receber_carona()
        else:
            self.registrar_oferecer_carona()


    def registrar_receber_carona(self):
        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")

        #Pyro4 - chave pública
        id_pedido = servidor.registrar_interesse_receber_carona(self.nome, 
                                                                self.telefone, 
                                                                origem, 
                                                                destino, 
                                                                data)

        self.ids_receber_carona.append = id_pedido

    
    def registrar_oferecer_carona(self):
        origem = self.get_variavel("Origem")
        destino = self.get_variavel("Destino")
        data = self.get_variavel("Data")
        n_passageiros = self.get_variavel("Número de Passageiros")

        #Pyro4 - chave pública
        id_pedido = servidor.registrar_interesse_oferecer_carona(self.nome, 
                                                            self.telefone, 
                                                            origem, 
                                                            destino, 
                                                            data)

        self.ids_oferecer_carona.append = id_pedido
        

    def cancelar_viagem(self):
        id_viagem = self.get_variavel("ID da Viagem")

        while True:
            print("Escolha uma opção:\n( 1 ) - Cancelar - receber carona\n( 2 ) - Cancelar - oferecer carona")
            opcao = input("Opção: ")
            if(opcao != 1 and opcao != 2):
                print("[ERRO] Opção inválida!")
                continue
            else:
                break
        
        if opcao == 1:
            self.cancelar_receber_carona(id_viagem)
        else:
            self.cancelar_oferecer_carona(id_viagem)


    def cancelar_receber_carona(self, id):
        if id in self.ids_receber_carona:
            #Pyro4 - chave pública
            servidor.cancelar_receber_carona(id)
            self.ids_receber_carona.remove(id)
        else:
            print("[ERRO] ID de registro de carona não existente!")


    def cancelar_oferecer_carona(self, id):
        if id in self.ids_oferecer_carona:
            #Pyro4 - chave pública
            servidor.cancelar_oferecer_carona(id)
            self.ids_oferecer_carona.remove(id)
        else:
            print("[ERRO] ID de registro de carona não existente!")

    
    def notificar_receber_carona(self, nome, telefone, origem, destino, data):
        print("[NOTIFICAÇÃO] O usuário {0} te oferecerá carona!".format(nome))
        print("""Informações:\nTelefone do usuário: {0}\nOrigem: {1}\n
                 Destino: {2}\nData: {3}""".format(telefone, origem, destino, data))


    def notificar_oferecer_carona(self, nome, telefone, origem, destino, data):
        print("[NOTIFICAÇÃO] O usuário {0} receberá sua carona!".format(nome))
        print("""Informações:\nTelefone do usuário: {0}\nOrigem: {1}\n
                 Destino: {2}\nData: {3}""".format(telefone, origem, destino, data))

        
def main():
    us = Usuario()

if __name__ == "__main__":
    main()