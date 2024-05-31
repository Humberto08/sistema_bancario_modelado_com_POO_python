# Codigo correto

from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
import textwrap

# Cliente
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco    
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

# Pessoa Física
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

# Conta
class Conta:
    def __init__(self, numero, cliente):
        self._agencia = '0001'
        self._numero = numero
        self._cliente = cliente
        self._saldo = 0
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

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

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print('*** Operação falhou! O valor de saque excede o valor do saldo.***')
        elif valor > 0:
            self._saldo -= valor
            print(f'=== Saque de R$ {valor} realizado com sucesso! ===')
            return True
        else:
            print('*** Operação falhou! O valor informado é inválido. ***')

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f'=== Depósito de R$ {valor} realizado com sucesso! ===')
            return True
        else:
            print('*** Operação falhou! O valor informado é inválido. ***')

        return False

# Conta Corrente
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__])
        
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print('*** Operação falhou! O valor do saque excede o limite. ***')
        elif excedeu_saques:
            print('*** Operação falhou! Número máximo de saques excedido. ***')
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f'''\
            Agência: {self.agencia}
            C/C: {self.numero}
            Titular: {self.cliente.nome}
        '''

# Historico
class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                'data': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                'valor': transacao.valor,
                'tipo': transacao.__class__.__name__,
                'conta_destino': getattr(transacao, 'conta_destino', None)
            }
        )

# Transacao
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

# Saque
class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self._valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# Deposito
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self._valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# Transferencia
class Transferencia(Transacao):
    def __init__(self, valor, conta_destino):
        self._valor = valor
        self._conta_destino = conta_destino

    @property
    def valor(self):
        return self._valor

    @property
    def conta_destino(self):
        return self._conta_destino

    def registrar(self, conta_origem):
        if conta_origem.sacar(self._valor):
            self._conta_destino.depositar(self._valor)
            conta_origem.historico.adicionar_transacao(self)
            self._conta_destino.historico.adicionar_transacao(self)

# Emprestimo
class Emprestimo(Transacao):
    TAXA_JUROS = 0.05  # 5% de juros
    NUMERO_PARCELAS = 12  # 12 parcelas

    def __init__(self, valor):
        self._valor = valor
        self._juros = Emprestimo.TAXA_JUROS
        self._parcelas = Emprestimo.NUMERO_PARCELAS

    @property
    def valor(self):
        return self._valor

    @property
    def juros(self):
        return self._juros

    @property
    def parcelas(self):
        return self._parcelas

    def registrar(self, conta):
        valor_com_juros = self._valor * (1 + self._juros)
        conta.depositar(self._valor)
        conta.historico.adicionar_transacao(self)

# Menu
def linha_completa(texto, largura=80, caractere='='):
    texto_centralizado = texto.center(largura, caractere)
    return texto_centralizado

def menu():
    menu_texto = f"""\n
    {linha_completa("\tHbank\t")}\n
    {linha_completa("\tMENU\t")}\n
    Bem-vindo ao Hbank, seu banco digital de toda hora!

    Escolha uma das opções abaixo:

    [d]\tDepositar
    [s]\tSacar
    [t]\tTransferir
    [e]\tExtrato
    [emp]\tEmpréstimo
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_texto))

# Filtrar cliente
def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

# Filtrar conta
def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n*** Cliente não possui contas! ***")
        return
    
    # FIXME: não permite cliente escolher conta
    return cliente.contas[0]  

# Depositar
def depositar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n*** Usuário não encontrado! ***")
        return

    valor = float(input("Valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

# Sacar
def sacar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n*** Usuário não encontrado! ***")
        return

    valor = float(input("Valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

# Transferir
def transferir(clientes):
    cpf_origem = input("CPF do cliente de origem: ")
    cliente_origem = filtrar_cliente(cpf_origem, clientes)

    if not cliente_origem:
        print("\n*** Cliente de origem não encontrado! ***")
        return

    cpf_destino = input("CPF do cliente de destino: ")
    cliente_destino = filtrar_cliente(cpf_destino, clientes)

    if not cliente_destino:
        print("\n*** Cliente de destino não encontrado! ***")
        return

    valor = float(input("Valor da transferência: "))
    conta_origem = recuperar_conta_cliente(cliente_origem)
    conta_destino = recuperar_conta_cliente(cliente_destino)

    if not conta_origem or not conta_destino:
        return

    transacao = Transferencia(valor, conta_destino)
    cliente_origem.realizar_transacao(conta_origem, transacao)

# Extrato
def exibir_extrato(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n*** Usuário não encontrado! ***")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n============== EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    total_transferencias_efetuadas = 0
    total_transferencias_recebidas = 0
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            if transacao['tipo'] == 'Transferencia':
                if transacao['conta_destino'] == conta:
                    extrato += f"\nTransferência Recebida:\n\tR$ {transacao['valor']:.2f}"
                    total_transferencias_recebidas += transacao['valor']
                else:
                    extrato += f"\nTransferência Efetuada:\n\tR$ {transacao['valor']:.2f}"
                    total_transferencias_efetuadas += transacao['valor']
            else:
                extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nTotal de Transferências Efetuadas:\tR$ {total_transferencias_efetuadas:.2f}")
    print(f"Total de Transferências Recebidas:\tR$ {total_transferencias_recebidas:.2f}")
    print(f"\nSaldo:\tR$ {conta.saldo:.2f}")
    print("=============== EXTRATO ================")

# Emprestimo
def solicitar_emprestimo(clientes):
    cpf = input("CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n*** Usuário não encontrado! ***")
        return

    valor = float(input("Valor do empréstimo: "))
    transacao = Emprestimo(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)
    valor_com_juros = valor * (1 + Emprestimo.TAXA_JUROS)
    parcela = valor_com_juros / Emprestimo.NUMERO_PARCELAS
    print(f"Empréstimo aprovado! Valor total com juros: R$ {valor_com_juros:.2f}")
    print(f"Serão {Emprestimo.NUMERO_PARCELAS} parcelas de R$ {parcela:.2f}")

# Novo cliente
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n*** Usuário já existe com esse CPF! ***")
        return

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)
    print("\n=== Usuário criado com sucesso! ===")

# Nova conta
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n*** Usuário não encontrado! ***")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)

    contas.append(conta)
    cliente.contas.append(conta)
    print("\n=== Conta criada com sucesso! ===")

# Listar contas
def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))
        print("=" * 100)

# Main
def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "t":
            transferir(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "emp":
            solicitar_emprestimo(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == 'q':
            break

        else:
            print("\n*** Opção inválida!, por favor tente novamente a opção desejada. ***\n")

main()
