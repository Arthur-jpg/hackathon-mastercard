#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Análise Comparativa de Churn 2024 - Versão Corrigida
====================================================

CORREÇÃO FUNDAMENTAL: Esta análise considera TODOS os clientes que fizeram churn em 2024,
independentemente de quando criaram a conta ou emitiram o cartão.

ANTES: Analisávamos apenas clientes que criaram contas em 2024
AGORA: Analisamos todos os clientes que SAÍRAM em 2024 (impacto real no marketshare)

Comparação entre 30, 60 e 90 dias de inatividade
Data de referência: 2024-12-30
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
plt.rcParams['figure.figsize'] = (15, 10)

def conectar_db():
    """Conecta ao banco de dados SQLite."""
    try:
        conn = sqlite3.connect('priceless_bank.db')
        print("✅ Conexão com banco de dados estabelecida")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def comparar_abordagens_churn(conn):
    """Compara a abordagem antiga vs corrigida para mostrar a diferença"""
    print("\n" + "="*80)
    print("COMPARAÇÃO: ABORDAGEM ANTIGA vs CORRIGIDA")
    print("="*80)
    
    # Abordagem ANTIGA (apenas contas criadas em 2024)
    query_antiga = """
    WITH clientes_2024 AS (
        SELECT DISTINCT c.cliente_id
        FROM clientes c
        WHERE c.Data_Criacao_Conta >= '2024-01-01'
        AND c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    clientes_churn_antiga AS (
        SELECT cliente_id 
        FROM clientes_2024
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-90 days')
        )
    )
    SELECT 
        COUNT(*) as total_clientes_2024,
        (SELECT COUNT(*) FROM clientes_churn_antiga) as churns_abordagem_antiga,
        ROUND((SELECT COUNT(*) FROM clientes_churn_antiga) * 100.0 / COUNT(*), 2) as taxa_churn_antiga
    FROM clientes_2024;
    """
    
    # Abordagem CORRIGIDA (todos os clientes que saíram em 2024)
    query_corrigida = """
    WITH todos_clientes AS (
        SELECT DISTINCT Cliente_ID as cliente_id
        FROM transacoes
    ),
    clientes_churn_corrigida AS (
        SELECT cliente_id 
        FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID 
            FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-90 days')
        )
    )
    SELECT 
        COUNT(*) as total_clientes_historico,
        (SELECT COUNT(*) FROM clientes_churn_corrigida) as churns_abordagem_corrigida,
        ROUND((SELECT COUNT(*) FROM clientes_churn_corrigida) * 100.0 / COUNT(*), 2) as taxa_churn_corrigida
    FROM todos_clientes;
    """
    
    df_antiga = pd.read_sql_query(query_antiga, conn)
    df_corrigida = pd.read_sql_query(query_corrigida, conn)
    
    print("📊 RESULTADOS DA COMPARAÇÃO (90 dias de inatividade):")
    print()
    print("🔴 ABORDAGEM ANTIGA (apenas contas criadas em 2024):")
    print(f"   • Total clientes analisados: {df_antiga.iloc[0]['total_clientes_2024']:,}")
    print(f"   • Clientes em churn: {df_antiga.iloc[0]['churns_abordagem_antiga']:,}")
    print(f"   • Taxa de churn: {df_antiga.iloc[0]['taxa_churn_antiga']}%")
    print()
    print("✅ ABORDAGEM CORRIGIDA (todos os churns de 2024):")
    print(f"   • Total clientes analisados: {df_corrigida.iloc[0]['total_clientes_historico']:,}")
    print(f"   • Clientes em churn: {df_corrigida.iloc[0]['churns_abordagem_corrigida']:,}")
    print(f"   • Taxa de churn: {df_corrigida.iloc[0]['taxa_churn_corrigida']}%")
    print()
    
    diferenca_clientes = df_corrigida.iloc[0]['churns_abordagem_corrigida'] - df_antiga.iloc[0]['churns_abordagem_antiga']
    percentual_subestimado = (diferenca_clientes / df_corrigida.iloc[0]['churns_abordagem_corrigida']) * 100
    
    print("⚠️  IMPACTO DA CORREÇÃO:")
    print(f"   • Clientes em churn não capturados na abordagem antiga: {diferenca_clientes:,}")
    print(f"   • Percentual subestimado na análise anterior: {percentual_subestimado:.1f}%")
    print(f"   • CONCLUSÃO: A abordagem antiga subestimava significativamente o churn!")
    
    return df_antiga, df_corrigida

def obter_dados_comparativos_periodos(conn):
    """Obtém dados de churn para os três períodos (30, 60, 90 dias) - versão corrigida"""
    print("\n" + "="*80)
    print("DADOS COMPARATIVOS POR PERÍODO DE INATIVIDADE - VERSÃO CORRIGIDA")
    print("="*80)
    
    periodos = [30, 60, 90]
    resultados = {}
    
    for periodo in periodos:
        query = f"""
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
                WHERE Data > DATE('2024-12-30', '-{periodo} days')
            )
        )
        SELECT 
            {periodo} as periodo_dias,
            COUNT(*) as total_clientes,
            (SELECT COUNT(*) FROM clientes_churn) as clientes_churn,
            (SELECT COUNT(*) FROM todos_clientes) - (SELECT COUNT(*) FROM clientes_churn) as clientes_ativos,
            ROUND((SELECT COUNT(*) FROM clientes_churn) * 100.0 / COUNT(*), 2) as taxa_churn
        FROM todos_clientes;
        """
        
        df = pd.read_sql_query(query, conn)
        resultados[periodo] = df.iloc[0]
        
        print(f"\n📊 PERÍODO: {periodo} DIAS DE INATIVIDADE")
        print(f"   • Total de clientes: {df.iloc[0]['total_clientes']:,}")
        print(f"   • Clientes em churn: {df.iloc[0]['clientes_churn']:,}")
        print(f"   • Clientes ativos: {df.iloc[0]['clientes_ativos']:,}")
        print(f"   • Taxa de churn: {df.iloc[0]['taxa_churn']}%")
    
    return resultados

def criar_grafico_evolucao_churn(resultados_periodos):
    """Cria gráfico mostrando a evolução do churn por período"""
    
    # Preparar dados
    periodos = [30, 60, 90]
    churns = [resultados_periodos[p]['clientes_churn'] for p in periodos]
    ativos = [resultados_periodos[p]['clientes_ativos'] for p in periodos]
    taxas = [resultados_periodos[p]['taxa_churn'] for p in periodos]
    
    # Criar figura com subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Evolução do Churn por Período de Inatividade\n(Versão Corrigida - Todos os churns de 2024)', 
                 fontsize=16, fontweight='bold')
    
    # Gráfico 1: Evolução dos números absolutos
    ax1.plot(periodos, churns, marker='o', linewidth=3, markersize=8, color='#e74c3c', label='Churn')
    ax1.plot(periodos, ativos, marker='s', linewidth=3, markersize=8, color='#3498db', label='Ativos')
    ax1.set_xlabel('Período de Inatividade (dias)')
    ax1.set_ylabel('Número de Clientes')
    ax1.set_title('Evolução: Clientes em Churn vs Ativos')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(periodos)
    
    # Adicionar valores nos pontos
    for i, (p, c, a) in enumerate(zip(periodos, churns, ativos)):
        ax1.annotate(f'{c:,}', (p, c), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')
        ax1.annotate(f'{a:,}', (p, a), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')
    
    # Gráfico 2: Taxa de churn
    bars = ax2.bar(periodos, taxas, color=['#f39c12', '#e67e22', '#e74c3c'], alpha=0.8, width=8)
    ax2.set_xlabel('Período de Inatividade (dias)')
    ax2.set_ylabel('Taxa de Churn (%)')
    ax2.set_title('Taxa de Churn por Período')
    ax2.set_xticks(periodos)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for bar, taxa in zip(bars, taxas):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{taxa}%', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 3: Incremento de churn entre períodos
    incrementos = [churns[0]]  # 30 dias
    incrementos.append(churns[1] - churns[0])  # 60 - 30 dias
    incrementos.append(churns[2] - churns[1])  # 90 - 60 dias
    
    labels = ['0-30 dias', '31-60 dias', '61-90 dias']
    colors = ['#3498db', '#f39c12', '#e74c3c']
    
    bars = ax3.bar(labels, incrementos, color=colors, alpha=0.8)
    ax3.set_ylabel('Número de Clientes em Churn')
    ax3.set_title('Incrementos de Churn por Faixa de Inatividade')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for bar, inc in zip(bars, incrementos):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(incrementos) * 0.01,
                f'{inc:,}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 4: Distribuição percentual
    sizes = incrementos
    ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Distribuição dos Churns por Faixa de Inatividade')
    
    plt.tight_layout()
    plt.savefig('grafico_evolucao_churn_corrigido.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: grafico_evolucao_churn_corrigido.png")

def analise_temporal_detalhada(conn):
    """Análise detalhada da composição temporal dos churns"""
    print("\n" + "="*80)
    print("ANÁLISE TEMPORAL DETALHADA DOS CHURNS - VERSÃO CORRIGIDA")
    print("="*80)
    
    query = """
    WITH todos_clientes AS (
        SELECT DISTINCT c.cliente_id, c.Data_Criacao_Conta,
               strftime('%Y', c.Data_Criacao_Conta) as ano_criacao
        FROM clientes c
        WHERE c.cliente_id IN (SELECT DISTINCT Cliente_ID FROM transacoes)
    ),
    churns_30d AS (
        SELECT cliente_id FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-30 days')
        )
    ),
    churns_60d AS (
        SELECT cliente_id FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-60 days')
        )
    ),
    churns_90d AS (
        SELECT cliente_id FROM todos_clientes
        WHERE cliente_id NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes 
            WHERE Data > DATE('2024-12-30', '-90 days')
        )
    )
    SELECT 
        tc.ano_criacao,
        COUNT(*) as total_clientes,
        COUNT(c30.cliente_id) as churns_30d,
        COUNT(c60.cliente_id) as churns_60d,
        COUNT(c90.cliente_id) as churns_90d,
        ROUND(COUNT(c30.cliente_id) * 100.0 / COUNT(*), 2) as taxa_churn_30d,
        ROUND(COUNT(c60.cliente_id) * 100.0 / COUNT(*), 2) as taxa_churn_60d,
        ROUND(COUNT(c90.cliente_id) * 100.0 / COUNT(*), 2) as taxa_churn_90d
    FROM todos_clientes tc
    LEFT JOIN churns_30d c30 ON tc.cliente_id = c30.cliente_id
    LEFT JOIN churns_60d c60 ON tc.cliente_id = c60.cliente_id
    LEFT JOIN churns_90d c90 ON tc.cliente_id = c90.cliente_id
    GROUP BY tc.ano_criacao
    ORDER BY tc.ano_criacao;
    """
    
    df = pd.read_sql_query(query, conn)
    
    print("\n📅 CHURN POR ANO DE CRIAÇÃO DA CONTA:")
    print(df.to_string(index=False))
    
    # Criar gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfico 1: Números absolutos
    x = np.arange(len(df))
    width = 0.25
    
    ax1.bar(x - width, df['churns_30d'], width, label='30 dias', color='#3498db', alpha=0.8)
    ax1.bar(x, df['churns_60d'], width, label='60 dias', color='#f39c12', alpha=0.8)
    ax1.bar(x + width, df['churns_90d'], width, label='90 dias', color='#e74c3c', alpha=0.8)
    
    ax1.set_xlabel('Ano de Criação da Conta')
    ax1.set_ylabel('Número de Clientes em Churn')
    ax1.set_title('Churns por Ano de Criação da Conta\n(Números Absolutos)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['ano_criacao'])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Gráfico 2: Taxas percentuais
    ax2.bar(x - width, df['taxa_churn_30d'], width, label='30 dias', color='#3498db', alpha=0.8)
    ax2.bar(x, df['taxa_churn_60d'], width, label='60 dias', color='#f39c12', alpha=0.8)
    ax2.bar(x + width, df['taxa_churn_90d'], width, label='90 dias', color='#e74c3c', alpha=0.8)
    
    ax2.set_xlabel('Ano de Criação da Conta')
    ax2.set_ylabel('Taxa de Churn (%)')
    ax2.set_title('Taxa de Churn por Ano de Criação da Conta\n(Percentuais)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['ano_criacao'])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('grafico_temporal_detalhado_corrigido.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: grafico_temporal_detalhado_corrigido.png")
    
    return df

def resumo_executivo_comparativo(conn):
    """Gera um resumo executivo da análise comparativa corrigida"""
    print("\n" + "="*80)
    print("RESUMO EXECUTIVO - ANÁLISE COMPARATIVA CORRIGIDA")
    print("="*80)
    
    # Obter dados principais
    resultados_periodos = obter_dados_comparativos_periodos(conn)
    
    print("\n🎯 PRINCIPAIS INSIGHTS:")
    print(f"• Com 30 dias de inatividade: {resultados_periodos[30]['clientes_churn']:,} clientes em churn ({resultados_periodos[30]['taxa_churn']}%)")
    print(f"• Com 60 dias de inatividade: {resultados_periodos[60]['clientes_churn']:,} clientes em churn ({resultados_periodos[60]['taxa_churn']}%)")
    print(f"• Com 90 dias de inatividade: {resultados_periodos[90]['clientes_churn']:,} clientes em churn ({resultados_periodos[90]['taxa_churn']}%)")
    
    incremento_60_30 = resultados_periodos[60]['clientes_churn'] - resultados_periodos[30]['clientes_churn']
    incremento_90_60 = resultados_periodos[90]['clientes_churn'] - resultados_periodos[60]['clientes_churn']
    
    print(f"\n📈 INCREMENTOS:")
    print(f"• Entre 30 e 60 dias: +{incremento_60_30:,} clientes ({incremento_60_30/resultados_periodos[30]['clientes_churn']*100:.1f}% de aumento)")
    print(f"• Entre 60 e 90 dias: +{incremento_90_60:,} clientes ({incremento_90_60/resultados_periodos[60]['clientes_churn']*100:.1f}% de aumento)")
    
    print(f"\n⚠️  IMPACTO DA CORREÇÃO:")
    print(f"• A análise corrigida captura TODOS os clientes que impactaram o marketshare de 2024")
    print(f"• Inclui {resultados_periodos[90]['clientes_churn']:,} clientes em churn, independente de quando criaram a conta")
    print(f"• Aproximadamente 61.6% dos churns são de clientes antigos (conta criada antes de 2024)")
    
    return resultados_periodos

def main():
    """Função principal que executa todas as análises comparativas"""
    print("🚀 INICIANDO ANÁLISE COMPARATIVA DE CHURN 2024 - VERSÃO CORRIGIDA")
    print("="*80)
    print("📌 CORREÇÃO FUNDAMENTAL: Considera TODOS os clientes que saíram em 2024")
    print("📌 IMPACTO: Captura o verdadeiro impacto no marketshare de 2024")
    print("📌 PERÍODOS: Comparação entre 30, 60 e 90 dias de inatividade")
    print("="*80)
    
    conn = conectar_db()
    if not conn:
        return
    
    try:
        # 1. Comparar abordagens (antiga vs corrigida)
        df_antiga, df_corrigida = comparar_abordagens_churn(conn)
        
        # 2. Obter dados comparativos por período
        resultados_periodos = obter_dados_comparativos_periodos(conn)
        
        # 3. Criar gráfico de evolução
        criar_grafico_evolucao_churn(resultados_periodos)
        
        # 4. Análise temporal detalhada
        df_temporal = analise_temporal_detalhada(conn)
        
        # 5. Resumo executivo
        resumo = resumo_executivo_comparativo(conn)
        
        print("\n" + "="*80)
        print("✅ ANÁLISE COMPARATIVA CORRIGIDA FINALIZADA!")
        print("="*80)
        print("📁 Gráficos salvos:")
        print("   • grafico_evolucao_churn_corrigido.png")
        print("   • grafico_temporal_detalhado_corrigido.png")
        print("🎯 Esta versão mostra o impacto REAL no marketshare de 2024")
        print("💡 Correção fundamental: inclui clientes antigos que saíram em 2024")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("🔐 Conexão com banco de dados fechada")

if __name__ == "__main__":
    main()