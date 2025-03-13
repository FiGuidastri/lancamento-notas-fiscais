import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurações de estilo
LARGURA_JANELA = 800
ALTURA_JANELA = 600
COR_FUNDO = "#f0f0f0"
FONTE_TITULO = ("Arial", 14, "bold")
FONTE_NORMAL = ("Arial", 12)

def centralizar_janela(janela):
    # Centraliza a janela na tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela - LARGURA_JANELA) // 2
    y = (altura_tela - ALTURA_JANELA) // 2
    janela.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{x}+{y}")

# Função para salvar os dados no Excel
def salvar_dados():
    # Acessa os campos globalmente
    global entry_responsavel, entry_numero_nota, entry_fornecedor, entry_valor_total, entry_data_emissao, entry_condicao_pagamento

    responsavel = entry_responsavel.get()
    numero_nota = entry_numero_nota.get()
    fornecedor = entry_fornecedor.get()
    valor_total = entry_valor_total.get()
    data_emissao = entry_data_emissao.get()
    condicao_pagamento = entry_condicao_pagamento.get()

    # Verifica se todos os campos obrigatórios foram preenchidos
    if not all([responsavel, numero_nota, fornecedor, valor_total, data_emissao, condicao_pagamento]):
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
        return

    # Calcula a data de vencimento
    try:
        condicao_pagamento_dias = int(condicao_pagamento)
        data_vencimento = (datetime.strptime(data_emissao, "%d/%m/%Y") + timedelta(days=condicao_pagamento_dias)).strftime("%d/%m/%Y")
    except ValueError:
        data_vencimento = ""

    # Cria um DataFrame com os dados
    novo_registro = pd.DataFrame([{
        "Responsável": responsavel,
        "Numero da nota": numero_nota,
        "Fornecedor": fornecedor,
        "Valor total": valor_total,
        "Emissão da nota": data_emissao,
        "Condição de Pagamento": condicao_pagamento,
        "Data vencimento": data_vencimento,
        "Requisição": "",
        "Aprovação RC": "",
        "Pedido": "",
        "Protocolo": "",
        "Lançamento": ""
    }])

    # Verifica se o arquivo Excel já existe
    if os.path.exists("notas.xlsx"):
        df = pd.read_excel("notas.xlsx")
        df = pd.concat([df, novo_registro], ignore_index=True)
    else:
        df = novo_registro

    # Salva o DataFrame no arquivo Excel
    df.to_excel("notas.xlsx", index=False)
    messagebox.showinfo("Sucesso", "Nota salva com sucesso!")

# Função para editar uma nota
def editar_nota():
    messagebox.showinfo("Editar Nota", "Funcionalidade de edição ainda não implementada.")

def criar_frame_central(parent):
    # Cria um frame centralizado
    frame = tk.Frame(parent, bg=COR_FUNDO)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    return frame

# Função para abrir a tela de inserção de nota
def abrir_tela_inserir():
    limpar_tela()
    frame = criar_frame_central(root)
    
    # Campos do formulário
    tk.Label(frame, text="Responsável:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=0, column=0, pady=5, sticky="e")
    global entry_responsavel
    entry_responsavel = tk.Entry(frame, font=FONTE_NORMAL)
    entry_responsavel.grid(row=0, column=1, pady=5)
    entry_responsavel.insert(0, os.getlogin())

    tk.Label(frame, text="Número da Nota:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=1, column=0, pady=5, sticky="e")
    global entry_numero_nota
    entry_numero_nota = tk.Entry(frame, font=FONTE_NORMAL)
    entry_numero_nota.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Fornecedor:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=2, column=0, pady=5, sticky="e")
    global entry_fornecedor
    entry_fornecedor = tk.Entry(frame, font=FONTE_NORMAL)
    entry_fornecedor.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Valor Total:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=3, column=0, pady=5, sticky="e")
    global entry_valor_total
    entry_valor_total = tk.Entry(frame, font=FONTE_NORMAL)
    entry_valor_total.grid(row=3, column=1, pady=5)

    tk.Label(frame, text="Data de Emissão (dd/mm/aaaa):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=4, column=0, pady=5, sticky="e")
    global entry_data_emissao
    entry_data_emissao = tk.Entry(frame, font=FONTE_NORMAL)
    entry_data_emissao.grid(row=4, column=1, pady=5)

    tk.Label(frame, text="Condição de Pagamento (dias):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=5, column=0, pady=5, sticky="e")
    global entry_condicao_pagamento
    entry_condicao_pagamento = tk.Entry(frame, font=FONTE_NORMAL)
    entry_condicao_pagamento.grid(row=5, column=1, pady=5)

    # Botões
    botoes_frame = tk.Frame(frame, bg=COR_FUNDO)
    botoes_frame.grid(row=6, column=0, columnspan=2, pady=20)
    tk.Button(botoes_frame, text="Salvar", command=salvar_dados, font=FONTE_NORMAL, width=10).pack(side="left", padx=10)
    tk.Button(botoes_frame, text="Voltar", command=voltar_tela_inicial, font=FONTE_NORMAL, width=10).pack(side="left", padx=10)

def abrir_tela_editar():
    limpar_tela()
    frame = criar_frame_central(root)
    tk.Label(frame, text="Funcionalidade de edição ainda não implementada.", font=FONTE_NORMAL, bg=COR_FUNDO).pack(pady=20)
    tk.Button(frame, text="Voltar", command=voltar_tela_inicial, font=FONTE_NORMAL, width=10).pack()

def limpar_tela():
    for widget in root.winfo_children():
        widget.destroy()

def voltar_tela_inicial():
    limpar_tela()
    frame = criar_frame_central(root)
    root.title("Sistema de Lançamento de Notas Fiscais")
    
    tk.Label(frame, text="Selecione uma opção:", font=FONTE_TITULO, bg=COR_FUNDO).pack(pady=20)
    
    botoes_frame = tk.Frame(frame, bg=COR_FUNDO)
    botoes_frame.pack(pady=10)
    
    tk.Button(botoes_frame, text="Inserir Nota", command=abrir_tela_inserir, font=FONTE_NORMAL, width=15).pack(pady=10)
    tk.Button(botoes_frame, text="Editar Nota", command=abrir_tela_editar, font=FONTE_NORMAL, width=15).pack(pady=10)

# Configuração da janela principal
root = tk.Tk()
root.title("Sistema de Lançamento de Notas Fiscais")
root.configure(bg=COR_FUNDO)
centralizar_janela(root)
root.resizable(False, False)  # Desabilita redimensionamento

voltar_tela_inicial()
root.mainloop()