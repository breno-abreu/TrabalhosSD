// Autor: Breno Moura de Abreu [1561286]
// Autor: Julio Cesar Werner Scholz [2023890]

const axios = require('axios')
const prompt = require('prompt-sync')({sigint: true});

const util = require('util');
const sleep = util.promisify(setTimeout);

const EventSource = require('eventsource')
const readline = require('readline');

const url = "http://localhost:5000"
const rl = readline.createInterface(process.stdin, process.stdout);
var es = null

//Função que requisita uma carona no servidor, se o o parametro type_ for 1 um pedido de carona será criado
// se for 2, uma oferta de carona será criada
function requisitar_carona(type_){
    var is_ok = false
    var id = 0
    console.log("Insira os seguintes dados: \n")
    let user_name = prompt("Nome: ")
    let tel  = prompt("Telefone: ")
    let orig = prompt("Origem: ")
    let dest = prompt("Destino: ")
    let date = prompt("Data: ")

    //axios - realiza um post no url especificado
    axios
        .post(url+"/registrar_interesse", {
            nome: user_name,
            telefone: tel,
            tipo: type_,
            origem: orig,
            destino: dest,
            data: date
        }) 
        .then(res => {
            //Se a resposta do servidor for 200 - OK, um novo event listener será criado para a requisição feita baseada
            if (res.status == "200"){
                console.log(`Sucesso: ${res.status} - id: ${res.data.id} \n` )
                
                //uma event source será criado na url especificiada com o id da requisição retornado pelo servidor 
                es = new EventSource(url + "/stream/"+ res.data.id.toString())
                //Quando uma notificação dor enviada pelo servidor ela será tratada e informada para o usuario
                es.addEventListener("online", function(resp){
                    resp_json = JSON.parse(resp.data)

                    msg = "Notificação recebida!\n" + resp_json["nome"] 

                    if(resp_json["tipo"] == "pedido"){
                        msg = msg + " está precisando de uma carona com origem em " 
                    }
                    else{
                        msg = msg + " está oferencendo uma carona com origem em " 
                    }

                    msg = msg + resp_json["origem"] + " com destino para " + 
                    resp_json["destino"] + " na data " + resp_json["data"]

                    console.log(msg)
                }, true)

                id = res.data.id
                is_ok = true
            }
            else{
                console.log(`Não houve sucesso um sua requisição: ${res.status}\n` )
                is_ok = false
            }
            
        })
        .catch(error => {
            //Erro ao fazer o POST
            console.error(error)
            is_ok = false
        });
        
    if (is_ok){ 
        return id
    }
    return -1
}

//Função que cancela uma requisão de carona a partir de um id informado pelo usuário
function cancelar_carona(){
    let id_ = prompt("Id da carona que voce deseja cancelar: ")
    //baseada na id informado pelo usario uma requisição de carona será cancelada no servidor pelo metodo POST
    axios
        .post(url+"/cancelar_interesse", {
            id: id_
        }) 
        .then(res => {
            console.log(`statusCode: ${res.status} - ${res.data} \n` )
            //Se o cancelamento for efetuado com sucesso, o event source pode ser fechado
            if (res.status == "200"){
                es.close();
            }
            id = res.data.id
        })
        .catch(error => {
            console.error(error)
        });
}

//Função que a realiza a consulta de caronas dado a origem o destino e a data
function consultar(){
    console.log("Insira os seguintes dados: \n")
    let orig = prompt("Origem: ")
    let dest = prompt("Destino: ")
    let date = prompt("Data: ")

    //metodo GET, enviado para servidor junto com os argumentos
    axios
    .get('http://localhost:5000/consultar', {
        params: {
            origem: orig ,
            destino: dest,
            data: date
        }
     })
    .then(res => {
        //Se servidor responder com status 200, mostra a resposta
        if (res.status == "200"){
            console.log(res.data)
        }
    }).catch(function(e) {
        console.log(e);
    })
}


//Função main que recebe o input do usario de forma continua
async function main(){
    menu = "( 1 ) :: Requisitar carona\n"
    menu += "( 2 ) :: Oferecer carona\n"
    menu += "( 3 ) :: Cancelar carona\n"
    menu += "( 4 ) :: Consultar caronas\n" 
    menu += "( 0 ) :: Sair\n"

    //Mostra o texto do menu no prompt
    rl.setPrompt(menu);
    rl.prompt();
    //Recebe o input do usario pela linha de comando de forma continua, até que haja uma interrupção pelo usuario (ctrl + c ou 0)
    rl.on('line', async function(opt) {
        switch(opt){
            case "0":
                rl.close();
                break;
            case "1":
                requisitar_carona(opt)
                break;
            case "2":
                requisitar_carona(opt)
                break;
            case "3":
                cancelar_carona()
                break;
            case "4":
                consultar()
            default:
            console.log("Entrada inválida...")
        }
        //Espera 2 segundos
        await sleep(2000);
        //Mostra o texto do menu no prompt 
        console.log(menu)
    }).on('close',function(){
        //Fecha o programa
        process.exit(0);
    });

}

//Inicialização da main
main()

