import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('vendas.db')
cursor = conn.cursor()

# Criação da tabela de vendas com uma chave estrangeira para a tabela de data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco REAL NOT NULL
    )
''')

try:
    cursor.execute("ALTER TABLE vendas ADD COLUMN data_id INTEGER")
except sqlite3.OperationalError:
    pass  # Ignora o erro se a coluna já existir

cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY,
        data TEXT NOT NULL
    )
''')
conn.commit()

# Função para adicionar um item
def adicionar_item():
    nome = nome_entry.get()
    quantidade = int(quantidade_entry.get())
    preco = float(preco_entry.get())
    data = datetime.now().strftime("%d-%m-%Y")

    if nome and quantidade > 0 and preco > 0:
        cursor.execute("INSERT INTO data (data) VALUES (?)", (data,))
        data_id = cursor.lastrowid
        cursor.execute("INSERT INTO vendas (nome, quantidade, preco, data_id) VALUES (?, ?, ?, ?)", 
                       (nome, quantidade, preco, data_id))
        conn.commit()
        messagebox.showinfo("Sucesso", "Item adicionado com sucesso!")
        atualizar_lista()
    else:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos corretamente.")
    
    nome_entry.delete(0, tk.END)
    quantidade_entry.delete(0, tk.END)
    preco_entry.delete(0, tk.END)

# Função para atualizar a lista de itens
def atualizar_lista():
    lista_estoque.delete(0, tk.END)
    cursor.execute('''
        SELECT vendas.id, vendas.nome, vendas.quantidade, vendas.preco, data.data
        FROM vendas
        JOIN data ON vendas.data_id = data.id
    ''')
    for row in cursor.fetchall():
        preco_total = row[2] * row[3]
        lista_estoque.insert(tk.END, f"ID: {row[0]} | Nome: {row[1]} | Quantidade: {row[2]} | "
                                     f"Preço: R${row[3]:.2f} | Data: {row[4]} | Preço Total: R${preco_total:.2f}")
    atualizar_preco_total_do_dia()

# Função para atualizar o preço total do dia
def atualizar_preco_total_do_dia():
    data_atual = datetime.now().strftime("%d-%m-%Y")
    cursor.execute('''
        SELECT SUM(vendas.quantidade * vendas.preco)
        FROM vendas
        JOIN data ON vendas.data_id = data.id
        WHERE data.data = ?
    ''', (data_atual,))
    preco_total_dia = cursor.fetchone()[0]
    if preco_total_dia is None:
        preco_total_dia = 0.0
    label_preco_total['text'] = f"Preço Total: R${preco_total_dia:.2f}"

# Função para calcular o preço total para uma data selecionada
def calcular_preco_total_para_data():
    data_selecionada = data_entry.get()
    try:
        cursor.execute('''
            SELECT SUM(vendas.quantidade * vendas.preco)
            FROM vendas
            JOIN data ON vendas.data_id = data.id
            WHERE data.data = ?
        ''', (data_selecionada,))
        preco_total = cursor.fetchone()[0]
        if preco_total is None:
            preco_total = 0.0
        label_preco_total_selecionada['text'] = f"Preço Total para {data_selecionada}: R${preco_total:.2f}"
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao calcular o preço total: {str(e)}")

# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Controle de Vendas")
root.geometry("800x600")
root.configure(bg="#f2f2f2")

# Estilo de fonte
font_title = ("Arial", 14, "bold")
font_label = ("Arial", 12)
font_entry = ("Arial", 12)
font_button = ("Arial", 12, "bold")

# Frame para entrada de dados
frame_inputs = tk.Frame(root, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
frame_inputs.pack(pady=10, padx=10, fill="x")

tk.Label(frame_inputs, text="Nome do Item:", font=font_label, bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
nome_entry = tk.Entry(frame_inputs, font=font_entry)
nome_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_inputs, text="Quantidade:", font=font_label, bg="#ffffff").grid(row=1, column=0, sticky="w", pady=5)
quantidade_entry = tk.Entry(frame_inputs, font=font_entry)
quantidade_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_inputs, text="Preço (R$):", font=font_label, bg="#ffffff").grid(row=2, column=0, sticky="w", pady=5)
preco_entry = tk.Entry(frame_inputs, font=font_entry)
preco_entry.grid(row=2, column=1, padx=10, pady=5)

# Botões de ações
frame_buttons = tk.Frame(root, bg="#f2f2f2")
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="Adicionar Item", command=adicionar_item, font=font_button, bg="#4caf50", fg="#ffffff").grid(row=0, column=0, padx=10)
tk.Button(frame_buttons, text="Editar Item", command=atualizar_lista, font=font_button, bg="#2196f3", fg="#ffffff").grid(row=0, column=1, padx=10)
tk.Button(frame_buttons, text="Excluir Item", command=atualizar_lista, font=font_button, bg="#f44336", fg="#ffffff").grid(row=0, column=2, padx=10)

# Lista de estoque
frame_lista = tk.Frame(root, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
frame_lista.pack(pady=10, padx=10, fill="both", expand=True)

lista_estoque = tk.Listbox(frame_lista, font=font_entry, width=100, height=15)
lista_estoque.pack(fill="both", expand=True)

# Preço total do dia
frame_totais = tk.Frame(root, bg="#f2f2f2", padx=10, pady=10)
frame_totais.pack(fill="x")

label_preco_total = tk.Label(frame_totais, text="Preço Total: R$0.00", font=font_title, bg="#f2f2f2")
label_preco_total.pack(side="left", padx=10)

# Campo para calcular preço total de uma data específica
frame_data = tk.Frame(root, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
frame_data.pack(pady=10, padx=10, fill="x")

tk.Label(frame_data, text="Data (dd-mm-aaaa):", font=font_label, bg="#ffffff").grid(row=0, column=0, sticky="w", pady=5)
data_entry = tk.Entry(frame_data, font=font_entry)
data_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Button(frame_data, text="Calcular Preço Total", command=calcular_preco_total_para_data, font=font_button, bg="#4caf50", fg="#ffffff").grid(row=0, column=2, padx=10)

label_preco_total_selecionada = tk.Label(frame_data, text="Preço Total para Data Selecionada: R$0.00", font=font_title, bg="#ffffff")
label_preco_total_selecionada.grid(row=1, column=0, columnspan=3, pady=10)

# Atualizar a lista inicial
atualizar_lista()

# Executar a interface
root.mainloop()

# Fecha a conexão com o banco de dados ao encerrar o programa
conn.close()
