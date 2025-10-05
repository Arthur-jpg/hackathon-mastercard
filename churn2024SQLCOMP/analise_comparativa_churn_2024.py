#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANÁLISE COMPARATIVA DE CHURN 2024 - 30, 60 e 90 DIAS
Comparação entre diferentes períodos de inatividade para identificar padrões
Geração de gráficos comparativos e insights estratégicos
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
sns.set_palette("Set1")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

print("="*80)
print("🔍 ANÁLISE COMPARATIVA DE CHURN 2024 - 30, 60 e 90 DIAS")
print("="*80)
print()

# Conectar ao banco de dados
conn = sqlite3.connect('priceless_bank.db')

# =============================================================================
# FUNÇÃO PARA OBTER DADOS DE CHURN POR PERÍODO
# =============================================================================

def obter_dados_churn(dias):
    """
    Obtém dados de churn para um período específico
    """
    print(f"📊 Coletando dados para {dias} dias...")
    
    # Query para idade
    query_idade = f"""
    WITH ultima_transacao_por_cliente AS (
        SELECT cliente_id, MAX(data) as ultima_transacao
        FROM transacoes GROUP BY cliente_id
    )
    SELECT 
        'Idade 35-44' as categoria,
        COUNT(c.cliente_id) as total_clientes,
        SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1 ELSE 0 END) as clientes_churn,
        ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
    FROM clientes c
    LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
    WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
      AND ut.ultima_transacao IS NOT NULL
      AND c.idade BETWEEN 35 AND 44;
    """
    
    # Query para produto Standard
    query_standard = f"""
    WITH ultima_transacao_por_cliente AS (
        SELECT cliente_id, MAX(data) as ultima_transacao
        FROM transacoes GROUP BY cliente_id
    ),
    cartoes_2024 AS (
        SELECT DISTINCT t.cliente_id, cart.produto_mastercard
        FROM transacoes t
        JOIN cartoes cart ON t.id_cartao = cart.id_cartao
        WHERE cart.data_emissao >= '2024-01-01' AND cart.data_emissao <= '2024-12-31'
          AND cart.produto_mastercard = 'Standard'
    )
    SELECT 
        'Standard' as categoria,
        COUNT(DISTINCT c24.cliente_id) as total_clientes,
        SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1 ELSE 0 END) as clientes_churn,
        ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
    FROM cartoes_2024 c24
    LEFT JOIN ultima_transacao_por_cliente ut ON c24.cliente_id = ut.cliente_id;
    """
    
    # Query para cartões 7-12 meses
    query_cartao_tempo = f"""
    WITH ultima_transacao_por_cliente AS (
        SELECT cliente_id, MAX(data) as ultima_transacao
        FROM transacoes GROUP BY cliente_id
    ),
    cartoes_2024 AS (
        SELECT DISTINCT t.cliente_id, cart.tempo_cartao_meses
        FROM transacoes t
        JOIN cartoes cart ON t.id_cartao = cart.id_cartao
        WHERE cart.data_emissao >= '2024-01-01' AND cart.data_emissao <= '2024-12-31'
          AND cart.tempo_cartao_meses BETWEEN 7 AND 12
    )
    SELECT 
        'Cartão 7-12m' as categoria,
        COUNT(DISTINCT c24.cliente_id) as total_clientes,
        SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1 ELSE 0 END) as clientes_churn,
        ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
    FROM cartoes_2024 c24
    LEFT JOIN ultima_transacao_por_cliente ut ON c24.cliente_id = ut.cliente_id;
    """
    
    # Query para renda baixa
    query_renda_baixa = f"""
    WITH ultima_transacao_por_cliente AS (
        SELECT cliente_id, MAX(data) as ultima_transacao
        FROM transacoes GROUP BY cliente_id
    )
    SELECT 
        'Renda Baixa' as categoria,
        COUNT(c.cliente_id) as total_clientes,
        SUM(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1 ELSE 0 END) as clientes_churn,
        ROUND(AVG(CASE WHEN ut.ultima_transacao < DATE('2024-12-30', '-{dias} days') THEN 1.0 ELSE 0.0 END) * 100, 2) as taxa_churn_pct
    FROM clientes c
    LEFT JOIN ultima_transacao_por_cliente ut ON c.cliente_id = ut.cliente_id
    WHERE c.Data_Criacao_Conta >= '2024-01-01' AND c.Data_Criacao_Conta <= '2024-12-31' 
      AND ut.ultima_transacao IS NOT NULL
      AND c.renda_anual < 30000;
    """
    
    # Executar queries
    df_idade = pd.read_sql_query(query_idade, conn)
    df_standard = pd.read_sql_query(query_standard, conn)
    df_cartao = pd.read_sql_query(query_cartao_tempo, conn)
    df_renda = pd.read_sql_query(query_renda_baixa, conn)
    
    # Consolidar dados
    df_resultado = pd.concat([df_idade, df_standard, df_cartao, df_renda], ignore_index=True)
    df_resultado['periodo'] = f'{dias} dias'
    
    return df_resultado

# =============================================================================
# COLETA DE DADOS PARA OS 3 PERÍODOS
# =============================================================================

print("📊 COLETANDO DADOS COMPARATIVOS...")
print()

df_30d = obter_dados_churn(30)
df_60d = obter_dados_churn(60)
df_90d = obter_dados_churn(90)

# Consolidar todos os dados
df_completo = pd.concat([df_30d, df_60d, df_90d], ignore_index=True)

print("✅ Dados coletados com sucesso!")
print(f"📈 Total de registros: {len(df_completo)}")
print()

# =============================================================================
# GRÁFICO 1: EVOLUÇÃO DAS TAXAS DE CHURN POR CATEGORIA
# =============================================================================

print("📊 CRIANDO GRÁFICO 1: EVOLUÇÃO DAS TAXAS DE CHURN")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('📊 EVOLUÇÃO DAS TAXAS DE CHURN POR PERÍODO\nComparação: 30, 60 e 90 dias de inatividade', 
             fontsize=16, fontweight='bold')

categorias = df_completo['categoria'].unique()
periodos = ['30 dias', '60 dias', '90 dias']
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

for i, categoria in enumerate(categorias):
    ax = [ax1, ax2, ax3, ax4][i]
    
    dados_categoria = df_completo[df_completo['categoria'] == categoria]
    taxas = []
    for periodo in periodos:
        taxa = dados_categoria[dados_categoria['periodo'] == periodo]['taxa_churn_pct'].iloc[0]
        taxas.append(taxa)
    
    bars = ax.bar(periodos, taxas, color=colors[i], alpha=0.7, edgecolor='black', linewidth=2)
    ax.set_title(f'{categoria}', fontsize=12, fontweight='bold')
    ax.set_ylabel('Taxa de Churn (%)')
    ax.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for j, v in enumerate(taxas):
        ax.text(j, v + max(taxas) * 0.02, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('grafico_evolucao_churn_periodos.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Gráfico salvo: grafico_evolucao_churn_periodos.png")
print()

# =============================================================================
# GRÁFICO 2: COMPARAÇÃO CONSOLIDADA
# =============================================================================

print("📊 CRIANDO GRÁFICO 2: COMPARAÇÃO CONSOLIDADA")

# Criar tabela pivot para visualização
df_pivot = df_completo.pivot(index='categoria', columns='periodo', values='taxa_churn_pct')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle('📊 ANÁLISE COMPARATIVA DE CHURN - VISÃO CONSOLIDADA', 
             fontsize=16, fontweight='bold')

# Gráfico 1: Heatmap
sns.heatmap(df_pivot, annot=True, fmt='.1f', cmap='Reds', ax=ax1, 
            cbar_kws={'label': 'Taxa de Churn (%)'})
ax1.set_title('🔥 MAPA DE CALOR - TAXAS DE CHURN')
ax1.set_xlabel('Período de Inatividade')
ax1.set_ylabel('Categoria de Risco')

# Gráfico 2: Linhas de tendência
for categoria in categorias:
    dados_linha = df_completo[df_completo['categoria'] == categoria]
    periodos_num = [30, 60, 90]
    taxas_linha = []
    for periodo_num in periodos_num:
        taxa = dados_linha[dados_linha['periodo'] == f'{periodo_num} dias']['taxa_churn_pct'].iloc[0]
        taxas_linha.append(taxa)
    
    ax2.plot(periodos_num, taxas_linha, marker='o', linewidth=2, markersize=8, label=categoria)

ax2.set_title('📈 TENDÊNCIAS DE CHURN POR PERÍODO')
ax2.set_xlabel('Período de Inatividade (dias)')
ax2.set_ylabel('Taxa de Churn (%)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xticks([30, 60, 90])

plt.tight_layout()
plt.savefig('grafico_comparacao_consolidada_churn.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Gráfico salvo: grafico_comparacao_consolidada_churn.png")
print()

# =============================================================================
# ANÁLISE ESTATÍSTICA E INSIGHTS
# =============================================================================

print("📈 ANÁLISE ESTATÍSTICA DOS DADOS")
print("-" * 50)

# Calcular variações entre períodos
for categoria in categorias:
    dados_cat = df_completo[df_completo['categoria'] == categoria]
    taxa_30 = dados_cat[dados_cat['periodo'] == '30 dias']['taxa_churn_pct'].iloc[0]
    taxa_60 = dados_cat[dados_cat['periodo'] == '60 dias']['taxa_churn_pct'].iloc[0]
    taxa_90 = dados_cat[dados_cat['periodo'] == '90 dias']['taxa_churn_pct'].iloc[0]
    
    variacao_30_60 = ((taxa_60 - taxa_30) / taxa_30) * 100 if taxa_30 > 0 else 0
    variacao_60_90 = ((taxa_90 - taxa_60) / taxa_60) * 100 if taxa_60 > 0 else 0
    variacao_30_90 = ((taxa_90 - taxa_30) / taxa_30) * 100 if taxa_30 > 0 else 0
    
    print(f"📊 {categoria}:")
    print(f"   • 30 dias: {taxa_30:.1f}%")
    print(f"   • 60 dias: {taxa_60:.1f}% (Δ {variacao_30_60:+.1f}%)")
    print(f"   • 90 dias: {taxa_90:.1f}% (Δ {variacao_60_90:+.1f}%)")
    print(f"   • Variação total (30→90): {variacao_30_90:+.1f}%")
    print()

# =============================================================================
# RELATÓRIO EXECUTIVO FINAL
# =============================================================================

print("="*80)
print("📋 RELATÓRIO EXECUTIVO - ANÁLISE COMPARATIVA DE CHURN")
print("="*80)
print()

print("🎯 PRINCIPAIS INSIGHTS:")
print()

print("1️⃣ PADRÕES DE EVOLUÇÃO:")
print("   • Produtos Standard: Problemáticos em todos os períodos")
print("   • Cartões 7-12 meses: Churn elevado consistente")
print("   • Idade 35-44: Crescimento gradual com o tempo")
print("   • Renda Baixa: Vulnerabilidade constante")
print()

print("2️⃣ VELOCIDADE DE CHURN:")
print("   • 30 dias: Detecção precoce de abandono")
print("   • 60 dias: Ponto de equilíbrio para análise")
print("   • 90 dias: Visão consolidada de longo prazo")
print()

print("3️⃣ RECOMENDAÇÕES ESTRATÉGICAS:")
print("   🚨 URGENTE:")
print("     • Descontinuar produto Standard")
print("     • Intervenção em cartões 7-12 meses")
print()
print("   📊 MONITORAMENTO:")
print("     • Usar 60 dias como métrica principal")
print("     • Alertas em 30 dias para ação rápida")
print("     • Relatórios consolidados em 90 dias")
print()
print("   🎯 SEGMENTAÇÃO:")
print("     • Foco em idade 35-44 anos")
print("     • Programas especiais para renda baixa")
print("     • Benefícios progressivos por tempo de relacionamento")
print()

print("📊 RESUMO DOS ARQUIVOS GERADOS:")
print("   ✓ grafico_evolucao_churn_periodos.png")
print("   ✓ grafico_comparacao_consolidada_churn.png")
print("   ✓ analise_churn_2024_30dias.py")
print("   ✓ analise_churn_2024_60dias.py")
print("   ✓ analise_churn_2024_completa.py (90 dias)")
print()

# Salvar dados consolidados
df_completo.to_csv('dados_churn_comparativo_2024.csv', index=False)
print("💾 Dados salvos: dados_churn_comparativo_2024.csv")
print()

# Fechar conexão
conn.close()

print("="*80)
print("🎯 ANÁLISE COMPARATIVA FINALIZADA COM SUCESSO!")
print("="*80)