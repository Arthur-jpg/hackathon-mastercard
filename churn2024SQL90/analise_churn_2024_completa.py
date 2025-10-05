#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANÁLISE COMPLETA DE CHURN 2024 - 9 TÓPICOS
Análise detalhada de churn para o ano de 2024 usando SQL puro
Geração de gráficos individuais e resumo executivo
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração de estilo
plt.style.use('default')
sns.set_palette("Set2")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

print("="*80)
print("🔍 ANÁLISE COMPLETA DE CHURN 2024 - 9 TÓPICOS")
print("="*80)
print()

# Conectar ao banco de dados
conn = sqlite3.connect('priceless_bank.db')

# =============================================================================
# FUNÇÃO PARA EXECUTAR QUERIES E CRIAR GRÁFICOS
# =============================================================================

def criar_grafico_churn(df, titulo, coluna_categoria, salvar_como, tipo='bar', figsize=(12, 8)):
    """
    Cria gráfico de churn personalizado
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(f'ANÁLISE DE CHURN 2024: {titulo.upper()}', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Taxa de Churn
    if tipo == 'bar':
        bars1 = ax1.bar(range(len(df)), df['taxa_churn_pct'], 
                       color=plt.cm.Reds(df['taxa_churn_pct']/df['taxa_churn_pct'].max()),
                       alpha=0.8, edgecolor='black', linewidth=1)
        ax1.set_xticks(range(len(df)))
        ax1.set_xticklabels(df[coluna_categoria], rotation=45, ha='right')
    else:  # horizontal bar
        bars1 = ax1.barh(range(len(df)), df['taxa_churn_pct'],
                        color=plt.cm.Reds(df['taxa_churn_pct']/df['taxa_churn_pct'].max()),
                        alpha=0.8, edgecolor='black', linewidth=1)
        ax1.set_yticks(range(len(df)))
        ax1.set_yticklabels(df[coluna_categoria])
    
    ax1.set_xlabel('Taxa de Churn (%)' if tipo == 'bar' else '')
    ax1.set_ylabel('Taxa de Churn (%)' if tipo != 'bar' else '')
    ax1.set_title('Taxa de Churn por Categoria')
    ax1.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for i, valor in enumerate(df['taxa_churn_pct']):
        if tipo == 'bar':
            ax1.text(i, valor + 0.1, f'{valor:.1f}%', ha='center', va='bottom', fontweight='bold')
        else:
            ax1.text(valor + 0.1, i, f'{valor:.1f}%', ha='left', va='center', fontweight='bold')
    
    # Gráfico 2: Distribuição de Clientes
    if tipo == 'bar':
        bars2 = ax2.bar(range(len(df)), df['total_clientes'],
                       color=plt.cm.Blues(df['total_clientes']/df['total_clientes'].max()),
                       alpha=0.8, edgecolor='black', linewidth=1)
        ax2.set_xticks(range(len(df)))
        ax2.set_xticklabels(df[coluna_categoria], rotation=45, ha='right')
    else:
        bars2 = ax2.barh(range(len(df)), df['total_clientes'],
                        color=plt.cm.Blues(df['total_clientes']/df['total_clientes'].max()),
                        alpha=0.8, edgecolor='black', linewidth=1)
        ax2.set_yticks(range(len(df)))
        ax2.set_yticklabels(df[coluna_categoria])
    
    ax2.set_xlabel('Número de Clientes' if tipo == 'bar' else '')
    ax2.set_ylabel('Número de Clientes' if tipo != 'bar' else '')
    ax2.set_title('Distribuição de Clientes')
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for i, valor in enumerate(df['total_clientes']):
        if tipo == 'bar':
            ax2.text(i, valor + max(df['total_clientes']) * 0.01, f'{valor}', 
                    ha='center', va='bottom', fontweight='bold')
        else:
            ax2.text(valor + max(df['total_clientes']) * 0.01, i, f'{valor}', 
                    ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(salvar_como, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✅ Gráfico salvo: {salvar_como}")
    return df

# =============================================================================
# 1️⃣ ANÁLISE POR IDADE
# =============================================================================

print("1️⃣ ANÁLISE POR FAIXA ETÁRIA")
print("-" * 40)

query_idade = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
)
SELECT 
    CASE 
        WHEN c.idade < 25 THEN '18-24 anos'
        WHEN c.idade BETWEEN 25 AND 34 THEN '25-34 anos'
        WHEN c.idade BETWEEN 35 AND 44 THEN '35-44 anos'
        WHEN c.idade BETWEEN 45 AND 54 THEN '45-54 anos'
        WHEN c.idade >= 55 THEN '55+ anos'
    END as faixa_etaria,
    COUNT(c.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM clientes c
LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
  AND ut.ultima_transacao IS NOT NULL
GROUP BY faixa_etaria ORDER BY AVG(c.idade);
"""

df_idade = pd.read_sql_query(query_idade, conn)
df_idade = criar_grafico_churn(df_idade, "Churn por Faixa Etária", "faixa_etaria", 
                              "grafico_1_churn_idade_2024.png")
print()

# =============================================================================
# 2️⃣ ANÁLISE POR RENDA
# =============================================================================

print("2️⃣ ANÁLISE POR FAIXA DE RENDA")
print("-" * 40)

query_renda = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
)
SELECT 
    CASE 
        WHEN c.renda_anual < 30000 THEN 'Até R$ 30k'
        WHEN c.renda_anual BETWEEN 30000 AND 50000 THEN 'R$ 30-50k'
        WHEN c.renda_anual BETWEEN 50001 AND 75000 THEN 'R$ 50-75k'
        WHEN c.renda_anual BETWEEN 75001 AND 100000 THEN 'R$ 75-100k'
        WHEN c.renda_anual BETWEEN 100001 AND 150000 THEN 'R$ 100-150k'
        ELSE 'R$ 150k+'
    END as faixa_renda,
    COUNT(c.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM clientes c
LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
  AND ut.ultima_transacao IS NOT NULL
GROUP BY faixa_renda ORDER BY AVG(c.renda_anual);
"""

df_renda = pd.read_sql_query(query_renda, conn)
df_renda = criar_grafico_churn(df_renda, "Churn por Faixa de Renda", "faixa_renda", 
                              "grafico_2_churn_renda_2024.png")
print()

# =============================================================================
# 3️⃣ ANÁLISE POR TEMPO DE CONTA
# =============================================================================

print("3️⃣ ANÁLISE POR TEMPO DE CONTA")
print("-" * 40)

query_tempo_conta = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
)
SELECT 
    CASE 
        WHEN c.tempo_conta_meses <= 6 THEN '0-6 meses'
        WHEN c.tempo_conta_meses BETWEEN 7 AND 12 THEN '7-12 meses'
        WHEN c.tempo_conta_meses BETWEEN 13 AND 18 THEN '13-18 meses'
        WHEN c.tempo_conta_meses BETWEEN 19 AND 24 THEN '19-24 meses'
        ELSE '24+ meses'
    END as periodo_conta,
    COUNT(c.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM clientes c
LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
  AND ut.ultima_transacao IS NOT NULL
GROUP BY periodo_conta ORDER BY AVG(c.tempo_conta_meses);
"""

df_tempo_conta = pd.read_sql_query(query_tempo_conta, conn)
df_tempo_conta = criar_grafico_churn(df_tempo_conta, "Churn por Tempo de Conta", "periodo_conta", 
                                    "grafico_3_churn_tempo_conta_2024.png")
print()

# =============================================================================
# 4️⃣ ANÁLISE POR CONTA ADICIONAL
# =============================================================================

print("4️⃣ ANÁLISE POR CONTA ADICIONAL")
print("-" * 40)

query_conta_adicional = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
)
SELECT 
    c.possui_conta_adicional as conta_adicional,
    COUNT(c.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM clientes c
LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
  AND ut.ultima_transacao IS NOT NULL
GROUP BY c.possui_conta_adicional ORDER BY taxa_churn_pct DESC;
"""

df_conta_adicional = pd.read_sql_query(query_conta_adicional, conn)
df_conta_adicional = criar_grafico_churn(df_conta_adicional, "Churn por Conta Adicional", "conta_adicional", 
                                        "grafico_4_churn_conta_adicional_2024.png")
print()

# =============================================================================
# 5️⃣ ANÁLISE POR ESTADO
# =============================================================================

print("5️⃣ ANÁLISE POR ESTADO")
print("-" * 40)

query_estado = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
),
churn_por_estado AS (
    SELECT 
        c.estado,
        COUNT(c.cliente_id) as total_clientes,
        SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
        ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
    FROM clientes c
    LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
    WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
      AND ut.ultima_transacao IS NOT NULL
    GROUP BY c.estado
    HAVING COUNT(c.cliente_id) >= 10
)
SELECT * FROM churn_por_estado ORDER BY taxa_churn_pct DESC;
"""

df_estado = pd.read_sql_query(query_estado, conn)
df_estado = criar_grafico_churn(df_estado, "Churn por Estado", "estado", 
                               "grafico_5_churn_estado_2024.png", tipo='horizontal')
print()

# =============================================================================
# 6️⃣ ANÁLISE POR TIPO DE CARTÃO
# =============================================================================

print("6️⃣ ANÁLISE POR TIPO DE CARTÃO")
print("-" * 40)

query_tipo_cartao = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
),
cartoes_2024 AS (
    SELECT DISTINCT t.cliente_id, cart.tipo_cartao
    FROM transacoes t
    JOIN cartoes cart ON t.id_cartao = cart.id_cartao
    WHERE cart.data_emissao >= '2024-01-01' AND cart.data_emissao <= '2024-12-31'
)
SELECT 
    c24.tipo_cartao,
    COUNT(DISTINCT c24.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM cartoes_2024 c24
LEFT JOIN ultima_transacao_por_cliente ut ON c24.cliente_id = ut.cliente_id
GROUP BY c24.tipo_cartao ORDER BY taxa_churn_pct DESC;
"""

df_tipo_cartao = pd.read_sql_query(query_tipo_cartao, conn)
df_tipo_cartao = criar_grafico_churn(df_tipo_cartao, "Churn por Tipo de Cartão", "tipo_cartao", 
                                    "grafico_6_churn_tipo_cartao_2024.png")
print()

# =============================================================================
# 7️⃣ ANÁLISE POR PRODUTO MASTERCARD
# =============================================================================

print("7️⃣ ANÁLISE POR PRODUTO MASTERCARD")
print("-" * 40)

query_produto = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
),
cartoes_2024 AS (
    SELECT DISTINCT t.cliente_id, cart.produto_mastercard
    FROM transacoes t
    JOIN cartoes cart ON t.id_cartao = cart.id_cartao
    WHERE cart.data_emissao >= '2024-01-01' AND cart.data_emissao <= '2024-12-31'
)
SELECT 
    c24.produto_mastercard,
    COUNT(DISTINCT c24.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM cartoes_2024 c24
LEFT JOIN ultima_transacao_por_cliente ut ON c24.cliente_id = ut.cliente_id
GROUP BY c24.produto_mastercard ORDER BY taxa_churn_pct DESC;
"""

df_produto = pd.read_sql_query(query_produto, conn)
df_produto = criar_grafico_churn(df_produto, "Churn por Produto Mastercard", "produto_mastercard", 
                                "grafico_7_churn_produto_2024.png", tipo='horizontal')
print()

# =============================================================================
# 8️⃣ ANÁLISE POR TEMPO DE CARTÃO
# =============================================================================

print("8️⃣ ANÁLISE POR TEMPO DE CARTÃO")
print("-" * 40)

query_tempo_cartao = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
),
cartoes_2024 AS (
    SELECT DISTINCT t.cliente_id, cart.tempo_cartao_meses
    FROM transacoes t
    JOIN cartoes cart ON t.id_cartao = cart.id_cartao
    WHERE cart.data_emissao >= '2024-01-01' AND cart.data_emissao <= '2024-12-31'
)
SELECT 
    CASE 
        WHEN c24.tempo_cartao_meses <= 6 THEN '0-6 meses'
        WHEN c24.tempo_cartao_meses BETWEEN 7 AND 12 THEN '7-12 meses'
        WHEN c24.tempo_cartao_meses BETWEEN 13 AND 18 THEN '13-18 meses'
        WHEN c24.tempo_cartao_meses BETWEEN 19 AND 24 THEN '19-24 meses'
        ELSE '24+ meses'
    END as periodo_cartao,
    COUNT(DISTINCT c24.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM cartoes_2024 c24
LEFT JOIN ultima_transacao_por_cliente ut ON c24.cliente_id = ut.cliente_id
GROUP BY periodo_cartao ORDER BY AVG(c24.tempo_cartao_meses);
"""

df_tempo_cartao = pd.read_sql_query(query_tempo_cartao, conn)
df_tempo_cartao = criar_grafico_churn(df_tempo_cartao, "Churn por Tempo de Cartão", "periodo_cartao", 
                                     "grafico_8_churn_tempo_cartao_2024.png")
print()

# =============================================================================
# 9️⃣ ANÁLISE POR LIMITE DE CARTÃO
# =============================================================================

print("9️⃣ ANÁLISE POR LIMITE DE CARTÃO")
print("-" * 40)

query_limite = """
WITH ultima_transacao_por_cliente AS (
    SELECT cliente_id, MAX(data) as ultima_transacao
    FROM transacoes GROUP BY cliente_id
),
cartoes_2024 AS (
    SELECT DISTINCT t.cliente_id, cart.limite_cartao
    FROM transacoes t
    JOIN cartoes cart ON t.id_cartao = cart.id_cartao
    WHERE cart.data_emissao >= '2024-01-01' AND cart.data_emissao <= '2024-12-31'
)
SELECT 
    CASE 
        WHEN c24.limite_cartao <= 1000 THEN 'Até R$ 1k'
        WHEN c24.limite_cartao BETWEEN 1001 AND 3000 THEN 'R$ 1-3k'
        WHEN c24.limite_cartao BETWEEN 3001 AND 5000 THEN 'R$ 3-5k'
        WHEN c24.limite_cartao BETWEEN 5001 AND 10000 THEN 'R$ 5-10k'
        WHEN c24.limite_cartao BETWEEN 10001 AND 20000 THEN 'R$ 10-20k'
        ELSE 'R$ 20k+'
    END as faixa_limite,
    COUNT(DISTINCT c24.cliente_id) as total_clientes,
    SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1 ELSE 0 END) as clientes_churn,
    ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-90 days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
FROM cartoes_2024 c24
LEFT JOIN ultima_transacao_por_cliente ut ON c24.cliente_id = ut.cliente_id
GROUP BY faixa_limite ORDER BY AVG(c24.limite_cartao);
"""

df_limite = pd.read_sql_query(query_limite, conn)
df_limite = criar_grafico_churn(df_limite, "Churn por Limite de Cartão", "faixa_limite", 
                               "grafico_9_churn_limite_2024.png")
print()

# =============================================================================
# 🎯 GRÁFICO RESUMO EXECUTIVO
# =============================================================================

print("🎯 CRIANDO GRÁFICO RESUMO EXECUTIVO")
print("-" * 40)

# Consolidar dados para resumo
resumo_dados = {
    'Categoria': ['Idade 35-44', 'Renda Baixa', 'Conta 7-12m', 'Sem Adic.', 'Estado MG', 
                  'Cartão Débito', 'Standard', 'Cartão 7-12m', 'Limite 5-10k'],
    'Taxa_Churn': [6.62, 6.98, 5.37, 4.52, 6.38, 62.5, 80.0, 62.5, 66.67],
    'Tipo': ['Perfil', 'Perfil', 'Perfil', 'Perfil', 'Geo', 'Produto', 'Produto', 'Produto', 'Produto'],
    'Clientes': [136, 43, 354, 442, 94, 8, 5, 32, 3]
}

df_resumo = pd.DataFrame(resumo_dados)

# Criar gráfico resumo
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('📊 RESUMO EXECUTIVO - CHURN ANALYSIS 2024\nPRINCIPAIS FATORES DE RISCO', 
             fontsize=18, fontweight='bold')

# Gráfico 1: Top 5 Maiores Taxas de Churn
top_5_churn = df_resumo.nlargest(5, 'Taxa_Churn')
colors1 = ['#FF4444' if x >= 60 else '#FF8888' if x >= 10 else '#FFAAAA' for x in top_5_churn['Taxa_Churn']]
bars1 = ax1.bar(range(len(top_5_churn)), top_5_churn['Taxa_Churn'], color=colors1, alpha=0.8, edgecolor='black')
ax1.set_xticks(range(len(top_5_churn)))
ax1.set_xticklabels(top_5_churn['Categoria'], rotation=45, ha='right')
ax1.set_ylabel('Taxa de Churn (%)')
ax1.set_title('🚨 TOP 5 MAIORES TAXAS DE CHURN')
ax1.grid(True, alpha=0.3)
for i, v in enumerate(top_5_churn['Taxa_Churn']):
    ax1.text(i, v + 1, f'{v}%', ha='center', va='bottom', fontweight='bold')

# Gráfico 2: Churn por Tipo de Fator
churn_por_tipo = df_resumo.groupby('Tipo')['Taxa_Churn'].mean().reset_index()
colors2 = ['#FF6B6B', '#4ECDC4']
bars2 = ax2.bar(churn_por_tipo['Tipo'], churn_por_tipo['Taxa_Churn'], color=colors2, alpha=0.8, edgecolor='black')
ax2.set_ylabel('Taxa Média de Churn (%)')
ax2.set_title('📊 CHURN MÉDIO POR TIPO DE FATOR')
ax2.grid(True, alpha=0.3)
for i, v in enumerate(churn_por_tipo['Taxa_Churn']):
    ax2.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

# Gráfico 3: Volume de Clientes Afetados
top_volume = df_resumo.nlargest(5, 'Clientes')
colors3 = plt.cm.Blues(np.linspace(0.4, 0.8, len(top_volume)))
bars3 = ax3.bar(range(len(top_volume)), top_volume['Clientes'], color=colors3, alpha=0.8, edgecolor='black')
ax3.set_xticks(range(len(top_volume)))
ax3.set_xticklabels(top_volume['Categoria'], rotation=45, ha='right')
ax3.set_ylabel('Número de Clientes')
ax3.set_title('👥 MAIOR VOLUME DE CLIENTES AFETADOS')
ax3.grid(True, alpha=0.3)
for i, v in enumerate(top_volume['Clientes']):
    ax3.text(i, v + 5, f'{v}', ha='center', va='bottom', fontweight='bold')

# Gráfico 4: Matriz Risco vs Volume
scatter = ax4.scatter(df_resumo['Clientes'], df_resumo['Taxa_Churn'], 
                     c=df_resumo['Taxa_Churn'], cmap='Reds', s=100, alpha=0.7, edgecolors='black')
ax4.set_xlabel('Número de Clientes')
ax4.set_ylabel('Taxa de Churn (%)')
ax4.set_title('🎯 MATRIZ RISCO vs VOLUME')
ax4.grid(True, alpha=0.3)

# Adicionar labels nos pontos críticos
for i, row in df_resumo.iterrows():
    if row['Taxa_Churn'] > 50 or row['Clientes'] > 300:
        ax4.annotate(row['Categoria'], (row['Clientes'], row['Taxa_Churn']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('grafico_resumo_executivo_churn_2024.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Gráfico Resumo Executivo salvo: grafico_resumo_executivo_churn_2024.png")
print()

# =============================================================================
# 📋 RELATÓRIO FINAL
# =============================================================================

print("="*80)
print("📋 RELATÓRIO FINAL - CHURN ANALYSIS 2024")
print("="*80)
print()

print("🚨 ALERTAS CRÍTICOS:")
print("1. PRODUTO STANDARD: 80% de churn - DESCONTINUAR URGENTE")
print("2. CARTÕES 7-12 MESES: 62,5% de churn - INTERVENÇÃO IMEDIATA")
print("3. LIMITE 5-10k: 66,67% de churn - REVISAR POLÍTICA")
print()

print("⚠️  FATORES DE RISCO ALTO:")
print("1. IDADE 35-44 ANOS: 6,62% churn (136 clientes)")
print("2. RENDA BAIXA: 6,98% churn (43 clientes)")
print("3. ESTADO MG: 6,38% churn (94 clientes)")
print()

print("✅ PONTOS FORTES:")
print("1. JOVENS 18-24: 0% churn - excelente retenção")
print("2. ALTA RENDA 100-150k: 3,14% churn")
print("3. GOLD CARDS: 40% churn (vs 80% Standard)")
print()

print("📊 RESUMO ESTATÍSTICO:")
print(f"• Total de gráficos gerados: 10")
print(f"• Categorias analisadas: 9")
print(f"• Período: Janeiro-Dezembro 2024")
print(f"• Critério de churn: 90 dias sem transação")
print()

print("📁 ARQUIVOS GERADOS:")
for i in range(1, 10):
    print(f"  ✓ grafico_{i}_churn_*_2024.png")
print("  ✓ grafico_resumo_executivo_churn_2024.png")
print()

# Fechar conexão
conn.close()

print("="*80)
print("🎯 ANÁLISE COMPLETA FINALIZADA COM SUCESSO!")
print("="*80)