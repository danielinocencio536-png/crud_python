"""
Etapa 4 - Interface gráfica com customtkinter (persistência em SQLite).

Instalar dependência:
    pip install customtkinter

Uso:
    python etapa4_interface.py
"""

import sqlite3
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
import types

try:
    import customtkinter as ctk
except ImportError:
    class CTk(tk.Tk):
        pass

    class CTkLabel(tk.Label):
        pass

    class CTkFrame(tk.Frame):
        pass

    class CTkEntry(tk.Entry):
        def __init__(self, master=None, placeholder_text=None, **kwargs):
            super().__init__(master, **kwargs)

    class CTkButton(tk.Button):
        def __init__(self, master=None, fg_color=None, hover_color=None, **kwargs):
            super().__init__(master, **kwargs)

    class CTkTextbox(tk.Text):
        pass

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
        CTkTextbox=CTkTextbox,
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


def deletar(id_cli):
    with conectar() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (id_cli,))


# ----------------- interface -----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Cadastro de Clientes")
        self.geometry("560x520")

        criar_tabela()

        # título
        ctk.CTkLabel(self, text="Cadastro de Clientes",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=12)

        # campos
        frame_form = ctk.CTkFrame(self)
        frame_form.pack(pady=8, padx=16, fill="x")

        self.entry_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome")
        self.entry_nome.pack(pady=4, padx=8, fill="x")

        self.entry_telefone = ctk.CTkEntry(frame_form, placeholder_text="Telefone")
        self.entry_telefone.pack(pady=4, padx=8, fill="x")

        self.entry_email = ctk.CTkEntry(frame_form, placeholder_text="Email")
        self.entry_email.pack(pady=4, padx=8, fill="x")

        # botões
        frame_btns = ctk.CTkFrame(self)
        frame_btns.pack(pady=8, padx=16, fill="x")

        ctk.CTkButton(frame_btns, text="Cadastrar", command=self.on_cadastrar).pack(
            side="left", expand=True, padx=4
        )
        ctk.CTkButton(frame_btns, text="Listar", command=self.on_listar).pack(
            side="left", expand=True, padx=4
        )
        ctk.CTkButton(frame_btns, text="Limpar", command=self.on_limpar).pack(
            side="left", expand=True, padx=4
        )
        ctk.CTkButton(frame_btns, text="Excluir selecionado",
                      fg_color="#a83232", hover_color="#7a2424",
                      command=self.on_excluir).pack(side="left", expand=True, padx=4)

        # lista
        self.textbox = ctk.CTkTextbox(self, height=240)
        self.textbox.pack(pady=8, padx=16, fill="both", expand=True)

        self.carregar_lista()

    # ---- ações ----
    def on_cadastrar(self):
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "O campo Nome é obrigatório.")
            return
        inserir(nome, telefone, email)
        self.on_limpar()
        self.carregar_lista()
        messagebox.showinfo("OK", f'Cliente "{nome}" cadastrado!')

    def on_listar(self):
        self.carregar_lista()

    def on_limpar(self):
        self.entry_nome.delete(0, "end")
        self.entry_telefone.delete(0, "end")
        self.entry_email.delete(0, "end")

    def on_excluir(self):
        # pega a linha selecionada no textbox
        try:
            sel = self.textbox.get("sel.first", "sel.last")
        except Exception:
            messagebox.showinfo("Selecione", "Selecione a linha do cliente na lista.")
            return
        primeira_linha = sel.splitlines()[0]
        try:
            id_cli = int(primeira_linha.split()[1])  # formato: "ID 3 - ..."
        except (IndexError, ValueError):
            messagebox.showerror("Erro", "Não foi possível identificar o ID.")
            return
        if messagebox.askyesno("Confirmar", f"Excluir cliente ID {id_cli}?"):
            deletar(id_cli)
            self.carregar_lista()

    def carregar_lista(self):
        self.textbox.delete("1.0", "end")
        rows = listar_todos()
        if not rows:
            self.textbox.insert("end", "Nenhum cliente cadastrado.\n")
            return
        for r in rows:
            self.textbox.insert("end", f"ID {r[0]} - {r[1]} | {r[2]} | {r[3]}\n")


if __name__ == "__main__":
    App().mainloop()
