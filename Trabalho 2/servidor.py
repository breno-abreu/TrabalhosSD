# Autor: Breno Moura de Abreu [1561286]
# Autor: Julio Cesar Werner Scholz [2023890]

import time
import json
from flask import Flask, request, jsonify, make_response
from flask.wrappers import Response

# lista de requisições de caronas registradas
# para receber notificações
caronas = []

# Contador que define um identificador único para
# cada requisição de carona
id_cont = 0

# Cria um objeto Flask
app = Flask(__name__)

# Decorator do Flask que indica que a função será
# chamada pelo cliente pela web através de uma URL
@app.route('/consultar', methods=['GET'])
def consultar():
    """ Recebe um request com argumentos e retorna as caronas
        que tem a mesma origem, destino e data recebida """

    #Recebe os argumentos
    info = request.args

    # Lista de caronas que serão enviadas para o cliente
    lista = []

    for carona in caronas:
        if info['origem'] == carona['origem'] and info['destino'] == carona['destino'] and info['data'] == carona['data']:
           lista.append(carona)

    # Caso haja pelo menos 1 registro na lista envia-a no formato JSON para o cliente
    if len(lista) > 0:
        return jsonify({'caronas' : lista})
    
    # Caso a lista esteja vazia envia um texto simples
    texto = "Nenhuma carona encontrada!"
    resposta = make_response(texto, 200)
    resposta.mimetype = 'text/plain'
        
    return resposta



@app.route('/registrar_interesse', methods=['POST'])
def registrar_interesse():
    """ Recebe um arquivo JSON contendo as informações
        de uma requisição, cria um dicionário e adiciona-o
        na lista de caronas que querem receber notificações """

    # Converte o arquivo JSON em um dicionário
    info = request.json
    
    # Incrementa o contador e adiciona um novo campo
    # 'id' no dicionário que recebe o número incrementado
    global id_cont
    id_cont += 1
    info['id'] = str(id_cont)

    if info['tipo'] == '1':
        info['tipo'] = 'pedido'
    else:
        info['tipo'] = 'oferta'
    
    # Adiciona o dicionário na lista de caronas
    caronas.append(info)

    # Retorna o id da requisição em formato JSON
    return jsonify({'id' : str(id_cont)})


@app.route('/cancelar_interesse', methods=['POST'])
def cancelar_interesse():
    """ Cancela a carona com id recebido em formato JSON
        retirando-a da lista """

    # Converte o arquivo JSON em um dicionário
    info = request.json
    id_req = info['id']

    # Indica se a carona foi cancelada ou não
    carona_cancelada = False

    # Remove a carona com o id recebido da lista de caronas
    for carona in caronas:
        if id_req == carona['id']:
            caronas.remove(carona)
            carona_cancelada = True
            break;

    # Envia uma mensagem para o servidor indicando se a requisição foi ou não cancelada
    if(carona_cancelada == True):
        texto = "Carona com id {0} foi cancelada!".format(id_req)
    else:
        texto = "Nenhuma carona com id {0} foi encontrada".format(id_req)
    
    resposta = make_response(texto, 200)
    resposta.mimetype = 'text/plain'

    return resposta


@app.route('/stream/<id_req>')
def evento(id_req):
    """ Inicia os Server-Sent Events (SSE) que irão enviar uma notificação
        para o cliente caso encontre uma carona que esteja de acordo com as
        informações da requisição que tem o id indicado na URL """

    def enviar_notificacao(id_req):
        """ Procura por caronas e envia uma mensagem ao cliente caso
            encontre uma carona apropriada """

        # Variável que irá conter a carona com o id recebido
        info = None

        # Encontra a carona com o id recebido na lista de caronas
        for carona in caronas:
            if carona['id'] == str(id_req):
                info = carona
        
        # Lista contendo os ids das caronas que já foram notificadas ao cliente
        ids_enviados = []

        # Loop infinito que procura pelas caronas que estejam de acordo
        # com a carona com o id recebido
        while True:
            if info != None:
                for carona in caronas:
                    if (carona['id'] != info['id'] and 
                        carona['tipo'] != info['tipo'] and
                        carona['origem'] == info['origem'] and 
                        carona['destino'] == info['destino'] and
                        carona['data'] == info['data'] and 
                        carona['id'] not in ids_enviados):

                        # Cria a reposta em formato JSON contendo todas as 
                        # informações de uma carona
                        dados = json.dumps(carona)

                        # Adiciona o id da carona enviada na lista, evitando
                        # que a mesma carona seja enviada novamente
                        ids_enviados.append(carona['id'])

                        # Envia a mensagem com as informações da carona
                        # O evento recebe o tipo 'online'
                        yield "data: {0}\nevent: online\n\n".format(dados)

            # Espera 1 segundo até pesquisar novamente
            time.sleep(1)

    # Função do Flask que irá enviar as notificações ao cliente de acordo com 
    # a função 'enviar_notificacao'
    return Response(enviar_notificacao(id_req), mimetype='text/event-stream')
            

if __name__ == "__main__":
    """ Executa o servidor """
    app.run(debug=True)