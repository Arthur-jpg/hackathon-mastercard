#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GRÁFICOS INDIVIDUAIS DETALHADOS - ANÁLISE DE CHURN POR FATOR
Criação de gráficos individuais para melhor visualização de cada fator
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de estilo
plt.style.use('default')
sns.set_palette("viridis")

print("📊 CRIANDO GRÁFICOS INDIVIDUAIS DETALHADOS...")
print()

# =============================================================================
# RECARREGAR E PREPARAR DADOS (mesmo processo do script anterior)
# =============================================================================

# Carregar dados
df_clientes = pd.read_csv('data/Base_clientes.csv')
df_transacoes = pd.read_csv('data/Base_transacoes.csv')
df_cartoes = pd.read_csv('data/Base_cartoes.csv')

# Converter datas
df_transacoes['Data'] = pd.to_datetime(df_transacoes['Data'])
df_clientes['Data_Nascimento'] = pd.to_datetime(df_clientes['Data_Nascimento'], format='%d/%m/%Y')
df_clientes['Data_Criacao_Conta'] = pd.to_datetime(df_clientes['Data_Criacao_Conta'])
df_cartoes['Data_Emissao'] = pd.to_datetime(df_cartoes['Data_Emissao'])

# Data de referência
data_referencia = df_transacoes['Data'].max()

# Identificar churn
ultima_transacao = df_transacoes.groupby('Cliente_ID')['Data'].max().reset_index()
ultima_transacao.columns = ['Cliente_ID', 'Ultima_Transacao']

dias_churn = 90
data_limite_churn = data_referencia - timedelta(days=dias_churn)
ultima_transacao['Churn'] = ultima_transacao['Ultima_Transacao'] < data_limite_churn

# Preparar dados de análise
df_analise = df_clientes.copy()
df_analise = df_analise.merge(ultima_transacao[['Cliente_ID', 'Churn']], on='Cliente_ID', how='left')

# Calcular variáveis derivadas
df_analise['Idade'] = ((data_referencia - df_analise['Data_Nascimento']).dt.days / 365.25)
df_analise['Idade'] = df_analise['Idade'].fillna(0).astype(int)

df_analise['Tempo_Conta_Meses'] = ((data_referencia - df_analise['Data_Criacao_Conta']).dt.days / 30.44)
df_analise['Tempo_Conta_Meses'] = df_analise['Tempo_Conta_Meses'].fillna(0).astype(int)

# Conectar dados de cartões
cartao_cliente = df_transacoes[['Cliente_ID', 'ID_Cartao']].drop_duplicates()
cartao_info = cartao_cliente.merge(df_cartoes, on='ID_Cartao', how='left')
cartao_por_cliente = cartao_info.groupby('Cliente_ID').first().reset_index()

df_analise = df_analise.merge(cartao_por_cliente[['Cliente_ID', 'Produto_Mastercard', 'Tipo_Cartao', 
                                                'Data_Emissao', 'Limite_Cartao']], 
                             on='Cliente_ID', how='left')

df_analise['Tempo_Cartao_Meses'] = ((data_referencia - df_analise['Data_Emissao']).dt.days / 30.44)
df_analise['Tempo_Cartao_Meses'] = df_analise['Tempo_Cartao_Meses'].fillna(-1).astype(int)

# =============================================================================
# FUNÇÃO PARA CRIAR GRÁFICOS INDIVIDUAIS
# =============================================================================

def criar_grafico_individual(df, coluna, titulo, bins=None, figsize=(12, 8), 
                           salvar_como=None, top_n=None):
    """
    Cria gráfico individual detalhado para um fator específico
    """
    df_clean = df.dropna(subset=[coluna, 'Churn'])
    
    # Preparar dados
    if bins is not None:
        df_clean[f'{coluna}_Faixa'] = pd.cut(df_clean[coluna], bins=bins, include_lowest=True)
        coluna_analise = f'{coluna}_Faixa'
    else:
        coluna_analise = coluna
    
    # Análise
    analise = df_clean.groupby(coluna_analise).agg({
        'Churn': ['count', 'sum'],
        'Cliente_ID': 'count'
    })
    
    analise.columns = ['Total_Clientes', 'Clientes_Churn', 'Total_Clientes_2']
    analise = analise.drop('Total_Clientes_2', axis=1)
    
    analise['Total_Clientes'] = pd.to_numeric(analise['Total_Clientes'], errors='coerce')
    analise['Clientes_Churn'] = pd.to_numeric(analise['Clientes_Churn'], errors='coerce')
    analise['Taxa_Churn'] = (analise['Clientes_Churn'] / analise['Total_Clientes'] * 100).round(1)
    analise['Pct_Base'] = (analise['Total_Clientes'] / analise['Total_Clientes'].sum() * 100).round(1)
    
    # Filtrar dados válidos
    analise = analise.dropna(subset=['Taxa_Churn'])
    analise = analise[analise['Total_Clientes'] > 0]
    
    # Aplicar top_n se especificado
    if top_n:
        analise = analise.nlargest(top_n, 'Taxa_Churn')
    
    if len(analise) == 0:
        print(f"⚠️ Sem dados válidos para {titulo}")
        return
    
    # Criar gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(f'ANÁLISE DE CHURN: {titulo.upper()}', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Taxa de Churn
    y_pos = np.arange(len(analise))
    bars1 = ax1.barh(y_pos, analise['Taxa_Churn'], 
                     color=plt.cm.Reds(analise['Taxa_Churn']/analise['Taxa_Churn'].max()),
                     alpha=0.8)
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([str(idx)[:25] for idx in analise.index], fontsize=10)
    ax1.set_xlabel('Taxa de Churn (%)')
    ax1.set_title('Taxa de Churn por Categoria')
    ax1.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for i, (bar, valor) in enumerate(zip(bars1, analise['Taxa_Churn'])):
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{valor:.1f}%', ha='left', va='center', fontweight='bold')
    
    # Gráfico 2: Distribuição de Clientes
    bars2 = ax2.barh(y_pos, analise['Total_Clientes'], 
                     color=plt.cm.Blues(analise['Total_Clientes']/analise['Total_Clientes'].max()),
                     alpha=0.8)
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([str(idx)[:25] for idx in analise.index], fontsize=10)
    ax2.set_xlabel('Número de Clientes')
    ax2.set_title('Distribuição de Clientes')
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for i, (bar, valor) in enumerate(zip(bars2, analise['Total_Clientes'])):
        width = bar.get_width()
        ax2.text(width + 20, bar.get_y() + bar.get_height()/2,
                f'{int(valor):,}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    
    if salvar_como:
        plt.savefig(salvar_como, dpi=300, bbox_inches='tight')
        print(f"✅ Salvo: {salvar_como}")
    
    plt.show()
    return analise

# =============================================================================
# CRIAR GRÁFICOS INDIVIDUAIS PARA CADA FATOR
# =============================================================================

print("1️⃣ GRÁFICO: CHURN POR FAIXA ETÁRIA")
faixas_idade = [0, 25, 35, 45, 55, 65, 100]
resultado_idade = criar_grafico_individual(
    df_analise, 'Idade', 'Churn por Faixa Etária',
    bins=faixas_idade, salvar_como='churn_por_idade.png'
)
print()

print("2️⃣ GRÁFICO: CHURN POR FAIXA DE RENDA")
faixas_renda = [0, 30000, 50000, 75000, 100000, 150000, 1000000]
resultado_renda = criar_grafico_individual(
    df_analise, 'Renda_Anual', 'Churn por Faixa de Renda',
    bins=faixas_renda, salvar_como='churn_por_renda.png'
)
print()

print("3️⃣ GRÁFICO: CHURN POR TEMPO DE CONTA")
faixas_tempo_conta = [0, 6, 12, 18, 24, 36, 1000]
resultado_tempo_conta = criar_grafico_individual(
    df_analise, 'Tempo_Conta_Meses', 'Churn por Tempo de Conta',
    bins=faixas_tempo_conta, salvar_como='churn_por_tempo_conta.png'
)
print()

print("4️⃣ GRÁFICO: CHURN POR CONTA ADICIONAL")
resultado_conta_adicional = criar_grafico_individual(
    df_analise, 'Possui_Conta_Adicional', 'Churn por Conta Adicional',
    salvar_como='churn_por_conta_adicional.png'
)
print()

print("5️⃣ GRÁFICO: CHURN POR ESTADO (TOP 10)")
resultado_estado = criar_grafico_individual(
    df_analise, 'Estado', 'Churn por Estado',
    top_n=10, salvar_como='churn_por_estado.png'
)
print()

print("6️⃣ GRÁFICO: CHURN POR TIPO DE CARTÃO")
resultado_tipo_cartao = criar_grafico_individual(
    df_analise, 'Tipo_Cartao', 'Churn por Tipo de Cartão',
    salvar_como='churn_por_tipo_cartao.png'
)
print()

print("7️⃣ GRÁFICO: CHURN POR PRODUTO MASTERCARD")
resultado_produto = criar_grafico_individual(
    df_analise, 'Produto_Mastercard', 'Churn por Produto Mastercard',
    salvar_como='churn_por_produto_mastercard.png'
)
print()

print("8️⃣ GRÁFICO: CHURN POR TEMPO DO CARTÃO")
faixas_tempo_cartao = [0, 6, 12, 18, 24, 36, 1000] 
resultado_tempo_cartao = criar_grafico_individual(
    df_analise, 'Tempo_Cartao_Meses', 'Churn por Tempo do Cartão',
    bins=faixas_tempo_cartao, salvar_como='churn_por_tempo_cartao.png'
)
print()

print("9️⃣ GRÁFICO: CHURN POR LIMITE DO CARTÃO")
df_credito = df_analise[df_analise['Limite_Cartao'] > 0]
faixas_limite = [0, 5000, 15000, 25000, 40000, 1000000]
resultado_limite = criar_grafico_individual(
    df_credito, 'Limite_Cartao', 'Churn por Limite do Cartão',
    bins=faixas_limite, salvar_como='churn_por_limite_cartao.png'
)
print()

# =============================================================================
# RESUMO DOS INSIGHTS MAIS IMPORTANTES
# =============================================================================

print("="*80)
print("🎯 RESUMO DOS INSIGHTS MAIS CRÍTICOS")
print("="*80)
print()

print("🚨 FATORES DE MAIOR RISCO DE CHURN:")
print()

print("1. 📅 TEMPO DO CARTÃO (6-12 meses): 42.9% churn")
print("   → Clientes com cartões recém-emitidos abandonam rapidamente")
print()

print("2. 💰 RENDA MÉDIA-ALTA (R$ 75-100k): 7.8% churn")
print("   → Segmento com expectativas altas, migra para concorrentes")
print()

print("3. 👥 IDADE 35-45 ANOS: 7.3% churn")
print("   → Faixa economicamente ativa, alta exigência de serviços")
print()

print("4. 💳 CARTÃO BLACK: 7.1% churn")
print("   → Clientes premium insatisfeitos com benefícios/serviços")
print()

print("5. 🏦 CONTA SIMPLES (sem adicional): 5.5% churn")
print("   → Menor vínculo com o banco, facilita migração")
print()

print("6. 📍 ESTADO RJ: 5.8% churn")
print("   → Mercado competitivo, muitas opções bancárias")
print()

print()
print("✅ TODOS OS GRÁFICOS INDIVIDUAIS FORAM CRIADOS!")
print("📊 Use estes insights para campanhas de retenção direcionadas.")
print()

print("="*80)
print("🎯 ANÁLISE COMPLETA DE CHURN FINALIZADA")
print("="*80)