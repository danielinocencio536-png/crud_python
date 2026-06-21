# Sistema de Cadastro (CRUD) - 4 Etapas

Projeto para aprender programação na prática, evoluindo do console até uma interface gráfica.

## Estrutura

| Arquivo                | Etapa   | O que aprende                                              |
|------------------------|---------|------------------------------------------------------------|
| `etapa1_console.py`    | Etapa 1 | Variáveis, listas, loops, funções, condicionais           |
| `etapa2_arquivo.py`    | Etapa 2 | `open()` - persistência em `clientes.txt`                  |
| `etapa3_sqlite.py`     | Etapa 3 | `sqlite3` - INSERT, SELECT, UPDATE, DELETE                 |
| `etapa4_interface.py`  | Etapa 4 | `customtkinter` - botões, campos, janela                    |

## Como rodar

### Etapas 1, 2 e 3 (apenas Python padrão)
```bash
python etapa1_console.py
python etapa2_arquivo.py
python etapa3_sqlite.py
```

### Etapa 4 (interface)
```bash
pip install customtkinter
python etapa4_interface.py
```

## O que o sistema faz
- Cadastrar cliente (Nome, Telefone, Email)
- Listar clientes
- Buscar cliente
- Excluir cliente
- Sair

## Evolução

- **Etapa 1** → tudo em memória (some ao fechar)
- **Etapa 2** → salva em `clientes.txt` (texto puro)
- **Etapa 3** → banco SQLite `clientes.db` (banco de dados real)
- **Etapa 4** → interface gráfica amigável com `customtkinter`
