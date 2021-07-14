class Requisicao:
    def __init__(self, id_req, nome, telefone, origem, destino, data, n_passageiros=None):
        self.id_req = id_req
        self.nome = nome
        self.telefone = telefone
        self.origem = origem
        self.destino = destino
        self.data = data
        self.n_passageiros = n_passageiros