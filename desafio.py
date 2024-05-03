from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Conta:
    def __init__ (self, numero, cliente):
        self._saldo=0
        self._numero=numero
        self._agencia="0001"
        self._cliente=cliente
        self._historico=Historico()
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero,cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar (self, valor):
        self._valor= float(valor)
        saldo= self.saldo
        excedeu_saldo = valor>saldo

        if excedeu_saldo:
            print("Operação não realizada. Você não tem saldo suficiente!")
        
        elif valor>0:
            self._saldo -=valor
            return True
        else:
            print("O valor informado não é válido")
            return False

    def depositar(self,valor):
        self._valor= float(valor)
        if valor>0:
            self._saldo+= valor
            print("Depósito realizado com sucesso!")
            return True
        else:
            print("O valor informado não é válido")  
            return False
        
class ContaCorrente (Conta):
    def __init__(self, numero, cliente,limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite=float(limite)
        self._limite_saques=int(limite_saques)

    def sacar (self, valor):
        numero_saques=len(
            [transacao for transacao in self.historico._transacoes if transacao["tipo"] == Saque.__name__]    
        )

        excedeu_limite= valor>self._limite
        excedeu_saques= numero_saques> self._limite_saques

        if excedeu_limite:
            print (f"Operação falhou! O saque excede o limite de R$ {self.limite}")

        elif excedeu_saques:
            print (f"Operação falhou! Número de saques excedido!")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""
            Agência: \t {self.agencia}
            C/C:\t {self.numero}
            Titular: \t {self.cliente.nome}
            """

class Historico:
    def __init__ (self):
        self._transacoes = []
    
    def adicionar_transacao (self, transacao):
        self._transacoes.append ({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            })
        
class Cliente:
    def __init__(self, endereco):
        self._endereco=endereco
        self._contas=[]

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta (self,conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf=str(cpf)
        self.nome= str(nome)
        self.data_nascimento=data_nascimento

class Transacao (ABC):
    @property
    @abstractclassmethod
    def valor(self):
        pass

    @abstractclassmethod
    def registrar (self, conta):
        pass
        
class Saque (Transacao):
    def __init__(self, valor):
        self._valor=float(valor)

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao= conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito (Transacao):
    def __init__(self, valor):
        self._valor=float(valor)
    
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao=conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    print (f"""\n
    ###### MENU ######  
    [1] Depósito
    [2] Saque
    [3] Extrato
    [4] Criar usuario
    [5] Criar conta
    [6] Listar conta
    [0] Sair     
    """)
    opcao= int(input("Informe a opcao desejada: "))
    return opcao

def filtrar_cliente(cpf,clientes):
     clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
     return clientes_filtrados [0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente._contas:
        print ("Cliente não possui conta!")
        return
    
    #FIXME
    return cliente._contas[0]

def depositar (clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente= filtrar_cliente(cpf, clientes)

    if not cliente:
        print ("Cliente não encontrado")
        return 

    valor= float(input("Informe o valor a ser depositado: "))
    transacao =Deposito(valor)

    conta= recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar (clientes):
    cpf= input("Informe o CPF do cliente: ")
    cliente=filtrar_cliente(cpf, clientes)

    if not cliente:
        print ("cliente não encontrado")
        return


    valor= float(input("Informe o valor do saque: "))
    transacao= Saque(valor)

    conta=recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta,transacao)

def exibir_extrato(clientes):
    cpf= input("Informe o CPF do cliente: ")
    cliente=filtrar_cliente(cpf, clientes)

    if not cliente:
        print ("cliente não encontrado")
        return

    conta=recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n###### EXTRATO ######")
    transacoes= conta.historico._transacoes

    extrato= ""
    if not transacoes:
        extrato= "não foram realizadas movimentações"

    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}: \n\t R$ {transacao['valor']:.2f}"

    print (extrato)
    print (f"\n Saldo: R$ {conta.saldo:.2f}")

def criar_cliente(clientes):
    cpf= input("Informe o CPF do cliente: ")
    cliente=filtrar_cliente(cpf, clientes)

    if cliente:
        print ("Já existe cliente com esse CPF!")
        return
    
    nome= input("Informe o nome do cliente: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente= PessoaFisica (nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereco)

    clientes.append(cliente)
    print("Cliente criado com sucesso!")

def criar_conta(numero_conta, clientes, contas):
    cpf= input("Informe o CPF do cliente: ")
    cliente=filtrar_cliente(cpf, clientes)

    if not cliente:
        print ("cliente não encontrado")
        return

    conta= ContaCorrente.nova_conta(cliente=cliente, numero= numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("Conta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print(str(conta))

def main():
    clientes = []
    contas = []

    while True:
        opcao=menu()
        if opcao==1:
            depositar(clientes)

        elif opcao==2:
            sacar(clientes)

        elif opcao==3:
            exibir_extrato(clientes)

        elif opcao==4:
            criar_cliente(clientes)

        elif opcao==5:
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao==6:
            listar_contas(contas)

        elif opcao==7:
            break

        else:
            print("Infrme uma operação válida")


main()
             













