#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANÁLISE COMPLETA DE CHURN POR FATORES INDIVIDUAIS
Análise detalhada da taxa de churn baseada em cada característica dos clientes
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

print("="*80)
print("🔍 ANÁLISE COMPLETA DE CHURN POR FATORES INDIVIDUAIS")
print("="*80)
print()

# =============================================================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# =============================================================================

print("📊 CARREGANDO BASES DE DADOS:")
print("-" * 30)

# Carregar dados
df_clientes = pd.read_csv('data/Base_clientes.csv')
df_transacoes = pd.read_csv('data/Base_transacoes.csv')
df_cartoes = pd.read_csv('data/Base_cartoes.csv')

print(f"✅ Clientes: {len(df_clientes):,} registros")
print(f"✅ Transações: {len(df_transacoes):,} registros")
print(f"✅ Cartões: {len(df_cartoes):,} registros")
print()

# =============================================================================
# IDENTIFICAÇÃO DE CHURN POR CLIENTE
# =============================================================================

print("🎯 IDENTIFICANDO CLIENTES COM CHURN:")
print("-" * 35)

# Converter datas
df_transacoes['Data'] = pd.to_datetime(df_transacoes['Data'])
df_clientes['Data_Nascimento'] = pd.to_datetime(df_clientes['Data_Nascimento'], format='%d/%m/%Y')
df_clientes['Data_Criacao_Conta'] = pd.to_datetime(df_clientes['Data_Criacao_Conta'])
df_cartoes['Data_Emissao'] = pd.to_datetime(df_cartoes['Data_Emissao'])

# Data de referência (assumindo que dados são até agora)
data_referencia = df_transacoes['Data'].max()
print(f"📅 Data de referência: {data_referencia.strftime('%Y-%m-%d')}")

# Última transação de cada cliente
ultima_transacao = df_transacoes.groupby('Cliente_ID')['Data'].max().reset_index()
ultima_transacao.columns = ['Cliente_ID', 'Ultima_Transacao']

# Definir churn: cliente sem transações nos últimos 90 dias
dias_churn = 90
data_limite_churn = data_referencia - timedelta(days=dias_churn)

ultima_transacao['Churn'] = ultima_transacao['Ultima_Transacao'] < data_limite_churn
ultima_transacao['Dias_Sem_Transacao'] = (data_referencia - ultima_transacao['Ultima_Transacao']).dt.days

print(f"🔍 Critério de churn: {dias_churn} dias sem transações")
print(f"📊 Data limite para churn: {data_limite_churn.strftime('%Y-%m-%d')}")

# Estatísticas de churn
total_clientes = len(ultima_transacao)
clientes_churn = ultima_transacao['Churn'].sum()
taxa_churn_geral = (clientes_churn / total_clientes) * 100

print(f"📈 RESULTADOS GERAIS:")
print(f"   • Total de clientes: {total_clientes:,}")
print(f"   • Clientes em churn: {clientes_churn:,}")
print(f"   • Taxa de churn geral: {taxa_churn_geral:.1f}%")
print()

# =============================================================================
# PREPARAÇÃO DOS DADOS PARA ANÁLISE
# =============================================================================

# Merge dos dados para análise completa
df_analise = df_clientes.copy()
df_analise = df_analise.merge(ultima_transacao[['Cliente_ID', 'Churn', 'Dias_Sem_Transacao']], 
                             on='Cliente_ID', how='left')

# Calcular idade (tratando possíveis NaN)
df_analise['Idade'] = ((data_referencia - df_analise['Data_Nascimento']).dt.days / 365.25)
df_analise['Idade'] = df_analise['Idade'].fillna(0).astype(int)

# Calcular tempo de conta em meses (tratando possíveis NaN)
df_analise['Tempo_Conta_Meses'] = ((data_referencia - df_analise['Data_Criacao_Conta']).dt.days / 30.44)
df_analise['Tempo_Conta_Meses'] = df_analise['Tempo_Conta_Meses'].fillna(0).astype(int)

# Preparar dados dos cartões (vamos pegar informações do cartão principal/mais recente)
cartoes_principais = df_cartoes.groupby('ID_Cartao').first().reset_index()

# Mapear cartões para clientes (vamos usar o primeiro cartão de cada cliente como referência)
# Primeiro, precisamos conectar cartões com clientes através das transações
cartao_cliente = df_transacoes[['Cliente_ID', 'ID_Cartao']].drop_duplicates()
cartao_info = cartao_cliente.merge(df_cartoes, on='ID_Cartao', how='left')

# Para cada cliente, pegar informações do cartão mais utilizado
cartao_por_cliente = cartao_info.groupby('Cliente_ID').first().reset_index()

# Merge com dados de cartões
df_analise = df_analise.merge(cartao_por_cliente[['Cliente_ID', 'Produto_Mastercard', 'Tipo_Cartao', 
                                                'Data_Emissao', 'Limite_Cartao']], 
                             on='Cliente_ID', how='left')

# Calcular tempo desde emissão do cartão (tratando NaN)
df_analise['Tempo_Cartao_Meses'] = ((data_referencia - df_analise['Data_Emissao']).dt.days / 30.44)
df_analise['Tempo_Cartao_Meses'] = df_analise['Tempo_Cartao_Meses'].fillna(-1).astype(int)

print("📊 DADOS PREPARADOS PARA ANÁLISE:")
print(f"   • Clientes com dados completos: {len(df_analise):,}")
print(f"   • Variáveis para análise: {df_analise.shape[1]}")
print()

# =============================================================================
# FUNÇÃO PARA ANÁLISE DE CHURN POR FATOR
# =============================================================================

def analisar_churn_por_fator(df, coluna, titulo, tipo_variavel='categorica', bins=None):
    """
    Análise de churn por fator específico
    """
    print(f"🔍 Analisando: {titulo}")
    print("-" * 50)
    
    # Remover valores nulos
    df_clean = df.dropna(subset=[coluna, 'Churn'])
    
    if tipo_variavel == 'numerica' and bins is not None:
        # Para variáveis numéricas, criar faixas
        df_clean[f'{coluna}_Faixa'] = pd.cut(df_clean[coluna], bins=bins, include_lowest=True)
        coluna_analise = f'{coluna}_Faixa'
    else:
        coluna_analise = coluna
    
    # Análise por grupo
    analise = df_clean.groupby(coluna_analise).agg({
        'Churn': ['count', 'sum'],
        'Cliente_ID': 'count'
    }).round(2)
    
    # Flatten columns
    analise.columns = ['Total_Clientes', 'Clientes_Churn', 'Total_Clientes_2']
    analise = analise.drop('Total_Clientes_2', axis=1)
    
    # Converter para numérico e calcular taxa de churn
    analise['Total_Clientes'] = pd.to_numeric(analise['Total_Clientes'], errors='coerce')
    analise['Clientes_Churn'] = pd.to_numeric(analise['Clientes_Churn'], errors='coerce')
    analise['Taxa_Churn'] = (analise['Clientes_Churn'] / analise['Total_Clientes'] * 100).round(1)
    
    # Calcular percentual do total
    analise['Pct_Base'] = (analise['Total_Clientes'] / analise['Total_Clientes'].sum() * 100).round(1)
    
    # Ordenar por taxa de churn (descendente)
    analise = analise.sort_values('Taxa_Churn', ascending=False)
    
    print("📊 RESULTADOS:")
    for idx, row in analise.head(10).iterrows():  # Top 10 para não poluir output
        print(f"   • {idx}: {row['Taxa_Churn']:.1f}% churn ({row['Clientes_Churn']:.0f}/{row['Total_Clientes']:.0f} clientes)")
    
    if len(analise) > 10:
        print(f"   ... (e mais {len(analise)-10} categorias)")
    
    print()
    
    return analise

# =============================================================================
# ANÁLISES POR FATOR INDIVIDUAL
# =============================================================================

print("="*80)
print("🎯 ANÁLISES DE CHURN POR FATOR INDIVIDUAL")
print("="*80)
print()

# Lista para armazenar resultados
resultados_analises = []

# 1. ANÁLISE POR IDADE
print("1️⃣ ANÁLISE POR IDADE")
faixas_idade = [0, 25, 35, 45, 55, 65, 100]
labels_idade = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
resultado_idade = analisar_churn_por_fator(df_analise, 'Idade', 'Faixa Etária', 
                                         'numerica', faixas_idade)
resultados_analises.append(('Idade', resultado_idade))

# 2. ANÁLISE POR RENDA ANUAL
print("2️⃣ ANÁLISE POR RENDA ANUAL")
faixas_renda = [0, 30000, 50000, 75000, 100000, 150000, 1000000]
resultado_renda = analisar_churn_por_fator(df_analise, 'Renda_Anual', 'Faixa de Renda', 
                                         'numerica', faixas_renda)
resultados_analises.append(('Renda_Anual', resultado_renda))

# 3. ANÁLISE POR TEMPO DE CONTA
print("3️⃣ ANÁLISE POR TEMPO DE CONTA")
faixas_tempo_conta = [0, 6, 12, 18, 24, 36, 1000]
resultado_tempo_conta = analisar_churn_por_fator(df_analise, 'Tempo_Conta_Meses', 'Tempo de Conta', 
                                               'numerica', faixas_tempo_conta)
resultados_analises.append(('Tempo_Conta', resultado_tempo_conta))

# 4. ANÁLISE POR CONTA ADICIONAL
print("4️⃣ ANÁLISE POR POSSUI CONTA ADICIONAL")
resultado_conta_adicional = analisar_churn_por_fator(df_analise, 'Possui_Conta_Adicional', 
                                                   'Conta Adicional', 'categorica')
resultados_analises.append(('Conta_Adicional', resultado_conta_adicional))

# 5. ANÁLISE POR ESTADO
print("5️⃣ ANÁLISE POR ESTADO")
resultado_estado = analisar_churn_por_fator(df_analise, 'Estado', 'Estado', 'categorica')
resultados_analises.append(('Estado', resultado_estado))

# 6. ANÁLISE POR TIPO DE CARTÃO
print("6️⃣ ANÁLISE POR TIPO DE CARTÃO")
resultado_tipo_cartao = analisar_churn_por_fator(df_analise, 'Tipo_Cartao', 'Tipo de Cartão', 'categorica')
resultados_analises.append(('Tipo_Cartao', resultado_tipo_cartao))

# 7. ANÁLISE POR PRODUTO MASTERCARD
print("7️⃣ ANÁLISE POR PRODUTO MASTERCARD")
resultado_produto = analisar_churn_por_fator(df_analise, 'Produto_Mastercard', 'Produto Mastercard', 'categorica')
resultados_analises.append(('Produto_Mastercard', resultado_produto))

# 8. ANÁLISE POR TEMPO DE CARTÃO
print("8️⃣ ANÁLISE POR TEMPO DE EMISSÃO DO CARTÃO")
faixas_tempo_cartao = [0, 6, 12, 18, 24, 36, 1000]
resultado_tempo_cartao = analisar_churn_por_fator(df_analise, 'Tempo_Cartao_Meses', 'Tempo do Cartão', 
                                                'numerica', faixas_tempo_cartao)
resultados_analises.append(('Tempo_Cartao', resultado_tempo_cartao))

# 9. ANÁLISE POR LIMITE DO CARTÃO
print("9️⃣ ANÁLISE POR LIMITE DO CARTÃO")
# Filtrar apenas cartões de crédito (com limite > 0)
df_credito = df_analise[df_analise['Limite_Cartao'] > 0]
faixas_limite = [0, 5000, 15000, 25000, 40000, 1000000]
resultado_limite = analisar_churn_por_fator(df_credito, 'Limite_Cartao', 'Limite do Cartão', 
                                          'numerica', faixas_limite)
resultados_analises.append(('Limite_Cartao', resultado_limite))

# =============================================================================
# GERAÇÃO DE GRÁFICOS
# =============================================================================

print("📊 GERANDO GRÁFICOS DE CHURN POR FATOR...")
print()

# Criar figura com subplots para todos os gráficos
fig = plt.figure(figsize=(20, 24))

# Configuração dos subplots (3 colunas, 3 linhas)
subplot_configs = [
    (3, 3, 1, 'Idade'),
    (3, 3, 2, 'Renda_Anual'),
    (3, 3, 3, 'Tempo_Conta'),
    (3, 3, 4, 'Conta_Adicional'),
    (3, 3, 5, 'Estado'),
    (3, 3, 6, 'Tipo_Cartao'),
    (3, 3, 7, 'Produto_Mastercard'),
    (3, 3, 8, 'Tempo_Cartao'),
    (3, 3, 9, 'Limite_Cartao')
]

# Títulos dos gráficos
titulos_graficos = {
    'Idade': 'Taxa de Churn por Faixa Etária',
    'Renda_Anual': 'Taxa de Churn por Faixa de Renda',
    'Tempo_Conta': 'Taxa de Churn por Tempo de Conta',
    'Conta_Adicional': 'Taxa de Churn por Conta Adicional',
    'Estado': 'Taxa de Churn por Estado (Top 10)',
    'Tipo_Cartao': 'Taxa de Churn por Tipo de Cartão',
    'Produto_Mastercard': 'Taxa de Churn por Produto Mastercard',
    'Tempo_Cartao': 'Taxa de Churn por Tempo do Cartão',
    'Limite_Cartao': 'Taxa de Churn por Limite do Cartão'
}

for i, (rows, cols, pos, fator) in enumerate(subplot_configs):
    ax = plt.subplot(rows, cols, pos)
    
    # Encontrar dados do fator
    dados_fator = None
    for nome_fator, dados in resultados_analises:
        if nome_fator == fator:
            dados_fator = dados
            break
    
    if dados_fator is not None:
        # Preparar dados para o gráfico
        if fator == 'Estado':
            # Para estados, mostrar apenas top 10
            dados_plot = dados_fator.head(10)
        else:
            dados_plot = dados_fator
        
        # Criar gráfico de barras
        bars = ax.bar(range(len(dados_plot)), dados_plot['Taxa_Churn'], 
                     color='steelblue', alpha=0.7)
        
        # Configurar eixos
        ax.set_xlabel('Categorias')
        ax.set_ylabel('Taxa de Churn (%)')
        ax.set_title(titulos_graficos[fator], fontweight='bold', pad=20)
        
        # Rótulos do eixo X
        labels = [str(idx)[:15] for idx in dados_plot.index]  # Limitar tamanho dos labels
        ax.set_xticks(range(len(dados_plot)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # Adicionar valores nas barras
        for bar, valor in zip(bars, dados_plot['Taxa_Churn']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{valor:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # Grid
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, max(dados_plot['Taxa_Churn']) * 1.15)

plt.suptitle('ANÁLISE COMPLETA DE CHURN POR FATORES INDIVIDUAIS', 
             fontsize=20, fontweight='bold', y=0.98)
plt.tight_layout()
plt.subplots_adjust(top=0.95)
plt.savefig('analise_churn_completa_fatores.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico principal salvo: analise_churn_completa_fatores.png")

# =============================================================================
# INSIGHTS PRINCIPAIS
# =============================================================================

print("="*80)
print("🎯 INSIGHTS PRINCIPAIS - FATORES DE MAIOR IMPACTO NO CHURN")
print("="*80)
print()

print("🔍 TOP INSIGHTS POR FATOR:")
print()

# Analisar cada fator para encontrar insights
for nome_fator, dados in resultados_analises:
    if len(dados) > 1:  # Só analisar fatores com múltiplas categorias
        maior_churn = dados.iloc[0]  # Primeira linha (maior churn)
        menor_churn = dados.iloc[-1]  # Última linha (menor churn)
        
        print(f"📊 {nome_fator.upper()}:")
        print(f"   • MAIOR risco: {maior_churn.name} ({maior_churn['Taxa_Churn']:.1f}% churn)")
        print(f"   • MENOR risco: {menor_churn.name} ({menor_churn['Taxa_Churn']:.1f}% churn)")
        print(f"   • Diferença: {maior_churn['Taxa_Churn'] - menor_churn['Taxa_Churn']:.1f}pp")
        print()

# =============================================================================
# RESUMO EXECUTIVO
# =============================================================================

print("="*80)
print("📋 RESUMO EXECUTIVO - ANÁLISE DE CHURN")
print("="*80)
print()

print(f"📊 MÉTRICAS GERAIS:")
print(f"   • Taxa de churn geral: {taxa_churn_geral:.1f}%")
print(f"   • Critério: {dias_churn} dias sem transações")
print(f"   • Clientes analisados: {len(df_analise):,}")
print(f"   • Fatores analisados: {len(resultados_analises)}")
print()

print("🎯 PRÓXIMOS PASSOS SUGERIDOS:")
print("   1. Focar nos segmentos de MAIOR risco identificados")
print("   2. Desenvolver campanhas de retenção específicas")
print("   3. Analisar correlações entre fatores")
print("   4. Implementar modelo preditivo de churn")
print()

print("="*80)
print("✅ ANÁLISE DE CHURN COMPLETA FINALIZADA")
print("="*80)