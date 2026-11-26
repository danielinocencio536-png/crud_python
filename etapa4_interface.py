"""
Etapa 4 - Interface gráfica com customtkinter (persistência em SQLite).

Instalar dependência:
    pip install customtkinter

Uso:
    python etapa4_interface.py

Como usar a janela:
    - Cadastrar: preencha os campos e clique em Cadastrar.
    - Buscar: digite parte do nome no campo de busca (filtra na hora).
    - Atualizar: clique num cliente da tabela, altere os campos e clique em Atualizar.
    - Excluir: clique num cliente da tabela e clique em Excluir (ou tecla Delete).
"""

import re
import sqlite3
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk
import types

try:
    import customtkinter as ctk
    TEM_CTK = True
except ImportError:
    TEM_CTK = False

    class CTk(tk.Tk):
        pass

    class CTkLabel(tk.Label):
        def __init__(self, master=None, width=None, **kwargs):
            super().__init__(master, **kwargs)  # width do ctk é em pixels

    class CTkFrame(tk.Frame):
        def __init__(self, master=None, fg_color=None, **kwargs):
            super().__init__(master, **kwargs)

    class CTkEntry(tk.Entry):
        def __init__(self, master=None, placeholder_text=None, **kwargs):
            super().__init__(master, **kwargs)

    class CTkButton(tk.Button):
        def __init__(self, master=None, fg_color=None, hover_color=None, **kwargs):
            super().__init__(master, **kwargs)

    def set_appearance_mode(mode):
        pass

    def set_default_color_theme(theme):
        pass

    def CTkFont(size=12, weight="normal"):
        return tkfont.Font(size=size, weight=weight)

    ctk = types.SimpleNamespace(
        CTk=CTk,
        CTkLabel=CTkLabel,
        CTkFrame=CTkFrame,
        CTkEntry=CTkEntry,
        CTkButton=CTkButton,
        set_appearance_mode=set_appearance_mode,
        set_default_color_theme=set_default_color_theme,
        CTkFont=CTkFont,
    )

DB = "clientes.db"


# ----------------- camada de dados -----------------
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


def inserir(nome, telefone, email):
    with conectar() as conn:
        conn.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email),
        )


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


def atualizar(id_cli, nome, telefone, email):
    with conectar() as conn:
        conn.execute(
            "UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, telefone, email, id_cli),
        )


def deletar(id_cli):
    with conectar() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (id_cli,))


# ----------------- validação -----------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def so_digitos(texto):
    return "".join(c for c in (texto or "") if c.isdigit())


def formatar_telefone(digitos):
    """11999990000 -> (11) 99999-0000 | 1133334444 -> (11) 3333-4444"""
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"


def validar_cliente(nome, telefone, email, ignorar_id=None):
    """Confere os dados antes de salvar.

    Retorna (erro, dados). Se der certo, erro é None e dados é a tupla
    (nome, telefone, email) já padronizada. ignorar_id serve para a
    atualização: o próprio cliente não conta como duplicado.
    """
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

    # duplicado = outro cliente com o mesmo email ou o mesmo telefone
    for id_cli, nome_cli, tel_cli, email_cli in listar_todos():
        if id_cli == ignorar_id:
            continue
        if email and email == (email_cli or "").strip().lower():
            return f"Já existe um cliente com este email: ID {id_cli} - {nome_cli}.", None
        if telefone and so_digitos(telefone) == so_digitos(tel_cli):
            return f"Já existe um cliente com este telefone: ID {id_cli} - {nome_cli}.", None

    return None, (nome, telefone, email)


# ----------------- interface -----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

VERMELHO = "#a83232"
VERMELHO_HOVER = "#7a2424"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Cadastro de Clientes")
        self.geometry("760x620")
        self.minsize(640, 520)

        criar_tabela()
        self.id_selecionado = None  # cliente clicado na tabela

        # título
        ctk.CTkLabel(self, text="Cadastro de Clientes",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(12, 4))

        # campos, com rótulo fixo ao lado (assim o usuário sempre sabe qual é qual)
        frame_form = ctk.CTkFrame(self)
        frame_form.pack(pady=8, padx=16, fill="x")
        frame_form.columnconfigure(1, weight=1)

        self.entry_nome = self._campo(frame_form, 0, "Nome *", "Ex.: Maria Silva")
        self.entry_telefone = self._campo(frame_form, 1, "Telefone", "Ex.: (11) 99999-0000")
        self.entry_email = self._campo(frame_form, 2, "Email", "Ex.: maria@email.com")

        # botões: grade com colunas do mesmo tamanho, nenhum texto fica cortado
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=4, padx=16, fill="x")
        botoes = [
            ("Cadastrar", self.on_cadastrar, {}),
            ("Atualizar", self.on_atualizar, {}),
            ("Excluir", self.on_excluir,
             {"fg_color": VERMELHO, "hover_color": VERMELHO_HOVER}),
            ("Limpar", self.on_limpar, {}),
        ]
        for col, (texto, comando, cores) in enumerate(botoes):
            frame_btns.columnconfigure(col, weight=1, uniform="botoes")
            ctk.CTkButton(frame_btns, text=texto, command=comando, **cores).grid(
                row=0, column=col, padx=4, sticky="ew"
            )

        # busca (filtra enquanto digita)
        frame_busca = ctk.CTkFrame(self, fg_color="transparent")
        frame_busca.pack(pady=(12, 4), padx=16, fill="x")
        ctk.CTkLabel(frame_busca, text="Buscar").pack(side="left", padx=(4, 8))
        self.entry_busca = ctk.CTkEntry(frame_busca,
                                        placeholder_text="Digite parte do nome...")
        self.entry_busca.pack(side="left", fill="x", expand=True, padx=4)
        self.entry_busca.bind("<KeyRelease>", lambda e: self.carregar_lista())

        # tabela clicável
        self._estilo_tabela()
        frame_tabela = ctk.CTkFrame(self)
        frame_tabela.pack(pady=4, padx=16, fill="both", expand=True)
        colunas = ("id", "nome", "telefone", "email")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings",
                                   selectmode="browse")
        for col, titulo, largura, ancora in [
            ("id", "ID", 50, "center"),
            ("nome", "Nome", 200, "w"),
            ("telefone", "Telefone", 140, "w"),
            ("email", "Email", 220, "w"),
        ]:
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=largura, anchor=ancora, stretch=(col != "id"))
        if TEM_CTK:
            barra = ctk.CTkScrollbar(frame_tabela, command=self.tabela.yview)
        else:
            barra = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        barra.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.tabela.bind("<<TreeviewSelect>>", self.on_selecionar)
        self.tabela.bind("<Delete>", lambda e: self.on_excluir())

        # barra de status: avisos de sucesso sem abrir janelinha
        self.status = ctk.CTkLabel(self, text="", anchor="w")
        self.status.pack(fill="x", padx=20, pady=(0, 10))

        self.carregar_lista()

    # ---- montagem ----
    def _campo(self, master, linha, rotulo, dica):
        ctk.CTkLabel(master, text=rotulo, width=80, anchor="w").grid(
            row=linha, column=0, padx=(10, 4), pady=4, sticky="w")
        entry = ctk.CTkEntry(master, placeholder_text=dica)
        entry.grid(row=linha, column=1, padx=(4, 10), pady=4, sticky="ew")
        return entry

    def _estilo_tabela(self):
        """Deixa a tabela (ttk) com as cores do tema escuro do customtkinter."""
        if not TEM_CTK:
            return
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b",
                         foreground="#dce4ee", rowheight=26, borderwidth=0)
        estilo.map("Treeview", background=[("selected", "#1f6aa5")],
                   foreground=[("selected", "white")])
        estilo.configure("Treeview.Heading", background="#3a3a3a",
                         foreground="#dce4ee", relief="flat")
        estilo.map("Treeview.Heading", background=[("active", "#4a4a4a")])

    # ---- ações ----
    def _dados_do_form(self):
        return (self.entry_nome.get(), self.entry_telefone.get(), self.entry_email.get())

    def on_cadastrar(self):
        erro, dados = validar_cliente(*self._dados_do_form())
        if erro:
            messagebox.showwarning("Atenção", erro)
            return
        inserir(*dados)
        self.on_limpar()
        self.carregar_lista()
        self.mostrar_status(f'Cliente "{dados[0]}" cadastrado!')

    def on_atualizar(self):
        if self.id_selecionado is None:
            messagebox.showinfo("Selecione", "Clique no cliente da tabela que deseja atualizar.")
            return
        id_cli = self.id_selecionado
        erro, dados = validar_cliente(*self._dados_do_form(), ignorar_id=id_cli)
        if erro:
            messagebox.showwarning("Atenção", erro)
            return
        atualizar(id_cli, *dados)
        self.on_limpar()
        self.carregar_lista()
        self.mostrar_status(f"Cliente ID {id_cli} atualizado!")

    def on_excluir(self):
        if self.id_selecionado is None:
            messagebox.showinfo("Selecione", "Clique no cliente da tabela que deseja excluir.")
            return
        cliente = buscar_por_id(self.id_selecionado)
        if cliente is None:  # já foi apagado
            self.on_limpar()
            self.carregar_lista()
            return
        id_cli, nome = cliente[0], cliente[1]
        if messagebox.askyesno("Confirmar", f'Excluir o cliente ID {id_cli} - "{nome}"?'):
            deletar(id_cli)
            self.on_limpar()
            self.carregar_lista()
            self.mostrar_status(f'Cliente "{nome}" excluído.')

    def on_selecionar(self, event=None):
        selecao = self.tabela.selection()
        if not selecao:
            return
        id_cli, nome, telefone, email = self.tabela.item(selecao[0], "values")
        self.id_selecionado = int(id_cli)
        for entry, valor in [(self.entry_nome, nome),
                             (self.entry_telefone, telefone),
                             (self.entry_email, email)]:
            entry.delete(0, "end")
            if valor:
                entry.insert(0, valor)
        self.mostrar_status(f"Selecionado: ID {id_cli} - {nome}. "
                            "Altere os campos e clique em Atualizar, ou clique em Excluir.")

    def on_limpar(self):
        # Tira o foco dos campos ANTES de apagar. O CTkEntry só mostra a
        # dica (placeholder) de novo num campo vazio que não está com foco;
        # era por isso que as dicas sumiam depois de cadastrar.
        self.focus_set()
        self.update()
        for entry in (self.entry_nome, self.entry_telefone, self.entry_email):
            entry.delete(0, "end")
        self.id_selecionado = None
        if self.tabela.selection():
            self.tabela.selection_remove(self.tabela.selection())
        self.mostrar_status("")

    def mostrar_status(self, texto):
        self.status.configure(text=texto)

    def carregar_lista(self):
        termo = self.entry_busca.get().strip()
        rows = buscar_por_nome(termo) if termo else listar_todos()
        self.tabela.delete(*self.tabela.get_children())
        for r in rows:
            valores = tuple("" if v is None else v for v in r)
            self.tabela.insert("", "end", iid=str(r[0]), values=valores)
        if termo:
            self.mostrar_status(f'{len(rows)} cliente(s) encontrado(s) para "{termo}".')
        elif not rows:
            self.mostrar_status("Nenhum cliente cadastrado.")


if __name__ == "__main__":
    App().mainloop()
