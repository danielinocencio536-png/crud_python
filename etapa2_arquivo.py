"""
Etapa 2 - CRUD persistido em arquivo texto (clientes.txt).

Cada cliente é gravado em uma linha no formato:
nome|telefone|email

Aprendizado: open(), leitura/escrita de arquivos, persistência simples.
"""

ARQUIVO = "clientes.txt"
clientes = []  # cache em memória sincronizado com o arquivo


def carregar():
    global clientes
    clientes = []
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split("|")
                if len(partes) == 3:
                    clientes.append({
                        "nome": partes[0],
                        "telefone": partes[1],
                        "email": partes[2],
                    })
    except FileNotFoundError:
        # primeira execução: arquivo ainda não existe
        open(ARQUIVO, "w", encoding="utf-8").close()


def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        for c in clientes:
            f.write(f"{c['nome']}|{c['telefone']}|{c['email']}\n")


def cadastrar():
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome não pode ser vazio.")
        return
    telefone = input("Telefone: ").strip()
    email = input("Email: ").strip()

    clientes.append({"nome": nome, "telefone": telefone, "email": email})
    salvar()
    print(f'Cliente "{nome}" cadastrado e salvo em {ARQUIVO}!')


def listar():
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return
    print("\n--- Lista de Clientes ---")
    for i, c in enumerate(clientes, start=1):
        print(f"{i}. Nome: {c['nome']} | Tel: {c['telefone']} | Email: {c['email']}")
    print()


def buscar():
    termo = input("Buscar por nome: ").strip().lower()
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
        salvar()
        print(f'Cliente "{removido["nome"]}" removido e arquivo atualizado.')
    else:
        print("Número fora do intervalo.")


def menu():
    carregar()
    while True:
        print("=== SISTEMA DE CADASTRO (ARQUIVO) ===")
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
