#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Análise de Churn 2024 - Versão Corrigida (60 dias de inatividade)
=================================================================

IMPORTANTE: Esta análise considera TODOS os clientes que fizeram churn em 2024,
independentemente de quando criaram a conta ou emitiram o cartão.

Objetivo: Entender o impacto no marketshare de 2024 causado por todos os churns,
incluindo clientes antigos que saíram em 2024.

Data de referência: 2024-12-30
Critério de churn: Sem transações nos últimos 60 dias (desde 2024-10-31)
Cartões: Dados válidos a partir de 01/01/2023 (devido às inconsistências)
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
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)

def conectar_db():
    """Conecta ao banco de dados SQLite."""
    try:
        conn = sqlite3.connect('priceless_bank.db')
        print("✅ Conexão com banco de dados estabelecida")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def criar_grafico_churn(dados, titulo, nome_arquivo, rotulo_x, tipo='bar'):
    """
    Cria gráficos padronizados para análise de churn.
    
    Parâmetros:
    - dados: DataFrame com os dados
    - titulo: Título do gráfico
    - nome_arquivo: Nome do arquivo para salvar
    - rotulo_x: Rótulo do eixo X
    - tipo: Tipo do gráfico ('bar', 'pie', 'heatmap')
    """
    plt.figure(figsize=(14, 8))
    
    if tipo == 'bar':
        # Gráfico de barras
        ax = plt.subplot(111)
        cores = ['#e74c3c', '#3498db']  # Vermelho para churn, azul para ativo
        
        # Dados para o gráfico
        categorias = dados[dados.columns[0]].tolist()
        valores_churn = dados['clientes_churn'].tolist()
        valores_ativo = dados['clientes_ativos'].tolist()
        
        x = np.arange(len(categorias))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, valores_churn, width, label='Churn', color=cores[0], alpha=0.8)
        bars2 = ax.bar(x + width/2, valores_ativo, width, label='Ativos', color=cores[1], alpha=0.8)
        
        # Adicionar valores nas barras
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(valores_churn + valores_ativo) * 0.01,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(valores_churn + valores_ativo) * 0.01,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel(rotulo_x, fontweight='bold')
        ax.set_ylabel('Número de Clientes', fontweight='bold')
        ax.set_title(titulo, fontweight='bold', fontsize=14, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adicionar percentuais de churn como texto
        for i, categoria in enumerate(categorias):
            total = valores_churn[i] + valores_ativo[i]
            if total > 0:
                perc_churn = (valores_churn[i] / total) * 100
                ax.text(i, max(valores_churn + valores_ativo) * 0.9, 
                       f'Churn: {perc_churn:.1f}%', 
                       ha='center', va='center', 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7),
                       fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print(f"📊 Gráfico salvo: {nome_arquivo}")

def analise_1_idade_churn(conn):
    """1. Análise de Churn por Faixa Etária - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("1. ANÁLISE DE CHURN POR FAIXA ETÁRIA (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Idade
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
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
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Faixa Etária\n(Todos os churns de 2024 - 60 dias inatividade)',
        'grafico_1_idade_churn_60dias_corrigido.png',
        'Faixa Etária'
    )
    
    return df

def analise_2_renda_churn(conn):
    """2. Análise de Churn por Faixa de Renda - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("2. ANÁLISE DE CHURN POR FAIXA DE RENDA (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Renda
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        CASE 
            WHEN tc.Renda < 3000 THEN 'Até R$ 3.000'
            WHEN tc.Renda BETWEEN 3000 AND 6000 THEN 'R$ 3.000 - R$ 6.000'
            WHEN tc.Renda BETWEEN 6000 AND 10000 THEN 'R$ 6.000 - R$ 10.000'
            WHEN tc.Renda BETWEEN 10000 AND 20000 THEN 'R$ 10.000 - R$ 20.000'
            WHEN tc.Renda > 20000 THEN 'Acima de R$ 20.000'
            ELSE 'Não informado'
        END as faixa_renda,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Faixa de Renda\n(Todos os churns de 2024 - 60 dias inatividade)',
        'grafico_2_renda_churn_60dias_corrigido.png',
        'Faixa de Renda'
    )
    
    return df

def analise_3_tempo_conta_churn(conn):
    """3. Análise de Churn por Tempo desde Criação da Conta - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("3. ANÁLISE DE CHURN POR TEMPO DESDE CRIAÇÃO DA CONTA (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, 
               ROUND((JULIANDAY('2024-12-30') - JULIANDAY(c.Data_Criacao_Conta)) / 30.44) as meses_conta
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        CASE 
            WHEN tc.meses_conta <= 6 THEN '0-6 meses'
            WHEN tc.meses_conta <= 12 THEN '7-12 meses'
            WHEN tc.meses_conta <= 24 THEN '13-24 meses'
            WHEN tc.meses_conta <= 36 THEN '25-36 meses'
            ELSE 'Mais de 36 meses'
        END as tempo_conta,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Tempo de Conta\n(Todos os churns de 2024 - 60 dias inatividade)',
        'grafico_3_tempo_conta_churn_60dias_corrigido.png',
        'Tempo desde Criação da Conta'
    )
    
    return df

def analise_4_conta_adicional_churn(conn):
    """4. Análise de Churn por Conta Adicional - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("4. ANÁLISE DE CHURN POR CONTA ADICIONAL (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Conta_Adicional
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        CASE 
            WHEN tc.Conta_Adicional = 'Sim' THEN 'Com Conta Adicional'
            ELSE 'Sem Conta Adicional'
        END as status_conta_adicional,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1
    ORDER BY 2 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Conta Adicional\n(Todos os churns de 2024 - 60 dias inatividade)',
        'grafico_4_conta_adicional_churn_60dias_corrigido.png',
        'Status da Conta Adicional'
    )
    
    return df

def analise_5_estado_churn(conn):
    """5. Análise de Churn por Estado - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("5. ANÁLISE DE CHURN POR ESTADO (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Estado
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        tc.Estado,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY tc.Estado
    HAVING COUNT(*) >= 18  -- Apenas estados com pelo menos 18 clientes (ajustado para 60 dias)
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Estado\n(Todos os churns de 2024 - 60 dias inatividade)',
        'grafico_5_estado_churn_60dias_corrigido.png',
        'Estado'
    )
    
    return df

def analise_6_tipo_cartao_churn(conn):
    """6. Análise de Churn por Tipo de Cartão - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("6. ANÁLISE DE CHURN POR TIPO DE CARTÃO (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT t.Cliente_ID as cliente_id, cart.Tipo_Cartao as Tipo
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        INNER JOIN clientes c ON t.Cliente_ID = c.cliente_id
        WHERE cart.Data_Emissao >= '2023-01-01'  -- Dados válidos a partir de 2023
        AND cart.Data_Emissao >= c.Data_Criacao_Conta  -- Cartão emitido após criação da conta
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        tc.Tipo as tipo_cartao,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY tc.Tipo
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Tipo de Cartão\n(Todos os churns de 2024 - 60 dias - Dados válidos desde 2023)',
        'grafico_6_tipo_cartao_churn_60dias_corrigido.png',
        'Tipo de Cartão'
    )
    
    return df

def analise_7_produto_mastercard_churn(conn):
    """7. Análise de Churn por Produto Mastercard - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("7. ANÁLISE DE CHURN POR PRODUTO MASTERCARD (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT t.Cliente_ID as cliente_id, cart.Produto_Mastercard
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        INNER JOIN clientes c ON t.Cliente_ID = c.cliente_id
        WHERE cart.Data_Emissao >= '2023-01-01'  -- Dados válidos a partir de 2023
        AND cart.Data_Emissao >= c.Data_Criacao_Conta  -- Cartão emitido após criação da conta
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        tc.Produto_Mastercard as produto_mastercard,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY tc.Produto_Mastercard
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Produto Mastercard\n(Todos os churns de 2024 - 60 dias - Dados válidos desde 2023)',
        'grafico_7_produto_mastercard_churn_60dias_corrigido.png',
        'Produto Mastercard'
    )
    
    return df

def analise_8_tempo_cartao_churn(conn):
    """8. Análise de Churn por Tempo desde Emissão do Cartão - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("8. ANÁLISE DE CHURN POR TEMPO DESDE EMISSÃO DO CARTÃO (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT t.Cliente_ID as cliente_id, 
               ROUND((JULIANDAY('2024-12-30') - JULIANDAY(cart.Data_Emissao)) / 30.44) as meses_cartao
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        INNER JOIN clientes c ON t.Cliente_ID = c.cliente_id
        WHERE cart.Data_Emissao >= '2023-01-01'  -- Dados válidos a partir de 2023
        AND cart.Data_Emissao >= c.Data_Criacao_Conta  -- Cartão emitido após criação da conta
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        CASE 
            WHEN tc.meses_cartao <= 6 THEN '0-6 meses'
            WHEN tc.meses_cartao <= 12 THEN '7-12 meses'
            WHEN tc.meses_cartao <= 24 THEN '13-24 meses'
            WHEN tc.meses_cartao <= 36 THEN '25-36 meses'
            ELSE 'Mais de 36 meses'
        END as tempo_cartao,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Tempo de Cartão\n(Todos os churns de 2024 - 60 dias - Dados válidos desde 2023)',
        'grafico_8_tempo_cartao_churn_60dias_corrigido.png',
        'Tempo desde Emissão do Cartão'
    )
    
    return df

def analise_9_limite_cartao_churn(conn):
    """9. Análise de Churn por Limite do Cartão - TODOS os clientes que saíram em 2024 (60 dias)"""
    print("\n" + "="*60)
    print("9. ANÁLISE DE CHURN POR LIMITE DO CARTÃO (60 DIAS)")
    print("="*60)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT t.Cliente_ID as cliente_id, cart.Limite_Cartao as Limite
        FROM transacoes t
        INNER JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        INNER JOIN clientes c ON t.Cliente_ID = c.cliente_id
        WHERE cart.Data_Emissao >= '2023-01-01'  -- Dados válidos a partir de 2023
        AND cart.Data_Emissao >= c.Data_Criacao_Conta  -- Cartão emitido após criação da conta
        AND cart.Limite_Cartao IS NOT NULL
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        CASE 
            WHEN tc.Limite < 1000 THEN 'Até R$ 1.000'
            WHEN tc.Limite BETWEEN 1000 AND 2500 THEN 'R$ 1.000 - R$ 2.500'
            WHEN tc.Limite BETWEEN 2500 AND 5000 THEN 'R$ 2.500 - R$ 5.000'
            WHEN tc.Limite BETWEEN 5000 AND 10000 THEN 'R$ 5.000 - R$ 10.000'
            WHEN tc.Limite > 10000 THEN 'Acima de R$ 10.000'
            ELSE 'Não informado'
        END as faixa_limite,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(CASE WHEN cc.cliente_id IS NULL THEN 1 END) as clientes_ativos,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1
    ORDER BY 5 DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    criar_grafico_churn(
        df, 
        'Análise de Churn por Limite do Cartão\n(Todos os churns de 2024 - 60 dias - Dados válidos desde 2023)',
        'grafico_9_limite_cartao_churn_60dias_corrigido.png',
        'Faixa de Limite'
    )
    
    return df

def resumo_executivo_churn(conn):
    """Gera um resumo executivo completo da análise de churn corrigida (60 dias)"""
    print("\n" + "="*80)
    print("RESUMO EXECUTIVO - ANÁLISE DE CHURN 2024 (60 DIAS - VERSÃO CORRIGIDA)")
    print("="*80)
    
    # 1. Estatísticas gerais
    query_geral = """
    WITH todos_clientes AS (
        SELECT DISTINCT Cliente_ID as cliente_id
        FROM transacoes
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        COUNT(*) as total_clientes_ativos_historico,
        (SELECT COUNT(*) FROM clientes_churn) as total_clientes_churn,
        (SELECT COUNT(*) FROM todos_clientes) - (SELECT COUNT(*) FROM clientes_churn) as clientes_ainda_ativos,
        ROUND((SELECT COUNT(*) FROM clientes_churn) * 100.0 / COUNT(*), 2) as taxa_churn_geral
    FROM todos_clientes;
    """
    
    df_geral = pd.read_sql_query(query_geral, conn)
    
    print("\n📊 ESTATÍSTICAS GERAIS (60 DIAS INATIVIDADE):")
    print(f"• Total de clientes que já fizeram transações: {df_geral.iloc[0]['total_clientes_ativos_historico']:,}")
    print(f"• Clientes em churn (60 dias sem transação): {df_geral.iloc[0]['total_clientes_churn']:,}")
    print(f"• Clientes ainda ativos: {df_geral.iloc[0]['clientes_ainda_ativos']:,}")
    print(f"• Taxa de churn geral: {df_geral.iloc[0]['taxa_churn_geral']}%")
    
    # 2. Análise temporal dos churns
    query_temporal = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Data_Criacao_Conta
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    )
    SELECT 
        CASE 
            WHEN strftime('%Y', tc.Data_Criacao_Conta) = '2024' THEN 'Conta criada em 2024'
            ELSE 'Conta criada antes de 2024'
        END as periodo_criacao,
        COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) as clientes_churn,
        COUNT(*) as total_clientes,
        ROUND(COUNT(CASE WHEN cc.cliente_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as taxa_churn
    FROM todos_clientes tc
    LEFT JOIN clientes_churn cc ON tc.cliente_id = cc.cliente_id
    GROUP BY 1;
    """
    
    df_temporal = pd.read_sql_query(query_temporal, conn)
    
    print(f"\n🕐 ANÁLISE TEMPORAL DOS CHURNS (60 DIAS):")
    for _, row in df_temporal.iterrows():
        print(f"• {row['periodo_criacao']}: {row['clientes_churn']:,} churns ({row['taxa_churn']}%)")
    
    return {
        'geral': df_geral,
        'temporal': df_temporal
    }

def main():
    """Função principal que executa todas as análises"""
    print("🚀 INICIANDO ANÁLISE DE CHURN 2024 - VERSÃO CORRIGIDA (60 DIAS)")
    print("="*80)
    print("📌 IMPORTANTE: Esta análise considera TODOS os clientes que saíram em 2024,")
    print("   independentemente de quando criaram a conta ou emitiram o cartão.")
    print("📌 Critério: 60 dias de inatividade desde 31/10/2024")
    print("📌 Dados de cartão: válidos a partir de 01/01/2023")
    print("="*80)
    
    conn = conectar_db()
    if not conn:
        return
    
    try:
        # Executar todas as análises
        resultados = {}
        
        resultados['idade'] = analise_1_idade_churn(conn)
        resultados['renda'] = analise_2_renda_churn(conn)
        resultados['tempo_conta'] = analise_3_tempo_conta_churn(conn)
        resultados['conta_adicional'] = analise_4_conta_adicional_churn(conn)
        resultados['estado'] = analise_5_estado_churn(conn)
        resultados['tipo_cartao'] = analise_6_tipo_cartao_churn(conn)
        resultados['produto_mastercard'] = analise_7_produto_mastercard_churn(conn)
        resultados['tempo_cartao'] = analise_8_tempo_cartao_churn(conn)
        resultados['limite_cartao'] = analise_9_limite_cartao_churn(conn)
        
        # Resumo executivo
        resumo = resumo_executivo_churn(conn)
        
        print("\n" + "="*80)
        print("✅ ANÁLISE COMPLETA FINALIZADA!")
        print("="*80)
        print("📁 Gráficos salvos com sufixo '_60dias_corrigido.png'")
        print("🎯 Esta versão captura o impacto real no marketshare de 2024")
        print("💡 Inclui clientes antigos que saíram em 2024 (60 dias de inatividade)")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("🔐 Conexão com banco de dados fechada")

if __name__ == "__main__":
    main()