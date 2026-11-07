import tkinter as tk
from tkinter import ttk, messagebox

# ==============================================================================
# MÓDULO DE LÓGICA E CÁLCULO (PROGRAMAÇÃO ESTRUTURADA - IPE)
# ==============================================================================

def obter_fator_emissao(matriz_energetica):
    """
    Estrutura condicional que retorna o fator de emissão (kg CO2 por litro ou kWh)
    baseado nas diretrizes do IPCC e do Programa Brasileiro GHG Protocol.
    """
    if matriz_energetica == "1 - Óleo Diesel Comercial (S10)":
        return 2.60  # kg CO2 por litro
    elif matriz_energetica == "2 - Gasolina Comum":
        return 2.27  # kg CO2 por litro
    elif matriz_energetica == "3 - Etanol Hidratado / Biocombustível":
        return 0.45  # kg CO2 equivalente residual por litro
    elif matriz_energetica == "4 - Veículo 100% Elétrico (Escopo 1 Zero)":
        return 0.00  # Emissão direta zero no escapamento
    else:
        return 2.60


def calcular_emissao_frota(qtd_veiculos, distancia_km, consumo_l_km, fator_emissao):
    """
    Aplica a equação matemática de inventário móvel:
    E_CO2 = (D * C * Fe) / 1000 (multiplicado pelo total de veículos da frota).
    Retorna o total emitido em toneladas de CO2 equivalente (tCO2e).
    """
    emissao_por_veiculo = (distancia_km * consumo_l_km * fator_emissao) / 1000.0
    emissao_total_toneladas = emissao_por_veiculo * qtd_veiculos
    return emissao_total_toneladas


def executar_calculo():
    """
    Função principal acionada pelo botão da interface gráfica.
    Realiza a leitura dos dados, tratamento de exceções, cálculos de compensação
    e estimativa de lucro com excedentes de créditos de carbono.
    """
    try:
        # 1. Entrada de Dados a partir da Interface Gráfica
        matriz_atual = combo_combustivel.get()
        qtd_veiculos = int(entry_veiculos.get())
        distancia_anual = float(entry_distancia.get().replace(",", "."))
        consumo_medio = float(entry_consumo.get().replace(",", "."))
        meta_emissao = float(entry_meta.get().replace(",", "."))
        cotacao_credito = float(entry_cotacao.get().replace(",", "."))

        # Validação lógica de valores positivos
        if (qtd_veiculos <= 0 or distancia_anual <= 0 or 
            consumo_medio < 0 or meta_emissao < 0 or cotacao_credito <= 0):
            messagebox.showwarning(
                "Atenção aos Dados",
                "Por favor, insira apenas valores numéricos maiores que zero."
            )
            return

        # 2. Processamento das Emissões Atuais (Cenário Fóssil/Atual)
        fator_atual = obter_fator_emissao(matriz_atual)
        emissao_atual = calcular_emissao_frota(
            qtd_veiculos, distancia_anual, consumo_medio, fator_atual
        )

        # 3. Processamento do Cenário de Transição (Frota 100% Elétrica)
        # No Brasil (SIN renovável), considera-se Escopo 1 zero e Escopo 2 residual
        fator_eletrico_residual = 0.04  # kg CO2e equivalente indireto por unidade
        emissao_eletrica = calcular_emissao_frota(
            qtd_veiculos, distancia_anual, consumo_medio, fator_eletrico_residual
        )

        # 4. Cálculo de Créditos de Carbono e Impacto Financeiro
        # 1 Crédito de Carbono = 1 tonelada de CO2e (tCO2e)
        custo_compensacao_total = emissao_atual * cotacao_credito
        reducao_transicao = max(0.0, emissao_atual - emissao_eletrica)
        lucro_transicao_eletrica = reducao_transicao * cotacao_credito

        # Avaliação em relação à Meta Corporativa (Cap and Trade)
        balanco_meta = meta_emissao - emissao_atual
        if balanco_meta < 0:
            creditos_deficit = abs(balanco_meta)
            custo_deficit = creditos_deficit * cotacao_credito
            status_meta = (
                f"DÉFICIT AMBIENTAL: Emitiu {creditos_deficit:.2f} tCO2e acima da meta.\n"
                f"Compensação Obrigatória: Comprar {creditos_deficit:.2f} créditos "
                f"(Custo: R$ {custo_deficit:,.2f})."
            )
            cor_status = "#B71C1C"  # Vermelho alerta
        else:
            creditos_excedentes = balanco_meta
            lucro_excedente_meta = creditos_excedentes * cotacao_credito
            status_meta = (
                f"SUPERÁVIT AMBIENTAL: Operou {creditos_excedentes:.2f} tCO2e abaixo da meta!\n"
                f"Excedente Gerado: {creditos_excedentes:.2f} créditos "
                f"(Lucro Potencial: R$ {lucro_excedente_meta:,.2f})."
            )
            cor_status = "#1B5E20"  # Verde sustentável

        # 5. Atualização dos Resultados na Interface Gráfica
        lbl_res_atual.config(
            text=f"{emissao_atual:,.2f} tCO2e / ano"
        )
        lbl_res_custo_comp.config(
            text=f"R$ {custo_compensacao_total:,.2f} (para neutralizar 100%)"
        )
        lbl_res_eletrica.config(
            text=f"{emissao_eletrica:,.2f} tCO2e / ano (Redução de {reducao_transicao:,.2f} tCO2e)"
        )
        lbl_res_lucro_transicao.config(
            text=f"{reducao_transicao:,.2f} Créditos | Receita: R$ {lucro_transicao_eletrica:,.2f}"
        )
        lbl_status_final.config(text=status_meta, fg=cor_status)

    except ValueError:
        messagebox.showerror(
            "Erro de Entrada",
            "Dado incompatível detectado! Certifique-se de preencher todos os "
            "campos utilizando apenas números válidos."
        )


def limpar_dados():
    """Limpa todos os campos de entrada e redefine o painel de resultados."""
    combo_combustivel.current(0)
    for campo in [entry_veiculos, entry_distancia, entry_consumo, entry_meta, entry_cotacao]:
        campo.delete(0, tk.END)
    
    # Restaura valores padrão de exemplo para facilitar testes rápidos
    entry_veiculos.insert(0, "15")
    entry_distancia.insert(0, "60000")
    entry_consumo.insert(0, "0.32")
    entry_meta.insert(0, "500")
    entry_cotacao.insert(0, "75.00")

    lbl_res_atual.config(text="0.00 tCO2e / ano")
    lbl_res_custo_comp.config(text="R$ 0.00")
    lbl_res_eletrica.config(text="0.00 tCO2e / ano")
    lbl_res_lucro_transicao.config(text="0.00 Créditos | R$ 0.00")
    lbl_status_final.config(
        text="Aguardando simulação... Preencha os dados e clique em Calcular.",
        fg="#37474F"
    )


# ==============================================================================
# CONSTRUÇÃO DA INTERFACE GRÁFICA (GUI - TKINTER / TTK)
# ==============================================================================

janela = tk.Tk()
janela.title("EcoFleet Analytics - Calculadora de Crédito de Carbono e Transição de Frotas")
janela.geometry("760x680")
janela.configure(bg="#F4F7F6")
janela.resizable(False, False)

# Configuração de Estilos Visuais
estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TCombobox", fieldbackground="white", background="#E0E0E0")

# Cabeçalho Superior (Banner Institucional)
frame_topo = tk.Frame(janela, bg="#1B4332", height=85)
frame_topo.pack(fill="x")

lbl_titulo = tk.Label(
    frame_topo,
    text="SIMULADOR DE CARBONO NEUTRO: MOBILIDADE E TRANSIÇÃO DE FROTAS",
    bg="#1B4332", fg="white", font=("Arial", 13, "bold"), pady=10
)
lbl_titulo.pack()

lbl_subtitulo = tk.Label(
    frame_topo,
    text="Cálculo de Emissões (Escopo 1 e 2), Compensação Ambiental e Receita no Mercado de Carbono",
    bg="#1B4332", fg="#B7E4C7", font=("Arial", 9)
)
lbl_subtitulo.pack(pady=(0, 10))

# Painel de Entrada de Dados Operacionais
frame_entradas = tk.LabelFrame(
    janela, text=" 1. Parâmetros Operacionais da Frota Logística ",
    bg="white", fg="#1B4332", font=("Arial", 10, "bold"),
    padx=20, pady=15, bd=1, relief="solid"
)
frame_entradas.pack(fill="x", padx=20, pady=15)

# Linha 1: Tipo de Combustível
tk.Label(
    frame_entradas, text="Matriz Energética Atual da Frota:",
    bg="white", font=("Arial", 10)
).grid(row=0, column=0, sticky="w", pady=6)

combo_combustivel = ttk.Combobox(
    frame_entradas, width=38, font=("Arial", 10), state="readonly",
    values=[
        "1 - Óleo Diesel Comercial (S10)",
        "2 - Gasolina Comum",
        "3 - Etanol Hidratado / Biocombustível",
        "4 - Veículo 100% Elétrico (Escopo 1 Zero)"
    ]
)
combo_combustivel.grid(row=0, column=1, pady=6, padx=10, sticky="e")

# Linha 2: Quantidade de Veículos
tk.Label(
    frame_entradas, text="Quantidade de Veículos na Frota (unidades):",
    bg="white", font=("Arial", 10)
).grid(row=1, column=0, sticky="w", pady=6)
entry_veiculos = ttk.Entry(frame_entradas, width=40, font=("Arial", 10))
entry_veiculos.grid(row=1, column=1, pady=6, padx=10)

# Linha 3: Distância Percorrida
tk.Label(
    frame_entradas, text="Distância Média Percorrida por Veículo/Ano (km):",
    bg="white", font=("Arial", 10)
).grid(row=2, column=0, sticky="w", pady=6)
entry_distancia = ttk.Entry(frame_entradas, width=40, font=("Arial", 10))
entry_distancia.grid(row=2, column=1, pady=6, padx=10)

# Linha 4: Consumo Médio
tk.Label(
    frame_entradas, text="Consumo Médio do Veículo (Litros por km rodado):",
    bg="white", font=("Arial", 10)
).grid(row=3, column=0, sticky="w", pady=6)
entry_consumo = ttk.Entry(frame_entradas, width=40, font=("Arial", 10))
entry_consumo.grid(row=3, column=1, pady=6, padx=10)

# Linha 5: Meta/Teto de Emissões Corporativas
tk.Label(
    frame_entradas, text="Teto / Meta Anual de Emissões da Empresa (tCO2e):",
    bg="white", font=("Arial", 10)
).grid(row=4, column=0, sticky="w", pady=6)
entry_meta = ttk.Entry(frame_entradas, width=40, font=("Arial", 10))
entry_meta.grid(row=4, column=1, pady=6, padx=10)

# Linha 6: Cotação do Crédito de Carbono
tk.Label(
    frame_entradas, text="Cotação Atual do Crédito de Carbono (R$ / tonelada):",
    bg="white", font=("Arial", 10)
).grid(row=5, column=0, sticky="w", pady=6)
entry_cotacao = ttk.Entry(frame_entradas, width=40, font=("Arial", 10))
entry_cotacao.grid(row=5, column=1, pady=6, padx=10)

# Painel de Botões de Ação
frame_botoes = tk.Frame(janela, bg="#F4F7F6")
frame_botoes.pack(fill="x", padx=20, pady=5)

btn_calcular = tk.Button(
    frame_botoes, text="CALCULAR EMISSÕES E IMPACTO FINANCEIRO",
    command=executar_calculo, bg="#2D6A4F", fg="white",
    font=("Arial", 10, "bold"), padx=18, pady=8, bd=0, cursor="hand2"
)
btn_calcular.pack(side="left", expand=True, fill="x", padx=(0, 10))

btn_limpar = tk.Button(
    frame_botoes, text="RESTAURAR PADRÃO / LIMPAR",
    command=limpar_dados, bg="#CFD8DC", fg="#263238",
    font=("Arial", 10, "bold"), padx=15, pady=8, bd=0, cursor="hand2"
)
btn_limpar.pack(side="right")

# Painel de Exibição de Resultados
frame_resultados = tk.LabelFrame(
    janela, text=" 2. Relatório de Auditoria Ambiental e Mercado de Carbono ",
    bg="white", fg="#1B4332", font=("Arial", 10, "bold"),
    padx=20, pady=15, bd=1, relief="solid"
)
frame_resultados.pack(fill="both", expand=True, padx=20, pady=15)

# Indicadores do Relatório
tk.Label(
    frame_resultados, text="Emissão Bruta da Frota Atual:",
    bg="white", font=("Arial", 10, "bold")
).grid(row=0, column=0, sticky="w", pady=6)
lbl_res_atual = tk.Label(
    frame_resultados, text="0.00 tCO2e / ano",
    bg="white", fg="#D84315", font=("Arial", 10, "bold")
)
lbl_res_atual.grid(row=0, column=1, sticky="w", padx=10)

tk.Label(
    frame_resultados, text="Custo de Neutralização Total (100%):",
    bg="white", font=("Arial", 10, "bold")
).grid(row=1, column=0, sticky="w", pady=6)
lbl_res_custo_comp = tk.Label(
    frame_resultados, text="R$ 0.00",
    bg="white", fg="#C62828", font=("Arial", 10, "bold")
)
lbl_res_custo_comp.grid(row=1, column=1, sticky="w", padx=10)

tk.Label(
    frame_resultados, text="Cenário de Transição (Frota Elétrica):",
    bg="white", font=("Arial", 10, "bold")
).grid(row=2, column=0, sticky="w", pady=6)
lbl_res_eletrica = tk.Label(
    frame_resultados, text="0.00 tCO2e / ano",
    bg="white", fg="#2E7D32", font=("Arial", 10, "bold")
)
lbl_res_eletrica.grid(row=2, column=1, sticky="w", padx=10)

tk.Label(
    frame_resultados, text="Potencial de Receita com Créditos:",
    bg="white", font=("Arial", 10, "bold")
).grid(row=3, column=0, sticky="w", pady=6)
lbl_res_lucro_transicao = tk.Label(
    frame_resultados, text="0.00 Créditos | R$ 0.00",
    bg="white", fg="#1B5E20", font=("Arial", 10, "bold")
)
lbl_res_lucro_transicao.grid(row=3, column=1, sticky="w", padx=10)

tk.Label(
    frame_resultados, text="Status da Meta Corporativa:",
    bg="white", font=("Arial", 10, "bold")
).grid(row=4, column=0, sticky="nw", pady=6)
lbl_status_final = tk.Label(
    frame_resultados,
    text="Aguardando simulação... Preencha os dados e clique em Calcular.",
    bg="white", fg="#37474F", font=("Arial", 10), justify="left", wraplength=420
)
lbl_status_final.grid(row=4, column=1, sticky="w", padx=10, pady=6)

# Inicializa os campos com os valores padrão
limpar_dados()

# Executa o loop principal da interface
if __name__ == "__main__":
    janela.mainloop()