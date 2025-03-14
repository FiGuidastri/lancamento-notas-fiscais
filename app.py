import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import traceback

# Configurações de estilo
LARGURA_JANELA = 800
ALTURA_JANELA = 600
COR_FUNDO = "#f0f0f0"
FONTE_TITULO = ("Roboto", 14, "bold")
FONTE_NORMAL = ("Roboto", 12)

PARQUET_FILE = "notas.parquet"

def centralizar_janela(janela):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela - LARGURA_JANELA) // 2
    y = (altura_tela - ALTURA_JANELA) // 2
    janela.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}+{x}+{y}")

# Função para limpar os campos de entrada
def limpar_campos():
    global entry_responsavel, entry_numero_nota, entry_fornecedor, entry_valor_total, entry_data_emissao, entry_condicao_pagamento
    entry_responsavel.delete(0, tk.END)
    entry_numero_nota.delete(0, tk.END)
    entry_fornecedor.delete(0, tk.END)
    entry_valor_total.delete(0, tk.END)
    entry_data_emissao.delete(0, tk.END)
    entry_condicao_pagamento.delete(0, tk.END)

# Função para salvar os dados no formato Parquet
def salvar_dados():
    global entry_responsavel, entry_numero_nota, entry_fornecedor, entry_valor_total, entry_data_emissao, entry_condicao_pagamento

    responsavel = entry_responsavel.get()
    numero_nota = entry_numero_nota.get()
    fornecedor = entry_fornecedor.get()
    valor_total = entry_valor_total.get()
    data_emissao = entry_data_emissao.get()
    condicao_pagamento = entry_condicao_pagamento.get()

    if not all([responsavel, numero_nota, fornecedor, valor_total, data_emissao, condicao_pagamento]):
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
        return

    try:
        condicao_pagamento_dias = int(condicao_pagamento)
        data_vencimento = (datetime.strptime(data_emissao, "%d/%m/%Y") + timedelta(days=condicao_pagamento_dias)).strftime("%d/%m/%Y")
    except ValueError:
        data_vencimento = ""

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

    if os.path.exists(PARQUET_FILE):
        df = pd.read_parquet(PARQUET_FILE)
        df = pd.concat([df, novo_registro], ignore_index=True)
    else:
        df = novo_registro

    df.to_parquet(PARQUET_FILE, index=False)
    limpar_campos()
    messagebox.showinfo("Sucesso", "Nota salva com sucesso!")

# Função para exibir todas as notas em uma nova janela
def exibir_notas():
    if not os.path.exists(PARQUET_FILE):
        messagebox.showinfo("Informação", "Nenhuma nota cadastrada.")
        return

    df = pd.read_parquet(PARQUET_FILE)

    # Criar nova janela
    janela_notas = tk.Toplevel(root)
    janela_notas.title("Notas Cadastradas")
    janela_notas.config(bg=COR_FUNDO)
    centralizar_janela(janela_notas)

    # Frame para conter a tabela e as barras de rolagem
    frame_tabela = tk.Frame(janela_notas, bg=COR_FUNDO)
    frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)

    # Criar Treeview para exibir os dados
    colunas = list(df.columns)
    tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", selectmode="browse")
    tree.grid(row=0, column=0, sticky="nsew")

    # Adicionar barra de rolagem vertical
    scrollbar_vertical = ttk.Scrollbar(frame_tabela, orient="vertical", command=tree.yview)
    scrollbar_vertical.grid(row=0, column=1, sticky="ns")

    # Adicionar barra de rolagem horizontal
    scrollbar_horizontal = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tree.xview)
    scrollbar_horizontal.grid(row=1, column=0, sticky="ew")

    tree.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    # Configurar cabeçalhos
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    # Inserir dados na tabela
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Configurar redimensionamento
    frame_tabela.grid_rowconfigure(0, weight=1)
    frame_tabela.grid_columnconfigure(0, weight=1)

    # Frame para botões
    botoes_frame = tk.Frame(janela_notas, bg=COR_FUNDO)
    botoes_frame.pack(pady=10)

    def editar_selecionado():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma nota para editar!")
            return
            
        try:
            # Debug: Verificar estrutura do DataFrame
            print("Colunas do DataFrame:", df.columns.tolist())
            print("Primeira linha do DataFrame:", df.iloc[0].tolist())
            
            # Obter índice dinâmico
            colunas_df = df.columns.tolist()
            indice_coluna = colunas_df.index("Numero da nota")
            
            # Obter valor da treeview
            item = tree.item(selecionado[0])
            valor_tree = item['values'][indice_coluna]
            print(f"Valor obtido da tree: {valor_tree} (Tipo: {type(valor_tree)})")
            
            # Converter para tipo correto
            valor_df = df["Numero da nota"].iloc[0]
            if isinstance(valor_df, (int, float)):
                numero_nota = int(valor_tree)
            else:
                numero_nota = str(valor_tree)
                
            print(f"Valor convertido: {numero_nota} (Tipo: {type(numero_nota)})")
            
            # Verificar existência
            if numero_nota not in df["Numero da nota"].values:
                raise ValueError(f"Nota {numero_nota} não existe no DataFrame")
            
            janela_notas.destroy()
            editar_nota(numero_nota)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha crítica: {str(e)}")
            print(traceback.format_exc())
            
    tk.Button(botoes_frame, text="Editar Selecionada", command=editar_selecionado, font=FONTE_NORMAL).pack(side="left", padx=10)
    tk.Button(botoes_frame, text="Fechar", command=janela_notas.destroy, font=FONTE_NORMAL).pack(side="left", padx=10)
    
# Função para editar uma nota
def editar_nota(numero_nota=None):
    # Verificar se o arquivo existe ou está vazio
    if not os.path.exists(PARQUET_FILE):
        messagebox.showinfo("Informação", "Nenhuma nota cadastrada.")
        return
    df = pd.read_parquet(PARQUET_FILE)
    if df.empty:
        messagebox.showinfo("Informação", "Nenhuma nota cadastrada.")
        return

    # Se já veio com o número da nota, pula a seleção
    if numero_nota:
        carregar_dados_editar(numero_nota, df)
        return

    limpar_tela()
    frame = criar_frame_central(root)
    
    tk.Label(frame, text="Selecione a nota a ser editada:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=0, column=0, pady=5, sticky="e")
    
    lista_notas = df["Numero da nota"].tolist()
    nota_selecionada = tk.StringVar()

    tk.OptionMenu(frame, nota_selecionada, *lista_notas).grid(row=0, column=1, pady=5)
    tk.Button(frame, text="Carregar Nota", command=lambda: carregar_dados_editar(nota_selecionada.get(), df), font=FONTE_NORMAL).grid(row=1, column=1, pady=10)

    tk.Button(frame, text="Voltar", command=voltar_tela_inicial, font=FONTE_NORMAL, width=10).grid(row=2, column=0, pady=20)

def carregar_dados_editar(nota_selecionada, df):
    try:
        # Debug: Verificar tipos
        print("\n--- DEBUG CARREGAR DADOS ---")
        print(f"Tipo da nota recebida: {type(nota_selecionada)}")
        print(f"Tipo no DataFrame: {df['Numero da nota'].dtype}")
        print(f"Valores únicos: {df['Numero da nota'].unique()[:5]}")
        
        # Converter tipos
        if df['Numero da nota'].dtype != object:
            df['Numero da nota'] = df['Numero da nota'].astype(type(nota_selecionada))
            
        # Buscar nota
        mask = df['Numero da nota'] == nota_selecionada
        if not mask.any():
            raise ValueError(f"Nenhuma nota com número {nota_selecionada}")
            
        nota_data = df[mask].iloc[0]

        # Criar tela de edição
        limpar_tela()
        frame = criar_frame_central(root)
        
        # Preencher os campos com os dados atuais
        tk.Label(frame, text="Número da Nota:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=0, column=0, pady=5, sticky="e")
        global entry_numero_nota
        entry_numero_nota = tk.Entry(frame, font=FONTE_NORMAL)
        entry_numero_nota.grid(row=0, column=1, pady=5)
        entry_numero_nota.insert(0, nota_data["Numero da nota"])

        tk.Label(frame, text="Fornecedor:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=1, column=0, pady=5, sticky="e")
        global entry_fornecedor
        entry_fornecedor = tk.Entry(frame, font=FONTE_NORMAL)
        entry_fornecedor.grid(row=1, column=1, pady=5)
        entry_fornecedor.insert(0, nota_data["Fornecedor"])

        tk.Label(frame, text="Valor Total:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=2, column=0, pady=5, sticky="e")
        global entry_valor_total
        entry_valor_total = tk.Entry(frame, font=FONTE_NORMAL)
        entry_valor_total.grid(row=2, column=1, pady=5)
        entry_valor_total.insert(0, nota_data["Valor total"])

        tk.Label(frame, text="Data de Emissão (dd/mm/aaaa):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=3, column=0, pady=5, sticky="e")
        global entry_data_emissao
        entry_data_emissao = tk.Entry(frame, font=FONTE_NORMAL)
        entry_data_emissao.grid(row=3, column=1, pady=5)
        entry_data_emissao.insert(0, nota_data["Emissão da nota"])

        tk.Label(frame, text="Condição de Pagamento (dias):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=4, column=0, pady=5, sticky="e")
        global entry_condicao_pagamento
        entry_condicao_pagamento = tk.Entry(frame, font=FONTE_NORMAL)
        entry_condicao_pagamento.grid(row=4, column=1, pady=5)
        entry_condicao_pagamento.insert(0, nota_data["Condição de Pagamento"])

        tk.Label(frame, text="Número da Requisição:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=5, column=0, pady=5, sticky="e")
        global entry_requisicao
        entry_requisicao = tk.Entry(frame, font=FONTE_NORMAL)
        entry_requisicao.grid(row=5, column=1, pady=5)
        entry_requisicao.insert(0, nota_data["Requisição"])

        tk.Label(frame, text="Número do Pedido:", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=6, column=0, pady=5, sticky="e")
        global entry_pedido
        entry_pedido = tk.Entry(frame, font=FONTE_NORMAL)
        entry_pedido.grid(row=6, column=1, pady=5)
        entry_pedido.insert(0, nota_data["Pedido"])

        tk.Label(frame, text="Data Protocolada (dd/mm/aaaa):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=7, column=0, pady=5, sticky="e")
        global entry_data_protocolada
        entry_data_protocolada = tk.Entry(frame, font=FONTE_NORMAL)
        entry_data_protocolada.grid(row=7, column=1, pady=5)
        entry_data_protocolada.insert(0, nota_data["Protocolo"])

        tk.Label(frame, text="Data de Aprovação RC (dd/mm/aaaa):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=8, column=0, pady=5, sticky="e")
        global entry_data_aprovacao  # Declarar como global
        entry_data_aprovacao = tk.Entry(frame, font=FONTE_NORMAL)
        entry_data_aprovacao.grid(row=8, column=1, pady=5)
        entry_data_aprovacao.insert(0, nota_data["Aprovação RC"])

        tk.Label(frame, text="Data de Lançamento (dd/mm/aaaa):", font=FONTE_NORMAL, bg=COR_FUNDO).grid(row=9, column=0, pady=5, sticky="e")
        global entry_data_lancamento  # Declarar como global
        entry_data_lancamento = tk.Entry(frame, font=FONTE_NORMAL)
        entry_data_lancamento.grid(row=9, column=1, pady=5)
        entry_data_lancamento.insert(0, nota_data["Lançamento"])

        # Botões de salvar e voltar
        botoes_frame = tk.Frame(frame, bg=COR_FUNDO)
        botoes_frame.grid(row=10, column=0, columnspan=2, pady=20)
        tk.Button(botoes_frame, text="Salvar", command=lambda: salvar_edicao(nota_selecionada, df), font=FONTE_NORMAL, width=10).pack(side="left", padx=10)
        tk.Button(botoes_frame, text="Voltar", command=voltar_tela_inicial, font=FONTE_NORMAL, width=10).pack(side="left", padx=10)
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro crítico: {str(e)}")
        print(traceback.format_exc())
        voltar_tela_inicial()


def salvar_edicao(nota_selecionada, df):
    # Atualizar os dados no DataFrame com os novos valores dos campos
    global entry_numero_nota, entry_fornecedor, entry_valor_total, entry_data_emissao, entry_condicao_pagamento
    global entry_requisicao, entry_pedido, entry_data_protocolada, entry_data_aprovacao, entry_data_lancamento  # Declarar como global

    df.loc[df["Numero da nota"] == nota_selecionada, "Numero da nota"] = entry_numero_nota.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Fornecedor"] = entry_fornecedor.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Valor total"] = entry_valor_total.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Emissão da nota"] = entry_data_emissao.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Condição de Pagamento"] = entry_condicao_pagamento.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Requisição"] = entry_requisicao.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Pedido"] = entry_pedido.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Protocolo"] = entry_data_protocolada.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Aprovação RC"] = entry_data_aprovacao.get()
    df.loc[df["Numero da nota"] == nota_selecionada, "Lançamento"] = entry_data_lancamento.get()

    df.to_parquet(PARQUET_FILE, index=False)
    messagebox.showinfo("Sucesso", "Nota editada com sucesso!")
    limpar_campos_editados()
    
        # Fechar qualquer janela residual
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()
    
    exibir_notas()


def limpar_campos_editados():
    # Limpar campos de forma controlada após a edição
    global entry_numero_nota, entry_fornecedor, entry_valor_total, entry_data_emissao, entry_condicao_pagamento
    global entry_requisicao, entry_pedido, entry_data_protocolada, entry_comentario  # Declarar como global

    entry_numero_nota.delete(0, tk.END)
    entry_fornecedor.delete(0, tk.END)
    entry_valor_total.delete(0, tk.END)
    entry_data_emissao.delete(0, tk.END)
    entry_condicao_pagamento.delete(0, tk.END)
    entry_requisicao.delete(0, tk.END)
    entry_pedido.delete(0, tk.END)
    entry_data_protocolada.delete(0, tk.END)
    entry_comentario.delete(0, tk.END)  # Agora está definido corretamente

def criar_frame_central(parent):
    frame = tk.Frame(parent, bg=COR_FUNDO)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    return frame

def limpar_tela():
    for widget in root.winfo_children():
        widget.destroy()

def voltar_tela_inicial():
    # Fechar qualquer janela de notas aberta
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()
            
    limpar_tela()
    frame = criar_frame_central(root)
    root.title("Sistema de Lançamento de Notas Fiscais")
    
    tk.Label(frame, text="Selecione uma opção:", font=FONTE_TITULO, bg=COR_FUNDO).pack(pady=20)
    
    botoes_frame = tk.Frame(frame, bg=COR_FUNDO)
    botoes_frame.pack(pady=10)
    
    tk.Button(botoes_frame, text="Inserir Nota", command=abrir_tela_inserir, font=FONTE_NORMAL, width=15).pack(pady=10)
    tk.Button(botoes_frame, text="Editar Nota", command=editar_nota, font=FONTE_NORMAL, width=15).pack(pady=10)
    tk.Button(botoes_frame, text="Exibir Notas", command=exibir_notas, font=FONTE_NORMAL, width=15).pack(pady=10)

def abrir_tela_inserir():
    limpar_tela()
    frame = criar_frame_central(root)
    
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

    tk.Button(frame, text="Salvar", command=salvar_dados, font=FONTE_NORMAL).grid(row=6, column=1, pady=20)
    tk.Button(frame, text="Voltar", command=voltar_tela_inicial, font=FONTE_NORMAL).grid(row=6, column=0, pady=20)

# Iniciar a janela principal
root = tk.Tk()
root.title("Sistema de Lançamento de Notas Fiscais")
root.config(bg=COR_FUNDO)
centralizar_janela(root)

# Exibir a tela inicial
voltar_tela_inicial()

root.mainloop()