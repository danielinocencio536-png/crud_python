"""
Etapa 1 - Sistema de Cadastro (CRUD) em Console

Funcionalidades:
1 - Cadastrar cliente
2 - Listar clientes
3 - Buscar cliente
4 - Excluir cliente
5 - Sair

Aprendizado: variáveis, listas, loops, funções, condicionais.
"""

clientes = []  # lista que vai guardar dicionários {"nome","telefone","email"}


def cadastrar():
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome não pode ser vazio.")
        return
    telefone = input("Telefone: ").strip()
    email = input("Email: ").strip()

    clientes.append({"nome": nome, "telefone": telefone, "email": email})
    print(f'Cliente "{nome}" cadastrado com sucesso!')


def listar():
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return
    print("\n--- Lista de Clientes ---")
    for i, c in enumerate(clientes, start=1):
        print(f"{i}. Nome: {c['nome']} | Tel: {c['telefone']} | Email: {c['email']}")
    print()


def buscar():
    termo = input("Buscar por nome (ou parte dele): ").strip().lower()
    encontrados = [c for c in clientes if termo in c["nome"].lower()]
    if not encontrados:
        print("Nenhum cliente encontrado.")
        return
    print("\n--- Resultados ---")
    for i, c in enumerate(encontrados, start=1):
        print(f"{i}. Nome: {c['nome']} | Tel: {c['telefone']} | Email: {c['email']}")
    print()


def excluir():
    listar()
    if not clientes:
        return
    try:
        idx = int(input("Número do cliente para excluir (0 para cancelar): "))
    except ValueError:
        print("Digite um número válido.")
        return
    if idx == 0:
        return
    if 1 <= idx <= len(clientes):
        removido = clientes.pop(idx - 1)
        print(f'Cliente "{removido["nome"]}" removido.')
    else:
        print("Número fora do intervalo.")


def menu():
    while True:
        print("=== SISTEMA DE CADASTRO ===")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("3 - Buscar cliente")
        print("4 - Excluir cliente")
        print("5 - Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            cadastrar()
        elif opcao == "2":
            listar()
        elif opcao == "3":
            buscar()
        elif opcao == "4":
            excluir()
        elif opcao == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida.\n")


if __name__ == "__main__":
    menu()
