"""
Etapa 5 - Versão web com Flask (HTML + CSS), usando o mesmo banco SQLite.

Instalar dependência:
    pip install flask

Uso:
    python etapa5_web.py          -> abre em http://127.0.0.1:5000
    python etapa5_web.py --rede   -> também aceita acesso de outros aparelhos
                                     da mesma rede Wi-Fi (ex.: o celular da loja),
                                     pelo IP do computador: http://<ip>:5000

Páginas:
    /                  lista de clientes + busca por nome
    /novo              formulário de cadastro
    /editar/<id>       formulário de atualização
    /excluir/<id>      exclusão (só por POST, com confirmação no navegador)
"""

import re
import secrets
import sqlite3
import sys

from flask import Flask, abort, flash, redirect, render_template, request, url_for

DB = "clientes.db"

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # necessário para as mensagens (flash)


# ----------------- camada de dados (igual à etapa 3/4) -----------------
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


def listar_todos():
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nome, telefone, email FROM clientes ORDER BY id"
        ).fetchall()


def buscar_por_nome(termo):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nome, telefone, email FROM clientes "
            "WHERE LOWER(nome) LIKE ? ORDER BY id",
            (f"%{termo.lower()}%",),
        ).fetchall()


def buscar_por_id(id_cli):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nome, telefone, email FROM clientes WHERE id = ?", (id_cli,)
        ).fetchone()


def inserir(nome, telefone, email):
    with conectar() as conn:
        conn.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email),
        )


def atualizar(id_cli, nome, telefone, email):
    with conectar() as conn:
        conn.execute(
            "UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, telefone, email, id_cli),
        )


def deletar(id_cli):
    with conectar() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (id_cli,))


# ----------------- validação (mesmas regras da etapa 4) -----------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def so_digitos(texto):
    return "".join(c for c in (texto or "") if c.isdigit())


def formatar_telefone(digitos):
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"


def validar_cliente(nome, telefone, email, ignorar_id=None):
    """Retorna (erro, dados). Se der certo, erro é None."""
    nome = nome.strip()
    telefone = telefone.strip()
    email = email.strip().lower()

    if not nome:
        return "O campo Nome é obrigatório.", None

    if telefone:
        digitos = so_digitos(telefone)
        if len(digitos) not in (10, 11):
            return "Telefone inválido. Use DDD + número, ex.: (11) 99999-0000.", None
        telefone = formatar_telefone(digitos)

    if email and not EMAIL_RE.match(email):
        return "Email inválido. Exemplo: maria@email.com", None

    for id_cli, nome_cli, tel_cli, email_cli in listar_todos():
        if id_cli == ignorar_id:
            continue
        if email and email == (email_cli or "").strip().lower():
            return f"Já existe um cliente com este email: ID {id_cli} - {nome_cli}.", None
        if telefone and so_digitos(telefone) == so_digitos(tel_cli):
            return f"Já existe um cliente com este telefone: ID {id_cli} - {nome_cli}.", None

    return None, (nome, telefone, email)


def dados_do_form():
    return (request.form.get("nome", ""), request.form.get("telefone", ""),
            request.form.get("email", ""))


# ----------------- páginas -----------------
@app.route("/")
def index():
    termo = request.args.get("q", "").strip()
    clientes = buscar_por_nome(termo) if termo else listar_todos()
    return render_template("lista.html", clientes=clientes, termo=termo)


@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        erro, dados = validar_cliente(*dados_do_form())
        if erro:
            flash(erro, "erro")
            return render_template("form.html", titulo="Novo cliente",
                                   cliente=dados_do_form()), 400
        inserir(*dados)
        flash(f'Cliente "{dados[0]}" cadastrado!', "ok")
        return redirect(url_for("index"))
    return render_template("form.html", titulo="Novo cliente", cliente=("", "", ""))


@app.route("/editar/<int:id_cli>", methods=["GET", "POST"])
def editar(id_cli):
    cliente = buscar_por_id(id_cli)
    if cliente is None:
        abort(404)
    titulo = f"Editar cliente ID {id_cli}"
    if request.method == "POST":
        erro, dados = validar_cliente(*dados_do_form(), ignorar_id=id_cli)
        if erro:
            flash(erro, "erro")
            return render_template("form.html", titulo=titulo, id_cli=id_cli,
                                   cliente=dados_do_form()), 400
        atualizar(id_cli, *dados)
        flash(f"Cliente ID {id_cli} atualizado!", "ok")
        return redirect(url_for("index"))
    _, nome, telefone, email = cliente
    return render_template("form.html", titulo=titulo, id_cli=id_cli,
                           cliente=(nome, telefone or "", email or ""))


@app.route("/excluir/<int:id_cli>", methods=["POST"])
def excluir(id_cli):
    cliente = buscar_por_id(id_cli)
    if cliente is None:
        abort(404)
    deletar(id_cli)
    flash(f'Cliente "{cliente[1]}" excluído.', "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    criar_tabela()
    host = "0.0.0.0" if "--rede" in sys.argv else "127.0.0.1"
    app.run(host=host, port=5000)
