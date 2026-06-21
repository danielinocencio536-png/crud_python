"""
Etapa 3 - CRUD com SQLite.

Banco: clientes.db
Tabela: clientes(id, nome, telefone, email)

Aprendizado: INSERT, SELECT, UPDATE, DELETE com sqlite3.
"""

import sqlite3

DB = "clientes.db"


def conectar():
    return sqlite3.connect(DB)


def criar_tabela():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT
            )
        """)


def cadastrar():
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome não pode ser vazio.")
        return
    telefone = input("Telefone: ").strip()
    email = input("Email: ").strip()

    with conectar() as conn:
        conn.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email),
        )
    print(f'Cliente "{nome}" cadastrado no banco!')


def listar():
    with conectar() as conn:
        rows = conn.execute(
            "SELECT id, nome, telefone, email FROM clientes ORDER BY id"
        ).fetchall()

    if not rows:
        print("Nenhum cliente cadastrado.")
        return
    print("\n--- Lista de Clientes ---")
    for r in rows:
        print(f"ID {r[0]} | Nome: {r[1]} | Tel: {r[2]} | Email: {r[3]}")
    print()


def buscar():
    termo = input("Buscar por nome: ").strip().lower()
    with conectar() as conn:
        rows = conn.execute(
            "SELECT id, nome, telefone, email FROM clientes WHERE LOWER(nome) LIKE ?",
            (f"%{termo}%",),
        ).fetchall()

    if not rows:
        print("Nenhum cliente encontrado.")
        return
    print("\n--- Resultados ---")
    for r in rows:
        print(f"ID {r[0]} | Nome: {r[1]} | Tel: {r[2]} | Email: {r[3]}")
    print()


def atualizar():
    try:
        id_cli = int(input("ID do cliente para atualizar: "))
    except ValueError:
        print("Digite um ID válido.")
        return

    with conectar() as conn:
        row = conn.execute(
            "SELECT id, nome, telefone, email FROM clientes WHERE id = ?", (id_cli,)
        ).fetchone()

    if not row:
        print("Cliente não encontrado.")
        return

    print(f"Atual: Nome: {row[1]} | Tel: {row[2]} | Email: {row[3]}")
    nome = input(f"Novo nome (enter para manter \"{row[1]}\"): ").strip() or row[1]
    telefone = input(f"Novo telefone (enter para manter \"{row[2]}\"): ").strip() or row[2]
    email = input(f"Novo email (enter para manter \"{row[3]}\"): ").strip() or row[3]

    with conectar() as conn:
        conn.execute(
            "UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, telefone, email, id_cli),
        )
    print("Cliente atualizado.")


def excluir():
    try:
        id_cli = int(input("ID do cliente para excluir (0 para cancelar): "))
    except ValueError:
        print("Digite um ID válido.")
        return
    if id_cli == 0:
        return
    with conectar() as conn:
        cur = conn.execute("DELETE FROM clientes WHERE id = ?", (id_cli,))
    if cur.rowcount:
        print("Cliente removido.")
    else:
        print("Cliente não encontrado.")


def menu():
    criar_tabela()
    while True:
        print("=== SISTEMA DE CADASTRO (SQLite) ===")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("3 - Buscar cliente")
        print("4 - Atualizar cliente")
        print("5 - Excluir cliente")
        print("6 - Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            cadastrar()
        elif opcao == "2":
            listar()
        elif opcao == "3":
            buscar()
        elif opcao == "4":
            atualizar()
        elif opcao == "5":
            excluir()
        elif opcao == "6":
            print("Saindo...")
            break
        else:
            print("Opção inválida.\n")


if __name__ == "__main__":
    menu()
