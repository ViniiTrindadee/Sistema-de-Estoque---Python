import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import qrcode # type: ignore
from PIL import ImageTk  # type: ignore

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('estoque.db')

# Criação da tabela de produtos se não existir
with conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL
        )
    ''')

# Função para adicionar um produto ao estoque
def adicionar_produto():
    nome = entry_nome.get()
    try:
        quantidade = int(entry_quantidade.get())
        if nome and quantidade >= 0:
            with conn:
                conn.execute('INSERT INTO produtos (nome, quantidade) VALUES (?, ?)', (nome, quantidade))
            messagebox.showinfo("Sucesso", f"Produto '{nome}' adicionado com sucesso!")
            atualizar_lista_produtos()
        else:
            messagebox.showwarning("Erro", "Por favor, insira um nome válido e uma quantidade não negativa.")
    except ValueError:
        messagebox.showwarning("Erro", "Por favor, insira um valor numérico para a quantidade.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar produto: {e}")

# Função para remover um produto do estoque
def remover_produto():
    nome = entry_nome.get()
    try:
        with conn:
            result = conn.execute('DELETE FROM produtos WHERE nome = ?', (nome,))
            if result.rowcount > 0:
                messagebox.showinfo("Sucesso", f"Produto '{nome}' removido com sucesso!")
            else:
                messagebox.showwarning("Erro", f"Produto '{nome}' não encontrado.")
        atualizar_lista_produtos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao remover produto: {e}")

# Função para retirar um produto do estoque
def retirar_produto():
    nome = entry_nome.get()
    try:
        quantidade = int(entry_quantidade.get())

        with conn:
            result = conn.execute('SELECT quantidade FROM produtos WHERE nome = ?', (nome,))
            produto = result.fetchone()

            if produto:
                nova_quantidade = produto[0] - quantidade

                if nova_quantidade >= 0:
                    conn.execute('UPDATE produtos SET quantidade = ? WHERE nome = ?', (nova_quantidade, nome))
                    messagebox.showinfo("Sucesso", f"{quantidade} unidades do produto '{nome}' retiradas com sucesso!")
                else:
                    messagebox.showwarning("Erro", "Quantidade insuficiente no estoque.")
            else:
                messagebox.showwarning("Erro", f"Produto '{nome}' não encontrado.")
        atualizar_lista_produtos()
    except ValueError:
        messagebox.showwarning("Erro", "Por favor, insira um valor numérico para a quantidade.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao retirar produto: {e}")

# Função para editar um produto existente no estoque
def editar_produto():
    nome = entry_nome.get()
    try:
        nova_quantidade = int(entry_quantidade.get())
        novo_nome = entry_novo_nome.get()

        if not novo_nome:
            novo_nome = nome

        if nome and nova_quantidade >= 0:
            with conn:
                result = conn.execute('UPDATE produtos SET nome = ?, quantidade = ? WHERE nome = ?', 
                                      (novo_nome, nova_quantidade, nome))
                if result.rowcount > 0:
                    messagebox.showinfo("Sucesso", f"Produto '{nome}' atualizado para '{novo_nome}' com {nova_quantidade} unidades!")
                else:
                    messagebox.showwarning("Erro", f"Produto '{nome}' não encontrado.")
            atualizar_lista_produtos()
        else:
            messagebox.showwarning("Erro", "Por favor, insira um nome válido e uma quantidade não negativa.")
    except ValueError:
        messagebox.showwarning("Erro", "Por favor, insira um valor numérico para a quantidade.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao editar produto: {e}")

# Função para buscar um produto no estoque
def buscar_produto():
    nome = entry_nome.get()
    try:
        with conn:
            result = conn.execute('SELECT quantidade FROM produtos WHERE nome = ?', (nome,))
            produto = result.fetchone()

            if produto:
                messagebox.showinfo("Produto Encontrado", f"Produto '{nome}' possui {produto[0]} unidades em estoque.")
            else:
                messagebox.showwarning("Erro", f"Produto '{nome}' não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar produto: {e}")

# Função para atualizar a lista de produtos na interface
def atualizar_lista_produtos():
    for row in tree.get_children():
        tree.delete(row)
    try:
        with conn:
            result = conn.execute('SELECT * FROM produtos')
            for row in result.fetchall():
                tree.insert("", tk.END, values=(row[1], row[2]))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar a lista de produtos: {e}")

# Função para gerar QR code de um produto
def gerar_qr_code_produto():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        nome = item['values'][0]
        quantidade = item['values'][1]
        qr_data = f"Produto: {nome}\nQuantidade: {quantidade}"
        qr = qrcode.make(qr_data)
        qr.show()
    else:
        messagebox.showwarning("Erro", "Por favor, selecione um produto na lista.")

# Função para gerar QR code do estoque inteiro
def gerar_qr_code_estoque():
    try:
        with conn:
            result = conn.execute('SELECT nome, quantidade FROM produtos')
            qr_data = "Estoque:\n"
            for row in result.fetchall():
                qr_data += f"{row[0]}: {row[1]} unidades\n"
            qr = qrcode.make(qr_data)
            qr.show()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar QR code do estoque: {e}")

# Interface gráfica usando tkinter
root = tk.Tk()
root.title("Controle de Estoque")

# Título
titulo = tk.Label(root, text="Controle de Estoque", font=("Helvetica", 16))
titulo.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

# Nome do produto
tk.Label(frame, text="Nome do Produto").grid(row=0, column=0)
entry_nome = tk.Entry(frame)
entry_nome.grid(row=0, column=1, padx=10, pady=5)

# Quantidade do produto
tk.Label(frame, text="Quantidade").grid(row=1, column=0)
entry_quantidade = tk.Entry(frame)
entry_quantidade.grid(row=1, column=1, padx=10, pady=5)

# Novo nome do produto (para edição)
tk.Label(frame, text="Novo Nome (opcional)").grid(row=2, column=0)
entry_novo_nome = tk.Entry(frame)
entry_novo_nome.grid(row=2, column=1, padx=10, pady=5)

# Botões de ação
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

btn_adicionar = tk.Button(btn_frame, text="Adicionar Produto", command=adicionar_produto, width=25)
btn_adicionar.grid(row=0, column=0, padx=5, pady=5)

btn_remover = tk.Button(btn_frame, text="Remover Produto", command=remover_produto, width=25)
btn_remover.grid(row=0, column=1, padx=5, pady=5)

btn_retirar = tk.Button(btn_frame, text="Retirar Produto", command=retirar_produto, width=25)
btn_retirar.grid(row=1, column=0, padx=5, pady=5)

btn_editar = tk.Button(btn_frame, text="Editar Produto", command=editar_produto, width=25)
btn_editar.grid(row=1, column=1, padx=5, pady=5)

btn_buscar = tk.Button(btn_frame, text="Buscar Produto", command=buscar_produto, width=25)
btn_buscar.grid(row=2, column=0, padx=5, pady=5)

btn_qr_produto = tk.Button(btn_frame, text="Gerar QR Code do Produto", command=gerar_qr_code_produto, width=25)
btn_qr_produto.grid(row=2, column=1, padx=5, pady=5)

btn_qr_estoque = tk.Button(btn_frame, text="Gerar QR Code do Estoque", command=gerar_qr_code_estoque, width=52)
btn_qr_estoque.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Lista de produtos usando Treeview
tree = ttk.Treeview(root, columns=("nome", "quantidade"), show="headings")
tree.heading("nome", text="Nome do Produto")
tree.heading("quantidade", text="Quantidade")
tree.column("nome", anchor="center")
tree.column("quantidade", anchor="center")
tree.pack(pady=20)

# Inicializar a lista de produtos na interface
atualizar_lista_produtos()

# Executar o aplicativo
root.mainloop()