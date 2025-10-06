#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Análise de Persona dos Clientes - Priceless Bank
===============================================

Objetivo: Identificar o perfil dos clientes através de análises gráficas
Dimensões: Idade, Renda, Limite de Cartão, Tipo de Cartão

Foco: Clientes ativos que fazem transações
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
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
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

def obter_dados_personas(conn):
    """Obtém dados dos clientes ativos para análise de personas"""
    
    query = """
    WITH clientes_ativos AS (
        SELECT DISTINCT Cliente_ID
        FROM transacoes
    ),
    dados_completos AS (
        SELECT DISTINCT
            c.Cliente_ID,
            c.Idade,
            c.Renda_Anual,
            cart.Tipo_Cartao,
            cart.Limite_Cartao,
            cart.Produto_Mastercard,
            -- Métricas de comportamento
            COUNT(DISTINCT t.ID_Transacao) as total_transacoes,
            ROUND(AVG(t.Valor_Compra), 2) as ticket_medio,
            ROUND(SUM(t.Valor_Compra), 2) as valor_total_gasto,
            MIN(t.Data) as primeira_transacao,
            MAX(t.Data) as ultima_transacao
        FROM clientes c
        INNER JOIN clientes_ativos ca ON c.Cliente_ID = ca.Cliente_ID
        LEFT JOIN transacoes t ON c.Cliente_ID = t.Cliente_ID
        LEFT JOIN cartoes cart ON t.ID_Cartao = cart.ID_Cartao
        GROUP BY c.Cliente_ID, c.Idade, c.Renda_Anual, cart.Tipo_Cartao, cart.Limite_Cartao, cart.Produto_Mastercard
    )
    SELECT * FROM dados_completos
    WHERE total_transacoes > 0
    ORDER BY valor_total_gasto DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"📊 Dados obtidos: {len(df)} clientes ativos")
    return df

def criar_faixas_categoricas(df):
    """Cria faixas categóricas para melhor análise"""
    
    # Faixas etárias
    df['faixa_etaria'] = pd.cut(df['Idade'], 
                               bins=[0, 25, 35, 45, 55, 100],
                               labels=['18-25', '26-35', '36-45', '46-55', '55+'])
    
    # Faixas de renda anual
    df['faixa_renda'] = pd.cut(df['Renda_Anual'],
                              bins=[0, 50000, 80000, 120000, float('inf')],
                              labels=['Até R$ 50k', 'R$ 50k-80k', 'R$ 80k-120k', 'Acima R$ 120k'])
    
    # Faixas de limite
    df['faixa_limite'] = pd.cut(df['Limite_Cartao'],
                               bins=[0, 1000, 5000, 10000, float('inf')],
                               labels=['Até R$ 1k', 'R$ 1k-5k', 'R$ 5k-10k', 'Acima R$ 10k'])
    
    # Perfil de gasto
    df['perfil_gasto'] = pd.cut(df['valor_total_gasto'],
                               bins=[0, 10000, 50000, 100000, float('inf')],
                               labels=['Baixo (<R$ 10k)', 'Médio (R$ 10k-50k)', 
                                      'Alto (R$ 50k-100k)', 'Premium (>R$ 100k)'])
    
    return df

def grafico_1_distribuicao_idade_renda(df):
    """Gráfico 1: Distribuição por Idade vs Renda"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('PERSONA DOS CLIENTES: Distribuição por Idade e Renda', fontsize=18, fontweight='bold', y=0.98)
    
    # Gráfico 1.1: Distribuição por faixa etária
    faixa_counts = df['faixa_etaria'].value_counts()
    colors1 = sns.color_palette("viridis", len(faixa_counts))
    
    bars1 = ax1.bar(faixa_counts.index, faixa_counts.values, color=colors1, alpha=0.8)
    ax1.set_title('Distribuição por Faixa Etária', fontweight='bold', pad=20)
    ax1.set_xlabel('Faixa Etária', fontweight='bold')
    ax1.set_ylabel('Número de Clientes', fontweight='bold')
    
    # Adicionar valores nas barras
    for bar, value in zip(bars1, faixa_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value}\n({value/len(df)*100:.1f}%)', 
                ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 1.2: Distribuição por faixa de renda
    renda_counts = df['faixa_renda'].value_counts()
    colors2 = sns.color_palette("plasma", len(renda_counts))
    
    bars2 = ax2.bar(renda_counts.index, renda_counts.values, color=colors2, alpha=0.8)
    ax2.set_title('Distribuição por Faixa de Renda', fontweight='bold', pad=20)
    ax2.set_xlabel('Faixa de Renda Anual', fontweight='bold')
    ax2.set_ylabel('Número de Clientes', fontweight='bold')
    
    for bar, value in zip(bars2, renda_counts.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value}\n({value/len(df)*100:.1f}%)', 
                ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 1.3: Scatter plot Idade vs Renda
    scatter = ax3.scatter(df['Idade'], df['Renda_Anual'], 
                         c=df['valor_total_gasto'], cmap='coolwarm', 
                         alpha=0.6, s=50)
    ax3.set_title('Relação Idade vs Renda (cor = valor gasto)', fontweight='bold', pad=20)
    ax3.set_xlabel('Idade', fontweight='bold')
    ax3.set_ylabel('Renda Anual (R$)', fontweight='bold')
    
    # Adicionar colorbar
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Valor Total Gasto (R$)', fontweight='bold')
    
    # Gráfico 1.4: Boxplot Renda por Faixa Etária
    df_clean = df.dropna(subset=['faixa_etaria', 'Renda_Anual'])
    box_plot = ax4.boxplot([group['Renda_Anual'].values for name, group in df_clean.groupby('faixa_etaria')],
                          labels=df_clean['faixa_etaria'].cat.categories,
                          patch_artist=True)
    
    # Colorir os boxplots
    colors4 = sns.color_palette("Set2", len(box_plot['boxes']))
    for patch, color in zip(box_plot['boxes'], colors4):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax4.set_title('Distribuição de Renda por Faixa Etária', fontweight='bold', pad=20)
    ax4.set_xlabel('Faixa Etária', fontweight='bold')
    ax4.set_ylabel('Renda Anual (R$)', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('persona_1_idade_renda.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: persona_1_idade_renda.png")

def grafico_2_cartoes_limites(df):
    """Gráfico 2: Análise de Cartões e Limites"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('PERSONA DOS CLIENTES: Cartões e Limites de Crédito', fontsize=18, fontweight='bold', y=0.98)
    
    # Gráfico 2.1: Distribuição por tipo de cartão
    tipo_counts = df['Tipo_Cartao'].value_counts()
    colors1 = sns.color_palette("Set1", len(tipo_counts))
    
    wedges, texts, autotexts = ax1.pie(tipo_counts.values, labels=tipo_counts.index, 
                                      colors=colors1, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Distribuição por Tipo de Cartão', fontweight='bold', pad=20)
    
    # Melhorar aparência do pie chart
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Gráfico 2.2: Distribuição por produto Mastercard
    produto_counts = df['Produto_Mastercard'].value_counts()
    colors2 = sns.color_palette("Set3", len(produto_counts))
    
    bars2 = ax2.bar(range(len(produto_counts)), produto_counts.values, color=colors2, alpha=0.8)
    ax2.set_title('Distribuição por Produto Mastercard', fontweight='bold', pad=20)
    ax2.set_xlabel('Produto Mastercard', fontweight='bold')
    ax2.set_ylabel('Número de Clientes', fontweight='bold')
    ax2.set_xticks(range(len(produto_counts)))
    ax2.set_xticklabels(produto_counts.index, rotation=45, ha='right')
    
    for bar, value in zip(bars2, produto_counts.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 2.3: Distribuição de limites
    limite_counts = df['faixa_limite'].value_counts()
    colors3 = sns.color_palette("viridis", len(limite_counts))
    
    bars3 = ax3.bar(limite_counts.index, limite_counts.values, color=colors3, alpha=0.8)
    ax3.set_title('Distribuição por Faixa de Limite', fontweight='bold', pad=20)
    ax3.set_xlabel('Faixa de Limite', fontweight='bold')
    ax3.set_ylabel('Número de Clientes', fontweight='bold')
    
    for bar, value in zip(bars3, limite_counts.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value}\n({value/len(df)*100:.1f}%)', 
                ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 2.4: Relação Limite vs Renda
    scatter2 = ax4.scatter(df['Renda_Anual'], df['Limite_Cartao'], 
                          c=df['Idade'], cmap='coolwarm', alpha=0.6, s=50)
    ax4.set_title('Relação Renda vs Limite (cor = idade)', fontweight='bold', pad=20)
    ax4.set_xlabel('Renda Anual (R$)', fontweight='bold')
    ax4.set_ylabel('Limite do Cartão (R$)', fontweight='bold')
    
    # Adicionar colorbar
    cbar2 = plt.colorbar(scatter2, ax=ax4)
    cbar2.set_label('Idade', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('persona_2_cartoes_limites.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: persona_2_cartoes_limites.png")

def grafico_3_comportamento_gastos(df):
    """Gráfico 3: Comportamento de Gastos"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('PERSONA DOS CLIENTES: Comportamento de Gastos', fontsize=18, fontweight='bold', y=0.98)
    
    # Gráfico 3.1: Distribuição do perfil de gasto
    gasto_counts = df['perfil_gasto'].value_counts()
    colors1 = sns.color_palette("Spectral", len(gasto_counts))
    
    bars1 = ax1.bar(gasto_counts.index, gasto_counts.values, color=colors1, alpha=0.8)
    ax1.set_title('Distribuição por Perfil de Gasto', fontweight='bold', pad=20)
    ax1.set_xlabel('Perfil de Gasto', fontweight='bold')
    ax1.set_ylabel('Número de Clientes', fontweight='bold')
    
    for bar, value in zip(bars1, gasto_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value}\n({value/len(df)*100:.1f}%)', 
                ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 3.2: Ticket médio por faixa etária
    ticket_por_idade = df.groupby('faixa_etaria')['ticket_medio'].mean().sort_values(ascending=False)
    colors2 = sns.color_palette("coolwarm", len(ticket_por_idade))
    
    bars2 = ax2.bar(ticket_por_idade.index, ticket_por_idade.values, color=colors2, alpha=0.8)
    ax2.set_title('Ticket Médio por Faixa Etária', fontweight='bold', pad=20)
    ax2.set_xlabel('Faixa Etária', fontweight='bold')
    ax2.set_ylabel('Ticket Médio (R$)', fontweight='bold')
    
    for bar, value in zip(bars2, ticket_por_idade.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'R$ {value:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 3.3: Número de transações por faixa de renda
    trans_por_renda = df.groupby('faixa_renda')['total_transacoes'].mean().sort_values(ascending=False)
    colors3 = sns.color_palette("plasma", len(trans_por_renda))
    
    bars3 = ax3.bar(trans_por_renda.index, trans_por_renda.values, color=colors3, alpha=0.8)
    ax3.set_title('Média de Transações por Faixa de Renda', fontweight='bold', pad=20)
    ax3.set_xlabel('Faixa de Renda', fontweight='bold')
    ax3.set_ylabel('Média de Transações', fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    
    for bar, value in zip(bars3, trans_por_renda.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Gráfico 3.4: Heatmap correlação entre variáveis numéricas
    numeric_cols = ['Idade', 'Renda_Anual', 'Limite_Cartao', 'total_transacoes', 'ticket_medio', 'valor_total_gasto']
    correlation_matrix = df[numeric_cols].corr()
    
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, ax=ax4, cbar_kws={'shrink': 0.8})
    ax4.set_title('Correlação entre Variáveis', fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('persona_3_comportamento_gastos.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: persona_3_comportamento_gastos.png")

def grafico_4_segmentacao_personas(df):
    """Gráfico 4: Segmentação e Identificação de Personas"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('IDENTIFICAÇÃO DE PERSONAS: Segmentação dos Clientes', fontsize=18, fontweight='bold', y=0.98)
    
    # Gráfico 4.1: Segmentação por Renda vs Idade (com tamanho = valor gasto)
    scatter1 = ax1.scatter(df['Idade'], df['Renda_Anual'], 
                          s=df['valor_total_gasto']/1000,  # Tamanho proporcional ao gasto
                          c=df['total_transacoes'], cmap='viridis', alpha=0.6)
    ax1.set_title('Segmentação: Idade vs Renda\n(tamanho = valor gasto, cor = frequência)', fontweight='bold', pad=20)
    ax1.set_xlabel('Idade', fontweight='bold')
    ax1.set_ylabel('Renda Anual (R$)', fontweight='bold')
    
    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label('Total de Transações', fontweight='bold')
    
    # Gráfico 4.2: Top 10 combinações Produto + Tipo de Cartão
    df['produto_tipo'] = df['Produto_Mastercard'] + ' - ' + df['Tipo_Cartao']
    top_combos = df['produto_tipo'].value_counts().head(10)
    
    colors2 = sns.color_palette("Set2", len(top_combos))
    bars2 = ax2.barh(range(len(top_combos)), top_combos.values, color=colors2, alpha=0.8)
    ax2.set_title('Top 10 Combinações Produto + Tipo', fontweight='bold', pad=20)
    ax2.set_xlabel('Número de Clientes', fontweight='bold')
    ax2.set_yticks(range(len(top_combos)))
    ax2.set_yticklabels(top_combos.index, fontsize=10)
    
    for i, (bar, value) in enumerate(zip(bars2, top_combos.values)):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'{value}', ha='left', va='center', fontweight='bold')
    
    # Gráfico 4.3: Distribuição de gastos por combinação Idade + Renda
    df['idade_renda'] = df['faixa_etaria'].astype(str) + ' | ' + df['faixa_renda'].astype(str)
    gasto_por_segmento = df.groupby('idade_renda')['valor_total_gasto'].mean().sort_values(ascending=True)
    
    colors3 = sns.color_palette("coolwarm", len(gasto_por_segmento))
    bars3 = ax3.barh(range(len(gasto_por_segmento)), gasto_por_segmento.values, color=colors3, alpha=0.8)
    ax3.set_title('Valor Médio Gasto por Segmento\n(Idade + Renda)', fontweight='bold', pad=20)
    ax3.set_xlabel('Valor Médio Gasto (R$)', fontweight='bold')
    ax3.set_yticks(range(len(gasto_por_segmento)))
    ax3.set_yticklabels(gasto_por_segmento.index, fontsize=9)
    
    for i, (bar, value) in enumerate(zip(bars3, gasto_por_segmento.values)):
        ax3.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
                f'R$ {value:.0f}', ha='left', va='center', fontweight='bold', fontsize=9)
    
    # Gráfico 4.4: Mapa de calor - Produtos por Faixa Etária
    produto_idade_pivot = pd.crosstab(df['Produto_Mastercard'], df['faixa_etaria'])
    
    sns.heatmap(produto_idade_pivot, annot=True, cmap='YlOrRd', fmt='d',
                square=False, ax=ax4, cbar_kws={'shrink': 0.8})
    ax4.set_title('Produtos por Faixa Etária', fontweight='bold', pad=20)
    ax4.set_xlabel('Faixa Etária', fontweight='bold')
    ax4.set_ylabel('Produto Mastercard', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('persona_4_segmentacao.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print("📊 Gráfico salvo: persona_4_segmentacao.png")

def gerar_relatorio_personas(df):
    """Gera relatório final com as personas identificadas"""
    
    print("\n" + "="*100)
    print("RELATÓRIO FINAL: PERSONAS DOS CLIENTES PRICELESS BANK")
    print("="*100)
    
    # Estatísticas gerais
    print(f"\n📊 PANORAMA GERAL:")
    print(f"   • Total de clientes ativos analisados: {len(df):,}")
    print(f"   • Idade média: {df['Idade'].mean():.1f} anos")
    print(f"   • Renda média anual: R$ {df['Renda_Anual'].mean():,.0f}")
    print(f"   • Limite médio: R$ {df['Limite_Cartao'].mean():,.0f}")
    print(f"   • Ticket médio: R$ {df['ticket_medio'].mean():.2f}")
    
    # Top personas por faixa etária
    print(f"\n🎯 PERSONAS IDENTIFICADAS POR FAIXA ETÁRIA:")
    for faixa in df['faixa_etaria'].cat.categories:
        subset = df[df['faixa_etaria'] == faixa]
        if len(subset) > 0:
            print(f"\n   👥 {faixa} anos ({len(subset)} clientes - {len(subset)/len(df)*100:.1f}%):")
            print(f"      • Renda média: R$ {subset['Renda_Anual'].mean():,.0f}")
            print(f"      • Limite médio: R$ {subset['Limite_Cartao'].mean():,.0f}")
            print(f"      • Ticket médio: R$ {subset['ticket_medio'].mean():.2f}")
            print(f"      • Produto preferido: {subset['Produto_Mastercard'].mode().iloc[0] if not subset['Produto_Mastercard'].mode().empty else 'N/A'}")
            print(f"      • Tipo cartão preferido: {subset['Tipo_Cartao'].mode().iloc[0] if not subset['Tipo_Cartao'].mode().empty else 'N/A'}")
    
    # Top produtos
    print(f"\n💳 PRODUTOS MAIS POPULARES:")
    top_produtos = df['Produto_Mastercard'].value_counts().head(5)
    for i, (produto, count) in enumerate(top_produtos.items(), 1):
        print(f"   {i}. {produto}: {count} clientes ({count/len(df)*100:.1f}%)")
    
    # Correlações importantes
    print(f"\n🔗 CORRELAÇÕES IMPORTANTES:")
    correlations = df[['Idade', 'Renda_Anual', 'Limite_Cartao', 'ticket_medio', 'valor_total_gasto']].corr()
    
    print(f"   • Renda vs Limite: {correlations.loc['Renda_Anual', 'Limite_Cartao']:.3f}")
    print(f"   • Idade vs Ticket Médio: {correlations.loc['Idade', 'ticket_medio']:.3f}")
    print(f"   • Limite vs Valor Gasto: {correlations.loc['Limite_Cartao', 'valor_total_gasto']:.3f}")
    
    # Segmentos de alto valor
    high_value = df[df['valor_total_gasto'] > df['valor_total_gasto'].quantile(0.8)]
    print(f"\n💎 CLIENTES DE ALTO VALOR (Top 20%):")
    print(f"   • Quantidade: {len(high_value)} clientes")
    print(f"   • Idade média: {high_value['Idade'].mean():.1f} anos")
    print(f"   • Renda média: R$ {high_value['Renda_Anual'].mean():,.0f}")
    print(f"   • Gasto médio: R$ {high_value['valor_total_gasto'].mean():,.0f}")
    print(f"   • Faixa etária predominante: {high_value['faixa_etaria'].mode().iloc[0] if not high_value['faixa_etaria'].mode().empty else 'N/A'}")
    
    print(f"\n✅ ANÁLISE DE PERSONAS CONCLUÍDA!")
    print(f"📁 Arquivos gerados:")
    print(f"   • persona_1_idade_renda.png")
    print(f"   • persona_2_cartoes_limites.png")
    print(f"   • persona_3_comportamento_gastos.png")
    print(f"   • persona_4_segmentacao.png")

def main():
    """Função principal"""
    print("🚀 INICIANDO ANÁLISE DE PERSONAS DOS CLIENTES")
    print("="*60)
    
    conn = conectar_db()
    if not conn:
        return
    
    try:
        # Obter dados
        df = obter_dados_personas(conn)
        
        # Criar faixas categóricas
        df = criar_faixas_categoricas(df)
        
        # Gerar gráficos
        grafico_1_distribuicao_idade_renda(df)
        grafico_2_cartoes_limites(df)
        grafico_3_comportamento_gastos(df)
        grafico_4_segmentacao_personas(df)
        
        # Gerar relatório final
        gerar_relatorio_personas(df)
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("\n🔐 Conexão com banco de dados fechada")

if __name__ == "__main__":
    main()