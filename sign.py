from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import pkcs1_15

class Entity:
    def __init__(self):
        self.key_pair = None
        self.public_key = None
        self.generate_keys()
        self.other_public_key = None
        
    def generate_keys(self):
        """ Gera as chaves pública e privada de uma entidade """
        random_seed = Random.new().read
        self.key_pair = RSA.generate(1024, random_seed)
        self.public_key = self.key_pair.publickey()

    def get_signature(self, message):
        """ Recebe uma mensagem e cria sua assinatura com base na
            chave privada da entidade """
        message_hash = SHA256.new(message.encode())
        signature = pkcs1_15.new(self.key_pair).sign(message_hash)
        return signature
    
    def verify_messsage(self, message, signature):
        """ Verifica se a assinatura recebida é compatível com a chave pública
            da outra entidade, validando, ou não, a assinatura """
        message_hash = SHA256.new(message.encode())
        try:
            pkcs1_15.new(self.other_public_key).verify(message_hash, signature)
            print("Valid Signature :)")
        except ValueError:
            print("Invalid Signature :(")


def main():
    alice = Entity()
    bob = Entity()

    # Bob recebe a chave pública de Alice
    bob.other_public_key = alice.public_key

    # Encontra-se a assinatura da mensagem criada por Alice
    signature = alice.get_signature("Hello World")

    # Bob verifica se o remetente foi a Alice
    bob.verify_messsage("Hello World", signature)


if __name__ == '__main__':
    main()


