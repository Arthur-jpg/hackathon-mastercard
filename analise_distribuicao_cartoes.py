#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Análise de Distribuição de Tipos de Cartões - Priceless Bank
===========================================================

Objetivo: Criar gráfico da distribuição de tipos de cartões
Dados: Cruzamento entre clientes, cartões e transações
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
plt.rcParams['font.size'] = 14
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
sns.set_style("whitegrid")
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

def obter_distribuicao_cartoes(conn):
    """Obtém a distribuição absoluta de cartões (não clientes únicos)"""
    
    query = """
    WITH cartoes_em_uso AS (
        SELECT DISTINCT 
            c.ID_Cartao,
            c.Tipo_Cartao,
            c.Limite_Cartao,
            c.Produto_Mastercard,
            t.Cliente_ID
        FROM cartoes c
        INNER JOIN transacoes t ON c.ID_Cartao = t.ID_Cartao
    ),
    total_cartoes_ativos AS (
        SELECT COUNT(*) as total FROM cartoes_em_uso
    ),
    clientes_sem_cartao AS (
        SELECT COUNT(*) as quantidade
        FROM clientes 
        WHERE Cliente_ID NOT IN (
            SELECT DISTINCT Cliente_ID FROM transacoes
        )
    )
    SELECT 
        Tipo_Cartao as tipo_cartao,
        COUNT(*) as quantidade_cartoes,
        ROUND(COUNT(*) * 100.0 / (
            (SELECT total FROM total_cartoes_ativos) + 
            (SELECT quantidade FROM clientes_sem_cartao)
        ), 2) as percentual
    FROM cartoes_em_uso
    GROUP BY Tipo_Cartao
    
    UNION ALL
    
    SELECT 
        'Sem Cartão Ativo' as tipo_cartao,
        (SELECT quantidade FROM clientes_sem_cartao) as quantidade_cartoes,
        ROUND((SELECT quantidade FROM clientes_sem_cartao) * 100.0 / (
            (SELECT total FROM total_cartoes_ativos) + 
            (SELECT quantidade FROM clientes_sem_cartao)
        ), 2) as percentual
    
    ORDER BY quantidade_cartoes DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"📊 Distribuição de cartões (números absolutos):")
    print(df.to_string(index=False))
    
    # Consulta adicional para mostrar clientes vs cartões
    query_comparacao = """
    SELECT 
        'Total de clientes cadastrados' as metrica,
        COUNT(*) as quantidade
    FROM clientes
    
    UNION ALL
    
    SELECT 
        'Clientes com cartão ativo' as metrica,
        COUNT(DISTINCT Cliente_ID) as quantidade
    FROM transacoes
    
    UNION ALL
    
    SELECT 
        'Total de cartões em uso' as metrica,
        COUNT(DISTINCT c.ID_Cartao) as quantidade
    FROM cartoes c
    INNER JOIN transacoes t ON c.ID_Cartao = t.ID_Cartao
    
    UNION ALL
    
    SELECT 
        'Clientes sem cartão ativo' as metrica,
        COUNT(*) as quantidade
    FROM clientes 
    WHERE Cliente_ID NOT IN (SELECT DISTINCT Cliente_ID FROM transacoes);
    """
    
    df_comparacao = pd.read_sql_query(query_comparacao, conn)
    print(f"\n📈 Comparação Clientes vs Cartões:")
    print(df_comparacao.to_string(index=False))
    
    return df

def obter_detalhes_cartoes(conn):
    """Obtém detalhes adicionais sobre os cartões ativos (números absolutos)"""
    
    query = """
    WITH cartoes_em_uso AS (
        SELECT DISTINCT 
            c.ID_Cartao,
            c.Tipo_Cartao,
            c.Limite_Cartao,
            c.Produto_Mastercard,
            t.Cliente_ID,
            COUNT(DISTINCT t.ID_Transacao) as total_transacoes,
            ROUND(AVG(t.Valor_Compra), 2) as ticket_medio
        FROM cartoes c
        INNER JOIN transacoes t ON c.ID_Cartao = t.ID_Cartao
        GROUP BY c.ID_Cartao, c.Tipo_Cartao, c.Limite_Cartao, c.Produto_Mastercard, t.Cliente_ID
    )
    SELECT 
        Tipo_Cartao,
        Produto_Mastercard,
        COUNT(*) as quantidade_cartoes,
        ROUND(AVG(Limite_Cartao), 0) as limite_medio,
        ROUND(AVG(total_transacoes), 1) as transacoes_medias,
        ROUND(AVG(ticket_medio), 2) as ticket_medio_geral
    FROM cartoes_em_uso
    GROUP BY Tipo_Cartao, Produto_Mastercard
    ORDER BY Tipo_Cartao, quantidade_cartoes DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    return df

def criar_grafico_distribuicao_cartoes(df_distribuicao, df_detalhes):
    """Cria gráfico completo da distribuição de cartões"""
    
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('DISTRIBUIÇÃO DE TIPOS DE CARTÕES - PRICELESS BANK\nAnálise Completa da Base de Clientes', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Gráfico 1: Pizza - Distribuição Geral
    ax1 = plt.subplot(2, 3, 1)
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    wedges, texts, autotexts = ax1.pie(df_distribuicao['quantidade_cartoes'], 
                                      labels=df_distribuicao['tipo_cartao'],
                                      colors=colors[:len(df_distribuicao)],
                                      autopct='%1.1f%%', 
                                      startangle=90,
                                      explode=[0.1 if 'Sem Cartão' in x else 0 for x in df_distribuicao['tipo_cartao']])
    
    ax1.set_title('Distribuição por Tipo de Cartão', fontweight='bold', pad=20, fontsize=16)
    
    # Melhorar aparência do pie chart
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    # Gráfico 2: Barras - Quantidade absoluta de cartões
    ax2 = plt.subplot(2, 3, 2)
    
    bars = ax2.bar(df_distribuicao['tipo_cartao'], df_distribuicao['quantidade_cartoes'], 
                   color=colors[:len(df_distribuicao)], alpha=0.8)
    
    ax2.set_title('Quantidade Absoluta de Cartões', fontweight='bold', pad=20, fontsize=16)
    ax2.set_xlabel('Tipo de Cartão', fontweight='bold')
    ax2.set_ylabel('Número de Cartões', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, df_distribuicao['quantidade_cartoes']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Gráfico 3: Barras Horizontais - Percentuais
    ax3 = plt.subplot(2, 3, 3)
    
    y_pos = np.arange(len(df_distribuicao))
    bars_h = ax3.barh(y_pos, df_distribuicao['percentual'], 
                      color=colors[:len(df_distribuicao)], alpha=0.8)
    
    ax3.set_title('Participação Percentual', fontweight='bold', pad=20, fontsize=16)
    ax3.set_xlabel('Percentual (%)', fontweight='bold')
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(df_distribuicao['tipo_cartao'])
    
    # Adicionar valores nas barras
    for i, (bar, value) in enumerate(zip(bars_h, df_distribuicao['percentual'])):
        ax3.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{value}%', ha='left', va='center', fontweight='bold', fontsize=12)
    
    # Gráfico 4: Análise detalhada dos cartões ativos (apenas Crédito e Débito)
    ax4 = plt.subplot(2, 3, 4)
    
    # Filtrar apenas cartões ativos
    df_ativos = df_detalhes[df_detalhes['Tipo_Cartao'].isin(['Crédito', 'Débito'])]
    
    if not df_ativos.empty:
        limite_por_tipo = df_ativos.groupby('Tipo_Cartao')['limite_medio'].mean()
        
        bars4 = ax4.bar(limite_por_tipo.index, limite_por_tipo.values, 
                       color=['#3498db', '#2ecc71'], alpha=0.8)
        
        ax4.set_title('Limite Médio por Tipo de Cartão', fontweight='bold', pad=20, fontsize=16)
        ax4.set_xlabel('Tipo de Cartão', fontweight='bold')
        ax4.set_ylabel('Limite Médio (R$)', fontweight='bold')
        
        # Adicionar valores nas barras
        for bar, value in zip(bars4, limite_por_tipo.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                    f'R$ {value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Gráfico 5: Produtos Mastercard por tipo de cartão
    ax5 = plt.subplot(2, 3, 5)
    
    if not df_detalhes.empty:
        # Criar tabela cruzada
        produto_tipo = df_detalhes.pivot_table(values='quantidade_cartoes', 
                                              index='Produto_Mastercard', 
                                              columns='Tipo_Cartao', 
                                              fill_value=0)
        
        # Criar heatmap
        sns.heatmap(produto_tipo, annot=True, cmap='YlOrRd', fmt='.0f',
                   square=False, ax=ax5, cbar_kws={'shrink': 0.8})
        ax5.set_title('Produtos por Tipo de Cartão', fontweight='bold', pad=20, fontsize=16)
        ax5.set_xlabel('Tipo de Cartão', fontweight='bold')
        ax5.set_ylabel('Produto Mastercard', fontweight='bold')
    
    # Gráfico 6: Resumo executivo em texto
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    # Calcular estatísticas para o resumo
    total_cartoes = df_distribuicao['quantidade_cartoes'].sum()
    sem_cartao = df_distribuicao[df_distribuicao['tipo_cartao'] == 'Sem Cartão Ativo']['quantidade_cartoes'].iloc[0] if 'Sem Cartão Ativo' in df_distribuicao['tipo_cartao'].values else 0
    credito = df_distribuicao[df_distribuicao['tipo_cartao'] == 'Crédito']['quantidade_cartoes'].iloc[0] if 'Crédito' in df_distribuicao['tipo_cartao'].values else 0
    debito = df_distribuicao[df_distribuicao['tipo_cartao'] == 'Débito']['quantidade_cartoes'].iloc[0] if 'Débito' in df_distribuicao['tipo_cartao'].values else 0
    
    resumo_texto = f"""
RESUMO EXECUTIVO

📊 Total de Cartões + Clientes sem cartão: {total_cartoes:,}

💳 DISTRIBUIÇÃO ABSOLUTA:
• Cartões Crédito: {credito} ({credito/total_cartoes*100:.1f}%)
• Cartões Débito: {debito} ({debito/total_cartoes*100:.1f}%)
• Clientes sem cartão: {sem_cartao} ({sem_cartao/total_cartoes*100:.1f}%)

🚨 INSIGHTS CRÍTICOS:
• {sem_cartao} clientes nunca ativaram
• Múltiplos cartões por cliente possível
• Oportunidade de ativação + cross-sell

🎯 RECOMENDAÇÕES:
• Campanha urgente de ativação
• Oferecer cartões adicionais
• Produtos complementares (crédito + débito)
    """
    
    ax6.text(0.05, 0.95, resumo_texto, transform=ax6.transAxes, 
            fontsize=12, verticalalignment='top', 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('distribuicao_tipos_cartoes.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: distribuicao_tipos_cartoes.png")

def gerar_relatorio_detalhado(df_distribuicao, df_detalhes):
    """Gera relatório detalhado da distribuição de cartões"""
    
    print("\n" + "="*80)
    print("RELATÓRIO DETALHADO: DISTRIBUIÇÃO DE TIPOS DE CARTÕES")
    print("="*80)
    
    total_cartoes = df_distribuicao['quantidade_cartoes'].sum()
    
    print(f"\n📊 PANORAMA GERAL:")
    print(f"   • Total de cartões + clientes sem cartão: {total_cartoes:,}")
    
    print(f"\n💳 DISTRIBUIÇÃO ABSOLUTA DE CARTÕES:")
    for _, row in df_distribuicao.iterrows():
        if row['tipo_cartao'] == 'Sem Cartão Ativo':
            print(f"   • {row['tipo_cartao']}: {row['quantidade_cartoes']} clientes ({row['percentual']}%)")
        else:
            print(f"   • Cartões {row['tipo_cartao']}: {row['quantidade_cartoes']} unidades ({row['percentual']}%)")
    
    if not df_detalhes.empty:
        print(f"\n📈 ANÁLISE DETALHADA DOS CARTÕES ATIVOS:")
        
        for tipo in df_detalhes['Tipo_Cartao'].unique():
            dados_tipo = df_detalhes[df_detalhes['Tipo_Cartao'] == tipo]
            total_tipo = dados_tipo['quantidade_cartoes'].sum()
            limite_medio = dados_tipo['limite_medio'].mean()
            
            print(f"\n   🔹 {tipo.upper()}:")
            print(f"      • Total de cartões: {total_tipo}")
            print(f"      • Limite médio: R$ {limite_medio:,.0f}")
            print(f"      • Produtos mais populares:")
            
            top_produtos = dados_tipo.nlargest(3, 'quantidade_cartoes')
            for _, produto in top_produtos.iterrows():
                print(f"        - {produto['Produto_Mastercard']}: {produto['quantidade_cartoes']} cartões")
    
    # Identificar oportunidades
    sem_cartao = df_distribuicao[df_distribuicao['tipo_cartao'] == 'Sem Cartão Ativo']['quantidade_cartoes'].iloc[0] if 'Sem Cartão Ativo' in df_distribuicao['tipo_cartao'].values else 0
    total_cartoes_ativos = df_distribuicao[df_distribuicao['tipo_cartao'] != 'Sem Cartão Ativo']['quantidade_cartoes'].sum()
    
    print(f"\n🎯 OPORTUNIDADES IDENTIFICADAS:")
    print(f"   • {sem_cartao} clientes sem cartão ativo representam oportunidade de:")
    print(f"     - Ativação imediata da base")
    print(f"     - Potencial receita adicional")
    print(f"     - Redução do churn por não-utilização")
    print(f"   • {total_cartoes_ativos} cartões ativos indicam potencial para cross-sell")
    
    print(f"\n💡 RECOMENDAÇÕES ESTRATÉGICAS:")
    print(f"   1. Campanha emergencial de ativação para {sem_cartao} clientes inativos")
    print(f"   2. Cross-sell: oferecer cartão débito para clientes só com crédito")
    print(f"   3. Produtos complementares para maximizar cartões por cliente")
    print(f"   4. Revisão do processo de onboarding e primeira utilização")
    
    print(f"\n✅ CONCLUSÃO:")
    print(f"Temos {total_cartoes_ativos} cartões ativos vs {sem_cartao} clientes inativos.")
    print(f"Oportunidade dupla: ativar + vender cartões adicionais.")

def main():
    """Função principal"""
    print("🚀 INICIANDO ANÁLISE DE DISTRIBUIÇÃO DE CARTÕES")
    print("="*60)
    
    conn = conectar_db()
    if not conn:
        return
    
    try:
        # Obter dados
        df_distribuicao = obter_distribuicao_cartoes(conn)
        df_detalhes = obter_detalhes_cartoes(conn)
        
        # Criar gráficos
        criar_grafico_distribuicao_cartoes(df_distribuicao, df_detalhes)
        
        # Gerar relatório
        gerar_relatorio_detalhado(df_distribuicao, df_detalhes)
        
        print(f"\n✅ ANÁLISE CONCLUÍDA!")
        print(f"📁 Arquivo gerado: distribuicao_tipos_cartoes.png")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("\n🔐 Conexão com banco de dados fechada")

if __name__ == "__main__":
    main()