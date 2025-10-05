#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Análise Completa de Churn 2024 - Identificação dos Motivos da Perda de Marketshare
=================================================================================

METODOLOGIA CORRIGIDA:
- BASE: TODOS os clientes cadastrados (2023 + 2024)
- FOCO: Status desses clientes em 2024 
- CATEGORIAS:
  1. NUNCA ATIVARAM: Clientes que criaram conta mas nunca fizeram transações
  2. INATIVOS: Clientes que fizeram transações mas estão 90+ dias sem transacionar (desde 01/10/2024)
  3. ATIVOS: Clientes que transacionaram nos últimos 90 dias

ANÁLISES DETALHADAS (7 DIMENSÕES):
1. Idade
2. Renda
3. Tempo de conta
4. Tipo de cartão
5. Produto Mastercard
6. Tempo de cartão  
7. Limite de cartão

OBJETIVO: Identificar onde está o problema da empresa e os motivos específicos do churn em 2024
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração para gráficos em português
plt.rcParams['font.size'] = 11
plt.rcParams['figure.figsize'] = (18, 12)
sns.set_palette("husl")

def conectar_db():
    """Conecta ao banco de dados SQLite."""
    try:
        conn = sqlite3.connect('priceless_bank.db')
        print("✅ Conexão com banco de dados estabelecida")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def criar_grafico_churn_completo(dados, titulo, nome_arquivo, rotulo_x, dimensao):
    """
    Cria análise gráfica completa para cada dimensão
    4 gráficos: Distribuição geral, Taxas de churn, Comparativo grupos, Heatmap
    """
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(f'{titulo}\n(Análise Completa de Churn 2024)', fontsize=18, fontweight='bold', y=0.98)
    
    # Preparar dados
    categorias = dados[dados.columns[0]].tolist()
    nunca_ativaram = dados['nunca_ativaram'].tolist()
    inativos = dados['inativos'].tolist()
    ativos = dados['ativos'].tolist()
    
    # Calcular totais e percentuais
    totais = [nunca_ativaram[i] + inativos[i] + ativos[i] for i in range(len(categorias))]
    perc_nunca = [(nunca_ativaram[i]/totais[i]*100) if totais[i] > 0 else 0 for i in range(len(categorias))]
    perc_inativos = [(inativos[i]/totais[i]*100) if totais[i] > 0 else 0 for i in range(len(categorias))]
    perc_ativos = [(ativos[i]/totais[i]*100) if totais[i] > 0 else 0 for i in range(len(categorias))]
    impacto_total = [perc_nunca[i] + perc_inativos[i] for i in range(len(categorias))]
    
    # Definir cores consistentes
    cores = ['#e74c3c', '#f39c12', '#27ae60']  # Vermelho, laranja, verde
    
    # GRÁFICO 1: Distribuição Absoluta (Barras Empilhadas)
    ax1 = plt.subplot(2, 2, 1)
    x = np.arange(len(categorias))
    
    bars1 = ax1.bar(x, nunca_ativaram, label='Nunca Ativaram', color=cores[0], alpha=0.85)
    bars2 = ax1.bar(x, inativos, bottom=nunca_ativaram, label='Inativos (90+ dias)', color=cores[1], alpha=0.85)
    bars3 = ax1.bar(x, ativos, bottom=[nunca_ativaram[i] + inativos[i] for i in range(len(categorias))], 
                   label='Ativos', color=cores[2], alpha=0.85)
    
    ax1.set_xlabel(rotulo_x, fontweight='bold')
    ax1.set_ylabel('Número de Clientes', fontweight='bold')
    ax1.set_title('Distribuição por Status (Números Absolutos)', fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categorias, rotation=45, ha='right')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for i, (nunca, inativo, ativo) in enumerate(zip(nunca_ativaram, inativos, ativos)):
        if nunca > 0:
            ax1.text(i, nunca/2, f'{nunca}', ha='center', va='center', fontweight='bold', color='white')
        if inativo > 0:
            ax1.text(i, nunca + inativo/2, f'{inativo}', ha='center', va='center', fontweight='bold', color='white')
        if ativo > 0:
            ax1.text(i, nunca + inativo + ativo/2, f'{ativo}', ha='center', va='center', fontweight='bold', color='white')
    
    # GRÁFICO 2: Taxas de Impacto (% de problemas)
    ax2 = plt.subplot(2, 2, 2)
    
    bars_nunca = ax2.bar(x - 0.2, perc_nunca, 0.4, label='% Nunca Ativaram', color=cores[0], alpha=0.85)
    bars_inativos = ax2.bar(x + 0.2, perc_inativos, 0.4, label='% Inativos', color=cores[1], alpha=0.85)
    
    ax2.set_xlabel(rotulo_x, fontweight='bold')
    ax2.set_ylabel('Percentual (%)', fontweight='bold')
    ax2.set_title('Taxas de Churn por Categoria', fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categorias, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for i, (p_nunca, p_inativo) in enumerate(zip(perc_nunca, perc_inativos)):
        if p_nunca > 0:
            ax2.text(i - 0.2, p_nunca + 1, f'{p_nunca:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
        if p_inativo > 0:
            ax2.text(i + 0.2, p_inativo + 1, f'{p_inativo:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # GRÁFICO 3: Impacto Total vs Retenção
    ax3 = plt.subplot(2, 2, 3)
    
    bars_problema = ax3.bar(x, impacto_total, label='Impacto Total (Nunca + Inativos)', color='#c0392b', alpha=0.85)
    bars_sucesso = ax3.bar(x, perc_ativos, bottom=impacto_total, label='Retenção (Ativos)', color='#27ae60', alpha=0.85)
    
    ax3.set_xlabel(rotulo_x, fontweight='bold')
    ax3.set_ylabel('Percentual (%)', fontweight='bold')
    ax3.set_title('Impacto Total vs Retenção por Categoria', fontweight='bold', pad=15)
    ax3.set_xticks(x)
    ax3.set_xticklabels(categorias, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_ylim(0, 100)
    
    # Adicionar linha de referência em 50%
    ax3.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Linha Crítica (50%)')
    
    # Adicionar valores de impacto
    for i, impacto in enumerate(impacto_total):
        if impacto > 5:  # Só mostrar se for significativo
            ax3.text(i, impacto/2, f'{impacto:.1f}%', ha='center', va='center', 
                    fontweight='bold', color='white', fontsize=10)
    
    # GRÁFICO 4: Análise de Risco (Heatmap de problemas)
    ax4 = plt.subplot(2, 2, 4)
    
    # Criar matriz para heatmap
    data_matrix = np.array([perc_nunca, perc_inativos, impacto_total]).T
    
    im = ax4.imshow(data_matrix, cmap='Reds', aspect='auto', alpha=0.8)
    
    # Configurar eixos
    ax4.set_xticks([0, 1, 2])
    ax4.set_xticklabels(['Nunca Ativaram (%)', 'Inativos (%)', 'Impacto Total (%)'], fontweight='bold')
    ax4.set_yticks(range(len(categorias)))
    ax4.set_yticklabels(categorias, fontweight='bold')
    ax4.set_title(f'Mapa de Calor - Problemas por {dimensao}', fontweight='bold', pad=15)
    
    # Adicionar valores no heatmap
    for i in range(len(categorias)):
        for j in range(3):
            value = data_matrix[i, j]
            color = 'white' if value > 20 else 'black'
            ax4.text(j, i, f'{value:.1f}%', ha='center', va='center', 
                    color=color, fontweight='bold', fontsize=9)
    
    # Adicionar colorbar
    cbar = plt.colorbar(im, ax=ax4, shrink=0.6)
    cbar.set_label('Percentual de Problemas', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print(f"📊 Análise completa salva: {nome_arquivo}")

def analise_base_completa(conn):
    """Análise base para entender a situação geral"""
    print("\n" + "="*100)
    print("ANÁLISE BASE COMPLETA - TODOS OS CLIENTES E STATUS EM 2024")
    print("="*100)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT cliente_id, Data_Criacao_Conta,
               strftime('%Y', Data_Criacao_Conta) as ano_criacao
        FROM clientes
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        'TOTAL CLIENTES CADASTRADOS (2023+2024)' as categoria,
        COUNT(*) as quantidade,
        '' as detalhes
    FROM todos_clientes
    
    UNION ALL
    
    SELECT 
        'Clientes cadastrados em 2023' as categoria,
        COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM todos_clientes), 1) || '%' as detalhes
    FROM todos_clientes WHERE ano_criacao = '2023'
    
    UNION ALL
    
    SELECT 
        'Clientes cadastrados em 2024' as categoria,
        COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM todos_clientes), 1) || '%' as detalhes
    FROM todos_clientes WHERE ano_criacao = '2024'
    
    UNION ALL
    
    SELECT 
        '--- STATUS EM 2024 (TODOS OS CLIENTES) ---' as categoria,
        0 as quantidade,
        '' as detalhes
    
    UNION ALL
    
    SELECT 
        'NUNCA ATIVARAM (sem transações)' as categoria,
        COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM todos_clientes), 1) || '%' as detalhes
    FROM todos_clientes tc
    WHERE tc.cliente_id NOT IN (SELECT cliente_id FROM clientes_com_transacoes)
    
    UNION ALL
    
    SELECT 
        'INATIVOS (90+ dias sem transação)' as categoria,
        COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM todos_clientes), 1) || '%' as detalhes
    FROM clientes_com_transacoes cct
    WHERE cct.cliente_id NOT IN (SELECT cliente_id FROM clientes_ativos_2024)
    
    UNION ALL
    
    SELECT 
        'ATIVOS (transacionaram < 90 dias)' as categoria,
        COUNT(*) as quantidade,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM todos_clientes), 1) || '%' as detalhes
    FROM clientes_ativos_2024
    
    UNION ALL
    
    SELECT 
        '--- IMPACTO TOTAL DO CHURN ---' as categoria,
        0 as quantidade,
        '' as detalhes
    
    UNION ALL
    
    SELECT 
        'TOTAL COM PROBLEMAS (Nunca + Inativos)' as categoria,
        (SELECT COUNT(*) FROM todos_clientes tc WHERE tc.cliente_id NOT IN (SELECT cliente_id FROM clientes_com_transacoes)) +
        (SELECT COUNT(*) FROM clientes_com_transacoes cct WHERE cct.cliente_id NOT IN (SELECT cliente_id FROM clientes_ativos_2024)) as quantidade,
        ROUND(((SELECT COUNT(*) FROM todos_clientes tc WHERE tc.cliente_id NOT IN (SELECT cliente_id FROM clientes_com_transacoes)) +
               (SELECT COUNT(*) FROM clientes_com_transacoes cct WHERE cct.cliente_id NOT IN (SELECT cliente_id FROM clientes_ativos_2024))) * 100.0 / 
               (SELECT COUNT(*) FROM todos_clientes), 1) || '%' as detalhes;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    return df

def analise_1_idade_completa(conn):
    """1. Análise Completa por Faixa Etária"""
    print("\n" + "="*100)
    print("1. ANÁLISE COMPLETA POR FAIXA ETÁRIA - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Idade
        FROM clientes c
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        CASE 
            WHEN tc.Idade BETWEEN 18 AND 25 THEN '18-25 anos'
            WHEN tc.Idade BETWEEN 26 AND 35 THEN '26-35 anos'
            WHEN tc.Idade BETWEEN 36 AND 45 THEN '36-45 anos'
            WHEN tc.Idade BETWEEN 46 AND 55 THEN '46-55 anos'
            WHEN tc.Idade > 55 THEN '55+ anos'
            ELSE 'Não informado'
        END as faixa_etaria,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM todos_clientes tc
    LEFT JOIN clientes_com_transacoes cct ON tc.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON tc.cliente_id = ca2024.cliente_id
    GROUP BY 1
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR FAIXA ETÁRIA:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['faixa_etaria']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['faixa_etaria']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 1: Churn por Faixa Etária',
        'analise_completa_1_idade_churn_2024.png',
        'Faixa Etária',
        'Idade'
    )
    
    return df

def analise_2_renda_completa(conn):
    """2. Análise Completa por Faixa de Renda"""
    print("\n" + "="*100)
    print("2. ANÁLISE COMPLETA POR FAIXA DE RENDA - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.Cliente_ID as cliente_id, c.Renda_Anual as renda
        FROM clientes c
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        CASE 
            WHEN tc.renda < 50000 THEN 'Até R$ 50.000/ano'
            WHEN tc.renda BETWEEN 50000 AND 80000 THEN 'R$ 50.000 - R$ 80.000/ano'
            WHEN tc.renda BETWEEN 80000 AND 120000 THEN 'R$ 80.000 - R$ 120.000/ano'
            WHEN tc.renda > 120000 THEN 'Acima de R$ 120.000/ano'
            ELSE 'Não informado'
        END as faixa_renda,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM todos_clientes tc
    LEFT JOIN clientes_com_transacoes cct ON tc.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON tc.cliente_id = ca2024.cliente_id
    GROUP BY 1
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR FAIXA DE RENDA:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['faixa_renda']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['faixa_renda']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 2: Churn por Faixa de Renda',
        'analise_completa_2_renda_churn_2024.png',
        'Faixa de Renda',
        'Renda'
    )
    
    return df

def analise_3_tempo_conta_completa(conn):
    """3. Análise Completa por Tempo de Conta"""
    print("\n" + "="*100)
    print("3. ANÁLISE COMPLETA POR TEMPO DE CONTA - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.Cliente_ID as cliente_id, 
               ROUND((JULIANDAY('2024-12-30') - JULIANDAY(c.Data_Criacao_Conta)) / 30.44) as meses_conta
        FROM clientes c
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        CASE 
            WHEN tc.meses_conta <= 6 THEN '0-6 meses'
            WHEN tc.meses_conta <= 12 THEN '7-12 meses'
            WHEN tc.meses_conta <= 24 THEN '13-24 meses'
            WHEN tc.meses_conta <= 36 THEN '25-36 meses'
            ELSE 'Mais de 36 meses'
        END as tempo_conta,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM todos_clientes tc
    LEFT JOIN clientes_com_transacoes cct ON tc.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON tc.cliente_id = ca2024.cliente_id
    GROUP BY 1
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR TEMPO DE CONTA:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['tempo_conta']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['tempo_conta']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 3: Churn por Tempo de Conta',
        'analise_completa_3_tempo_conta_churn_2024.png',
        'Tempo de Conta',
        'Tempo de Relacionamento'
    )
    
    return df

def analise_4_tipo_cartao_completa(conn):
    """4. Análise Completa por Tipo de Cartão"""
    print("\n" + "="*100)
    print("4. ANÁLISE COMPLETA POR TIPO DE CARTÃO - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id
        FROM clientes c
    ),
    clientes_cartoes AS (
        SELECT DISTINCT 
            t.Cliente_ID as cliente_id,
            cart.Tipo_Cartao as tipo_cartao
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        UNION
        -- Clientes sem cartão definido (nunca transacionaram)
        SELECT DISTINCT 
            c.Cliente_ID as cliente_id,
            'Sem Cartão Ativo' as tipo_cartao
        FROM clientes c
        WHERE c.Cliente_ID NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes
        )
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        cc.tipo_cartao,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM clientes_cartoes cc
    LEFT JOIN clientes_com_transacoes cct ON cc.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON cc.cliente_id = ca2024.cliente_id
    GROUP BY cc.tipo_cartao
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR TIPO DE CARTÃO:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['tipo_cartao']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['tipo_cartao']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 4: Churn por Tipo de Cartão',
        'analise_completa_4_tipo_cartao_churn_2024.png',
        'Tipo de Cartão',
        'Produto'
    )
    
    return df

def analise_5_produto_mastercard_completa(conn):
    """5. Análise Completa por Produto Mastercard"""
    print("\n" + "="*100)
    print("5. ANÁLISE COMPLETA POR PRODUTO MASTERCARD - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH clientes_produtos AS (
        SELECT DISTINCT 
            t.Cliente_ID as cliente_id,
            COALESCE(cart.Produto_Mastercard, 'Não Identificado') as produto_mastercard
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        UNION
        -- Clientes sem produto definido (nunca transacionaram)
        SELECT DISTINCT 
            c.Cliente_ID as cliente_id,
            'Sem Produto Ativo' as produto_mastercard
        FROM clientes c
        WHERE c.Cliente_ID NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes
        )
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        cp.produto_mastercard,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM clientes_produtos cp
    LEFT JOIN clientes_com_transacoes cct ON cp.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON cp.cliente_id = ca2024.cliente_id
    GROUP BY cp.produto_mastercard
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR PRODUTO MASTERCARD:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['produto_mastercard']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['produto_mastercard']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 5: Churn por Produto Mastercard',
        'analise_completa_5_produto_mastercard_churn_2024.png',
        'Produto Mastercard',
        'Linha de Produto'
    )
    
    return df

def analise_6_tempo_cartao_completa(conn):
    """6. Análise Completa por Tempo de Cartão"""
    print("\n" + "="*100)
    print("6. ANÁLISE COMPLETA POR TEMPO DE CARTÃO - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH clientes_tempo_cartao AS (
        SELECT DISTINCT 
            t.Cliente_ID as cliente_id,
            ROUND((JULIANDAY('2024-12-30') - JULIANDAY(cart.Data_Emissao)) / 30.44) as meses_cartao
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        UNION
        -- Clientes sem cartão ativo
        SELECT DISTINCT 
            c.Cliente_ID as cliente_id,
            -1 as meses_cartao  -- Código especial para sem cartão
        FROM clientes c
        WHERE c.Cliente_ID NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes
        )
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        CASE 
            WHEN ctc.meses_cartao = -1 THEN 'Sem Cartão Ativo'
            WHEN ctc.meses_cartao <= 6 THEN '0-6 meses'
            WHEN ctc.meses_cartao <= 12 THEN '7-12 meses'
            WHEN ctc.meses_cartao <= 24 THEN '13-24 meses'
            WHEN ctc.meses_cartao <= 36 THEN '25-36 meses'
            ELSE 'Mais de 36 meses'
        END as tempo_cartao,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM clientes_tempo_cartao ctc
    LEFT JOIN clientes_com_transacoes cct ON ctc.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON ctc.cliente_id = ca2024.cliente_id
    GROUP BY 1
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR TEMPO DE CARTÃO:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['tempo_cartao']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['tempo_cartao']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 6: Churn por Tempo de Cartão',
        'analise_completa_6_tempo_cartao_churn_2024.png',
        'Tempo de Cartão',
        'Maturidade do Cartão'
    )
    
    return df

def analise_7_limite_cartao_completa(conn):
    """7. Análise Completa por Limite de Cartão"""
    print("\n" + "="*100)
    print("7. ANÁLISE COMPLETA POR LIMITE DE CARTÃO - IDENTIFICAÇÃO DOS PROBLEMAS")
    print("="*100)
    
    query = """
    WITH clientes_limite AS (
        SELECT DISTINCT 
            t.Cliente_ID as cliente_id,
            cart.Limite_Cartao as limite
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        WHERE cart.Limite_Cartao IS NOT NULL
        UNION
        -- Clientes sem limite definido
        SELECT DISTINCT 
            c.Cliente_ID as cliente_id,
            -1 as limite  -- Código especial para sem limite
        FROM clientes c
        WHERE c.Cliente_ID NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes
        )
    ),
    clientes_com_transacoes AS (
        SELECT DISTINCT Cliente_ID as cliente_id FROM transacoes
    ),
    clientes_ativos_2024 AS (
        SELECT DISTINCT Cliente_ID as cliente_id 
        FROM transacoes 
        WHERE Data > DATE('2024-12-30', '-90 days')
    )
    SELECT 
        CASE 
            WHEN cl.limite = -1 THEN 'Sem Limite Definido'
            WHEN cl.limite = 0 THEN 'Limite Zero (Débito)'
            WHEN cl.limite < 1000 THEN 'Até R$ 1.000'
            WHEN cl.limite BETWEEN 1000 AND 2500 THEN 'R$ 1.000 - R$ 2.500'
            WHEN cl.limite BETWEEN 2500 AND 5000 THEN 'R$ 2.500 - R$ 5.000'
            WHEN cl.limite BETWEEN 5000 AND 10000 THEN 'R$ 5.000 - R$ 10.000'
            WHEN cl.limite > 10000 THEN 'Acima de R$ 10.000'
            ELSE 'Outros'
        END as faixa_limite,
        COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) as nunca_ativaram,
        COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) as inativos,
        COUNT(CASE WHEN ca2024.cliente_id IS NOT NULL THEN 1 END) as ativos,
        COUNT(*) as total,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_nunca_ativaram,
        ROUND(COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as perc_inativos,
        ROUND((COUNT(CASE WHEN cct.cliente_id IS NULL THEN 1 END) + 
               COUNT(CASE WHEN cct.cliente_id IS NOT NULL AND ca2024.cliente_id IS NULL THEN 1 END)) * 100.0 / COUNT(*), 2) as impacto_total
    FROM clientes_limite cl
    LEFT JOIN clientes_com_transacoes cct ON cl.cliente_id = cct.cliente_id
    LEFT JOIN clientes_ativos_2024 ca2024 ON cl.cliente_id = ca2024.cliente_id
    GROUP BY 1
    ORDER BY 8 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n🔍 INSIGHTS - PROBLEMAS POR LIMITE DE CARTÃO:")
    for _, row in df.iterrows():
        if row['impacto_total'] > 30:
            print(f"🚨 CRÍTICO - {row['faixa_limite']}: {row['impacto_total']:.1f}% de impacto total")
            print(f"   • {row['nunca_ativaram']} nunca ativaram ({row['perc_nunca_ativaram']:.1f}%)")
            print(f"   • {row['inativos']} ficaram inativos ({row['perc_inativos']:.1f}%)")
        elif row['impacto_total'] > 20:
            print(f"⚠️  ATENÇÃO - {row['faixa_limite']}: {row['impacto_total']:.1f}% de impacto")
    
    criar_grafico_churn_completo(
        df, 
        'PROBLEMA 7: Churn por Limite de Cartão',
        'analise_completa_7_limite_cartao_churn_2024.png',
        'Faixa de Limite',
        'Capacidade de Crédito'
    )
    
    return df

def gerar_relatorio_executivo_final(conn, resultados):
    """Gera relatório executivo final com os principais achados"""
    print("\n" + "="*100)
    print("RELATÓRIO EXECUTIVO FINAL - PRINCIPAIS PROBLEMAS IDENTIFICADOS")
    print("="*100)
    
    # Identificar os maiores problemas por dimensão
    problemas_criticos = []
    
    for dimensao, df in resultados.items():
        if df is not None and len(df) > 0:
            # Encontrar a categoria com maior impacto
            max_impacto = df['impacto_total'].max()
            categoria_problema = df[df['impacto_total'] == max_impacto].iloc[0]
            
            problemas_criticos.append({
                'dimensao': dimensao.title(),
                'categoria': categoria_problema[df.columns[0]],
                'impacto': max_impacto,
                'nunca_ativaram': categoria_problema['nunca_ativaram'],
                'inativos': categoria_problema['inativos'],
                'total': categoria_problema['total']
            })
    
    # Ordenar por impacto
    problemas_criticos.sort(key=lambda x: x['impacto'], reverse=True)
    
    print(f"\n🎯 TOP 5 MAIORES PROBLEMAS IDENTIFICADOS:")
    print("-" * 80)
    
    for i, problema in enumerate(problemas_criticos[:5]):
        print(f"{i+1}. {problema['dimensao'].upper()}: {problema['categoria']}")
        print(f"   📊 Impacto Total: {problema['impacto']:.1f}%")
        print(f"   🔴 Nunca Ativaram: {problema['nunca_ativaram']} clientes")
        print(f"   🟡 Ficaram Inativos: {problema['inativos']} clientes")
        print(f"   📈 Total Afetado: {problema['nunca_ativaram'] + problema['inativos']} de {problema['total']} clientes")
        print()
    
    print(f"\n💡 RECOMENDAÇÕES ESTRATÉGICAS:")
    print("-" * 50)
    
    # Gerar recomendações baseadas nos problemas identificados
    top_problema = problemas_criticos[0]
    
    if top_problema['nunca_ativaram'] > top_problema['inativos']:
        print("🎯 FOCO PRINCIPAL: ATIVAÇÃO DE CLIENTES")
        print("   • Implementar campanhas de onboarding mais efetivas")
        print("   • Melhorar processo de primeira utilização")
        print("   • Criar incentivos para primeira transação")
        print()
    else:
        print("🎯 FOCO PRINCIPAL: RETENÇÃO DE CLIENTES")
        print("   • Implementar programas de reengajamento")
        print("   • Criar alertas de risco de churn")
        print("   • Melhorar experiência do cliente ativo")
        print()
    
    print("📋 AÇÕES ESPECÍFICAS POR DIMENSÃO:")
    for problema in problemas_criticos[:3]:
        print(f"   • {problema['dimensao']}: Foco em {problema['categoria']}")
    
    print(f"\n🔍 CONCLUSÃO:")
    print(f"A análise identificou {len([p for p in problemas_criticos if p['impacto'] > 30])} problemas críticos")
    print(f"que estão impactando significativamente o marketshare em 2024.")

def main():
    """Função principal que executa todas as análises"""
    print("🚀 INICIANDO ANÁLISE COMPLETA DE CHURN 2024")
    print("="*100)
    print("📌 METODOLOGIA: Todos os clientes (2023+2024) com status em 2024")
    print("📌 CATEGORIAS: Nunca Ativaram vs Inativos vs Ativos")
    print("📌 ANÁLISES: 7 dimensões completas com gráficos detalhados")
    print("📌 OBJETIVO: Identificar onde está o problema da empresa")
    print("="*100)
    
    conn = conectar_db()
    if not conn:
        return
    
    try:
        # Análise base
        print("\n🔍 Executando análise base...")
        analise_base_completa(conn)
        
        # Executar todas as análises detalhadas
        print("\n🔍 Executando análises detalhadas...")
        resultados = {}
        
        resultados['idade'] = analise_1_idade_completa(conn)
        resultados['renda'] = analise_2_renda_completa(conn)
        resultados['tempo_conta'] = analise_3_tempo_conta_completa(conn)
        resultados['tipo_cartao'] = analise_4_tipo_cartao_completa(conn)
        resultados['produto_mastercard'] = analise_5_produto_mastercard_completa(conn)
        resultados['tempo_cartao'] = analise_6_tempo_cartao_completa(conn)
        resultados['limite_cartao'] = analise_7_limite_cartao_completa(conn)
        
        # Gerar relatório executivo final
        gerar_relatorio_executivo_final(conn, resultados)
        
        print("\n" + "="*100)
        print("✅ ANÁLISE COMPLETA DE CHURN 2024 FINALIZADA!")
        print("="*100)
        print("📁 Arquivos gerados:")
        print("   • analise_completa_1_idade_churn_2024.png")
        print("   • analise_completa_2_renda_churn_2024.png")
        print("   • analise_completa_3_tempo_conta_churn_2024.png")
        print("   • analise_completa_4_tipo_cartao_churn_2024.png")
        print("   • analise_completa_5_produto_mastercard_churn_2024.png")
        print("   • analise_completa_6_tempo_cartao_churn_2024.png")
        print("   • analise_completa_7_limite_cartao_churn_2024.png")
        print()
        print("🎯 ANÁLISE COMPLETA com identificação dos problemas específicos!")
        print("💡 Use os insights para desenvolver estratégias direcionadas de retenção")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("🔐 Conexão com banco de dados fechada")

if __name__ == "__main__":
    main()