#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANÁLISE CORRIGIDA: CHURN TEMPO DE CONTA vs TEMPO DE CARTÃO
Comparação rigorosa considerando apenas cartões emitidos a partir de 2023
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
print("🔧 ANÁLISE CORRIGIDA: CHURN TEMPO CONTA vs CARTÃO")
print("="*80)
print()

# =============================================================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# =============================================================================

# Carregar dados
df_clientes = pd.read_csv('data/Base_clientes.csv')
df_transacoes = pd.read_csv('data/Base_transacoes.csv')
df_cartoes = pd.read_csv('data/Base_cartoes.csv')

print("📊 DADOS CARREGADOS:")
print(f"   • Clientes: {len(df_clientes):,}")
print(f"   • Transações: {len(df_transacoes):,}")
print(f"   • Cartões: {len(df_cartoes):,}")
print()

# Converter datas
df_transacoes['Data'] = pd.to_datetime(df_transacoes['Data'])
df_clientes['Data_Nascimento'] = pd.to_datetime(df_clientes['Data_Nascimento'], format='%d/%m/%Y')
df_clientes['Data_Criacao_Conta'] = pd.to_datetime(df_clientes['Data_Criacao_Conta'])
df_cartoes['Data_Emissao'] = pd.to_datetime(df_cartoes['Data_Emissao'])

# Data de referência
data_referencia = df_transacoes['Data'].max()
print(f"📅 Data de referência: {data_referencia.strftime('%Y-%m-%d')}")

# =============================================================================
# FILTRO CRÍTICO: APENAS CARTÕES A PARTIR DE 2023
# =============================================================================

print("🔍 APLICANDO FILTRO CRÍTICO:")
print("-" * 30)

# Filtrar cartões emitidos a partir de 2023
data_corte = pd.to_datetime('2023-01-01')
print(f"📅 Data de corte: {data_corte.strftime('%Y-%m-%d')}")

cartoes_antes_2023 = len(df_cartoes[df_cartoes['Data_Emissao'] < data_corte])
cartoes_apos_2023 = len(df_cartoes[df_cartoes['Data_Emissao'] >= data_corte])

print(f"📊 DISTRIBUIÇÃO DE CARTÕES:")
print(f"   • Cartões ANTES de 2023: {cartoes_antes_2023:,} ({cartoes_antes_2023/len(df_cartoes)*100:.1f}%)")
print(f"   • Cartões A PARTIR de 2023: {cartoes_apos_2023:,} ({cartoes_apos_2023/len(df_cartoes)*100:.1f}%)")
print()

# Filtrar apenas cartões válidos (>= 2023)
df_cartoes_filtrado = df_cartoes[df_cartoes['Data_Emissao'] >= data_corte].copy()
print(f"✅ Cartões após filtro: {len(df_cartoes_filtrado):,}")

# Verificar range de datas após filtro
print(f"📊 NOVO RANGE DE CARTÕES:")
print(f"   • Data mínima: {df_cartoes_filtrado['Data_Emissao'].min().strftime('%Y-%m-%d')}")
print(f"   • Data máxima: {df_cartoes_filtrado['Data_Emissao'].max().strftime('%Y-%m-%d')}")

# Verificar range de contas para comparação
print(f"📊 RANGE DE CONTAS (para comparação):")
print(f"   • Data mínima: {df_clientes['Data_Criacao_Conta'].min().strftime('%Y-%m-%d')}")
print(f"   • Data máxima: {df_clientes['Data_Criacao_Conta'].max().strftime('%Y-%m-%d')}")
print()

# =============================================================================
# CÁLCULO DE TEMPOS CORRIGIDOS
# =============================================================================

print("⏰ CALCULANDO TEMPOS CORRIGIDOS:")
print("-" * 35)

# Tempos para contas (sem mudança)
df_clientes['Tempo_Conta_Meses'] = ((data_referencia - df_clientes['Data_Criacao_Conta']).dt.days / 30.44)

# Tempos para cartões (apenas >= 2023)
df_cartoes_filtrado['Tempo_Cartao_Meses'] = ((data_referencia - df_cartoes_filtrado['Data_Emissao']).dt.days / 30.44)

print(f"📊 ESTATÍSTICAS CORRIGIDAS:")
print(f"   TEMPO DE CONTA:")
print(f"   • Mínimo: {df_clientes['Tempo_Conta_Meses'].min():.2f} meses")
print(f"   • Máximo: {df_clientes['Tempo_Conta_Meses'].max():.2f} meses")
print(f"   • Média: {df_clientes['Tempo_Conta_Meses'].mean():.2f} meses")
print()
print(f"   TEMPO DE CARTÃO (>= 2023):")
print(f"   • Mínimo: {df_cartoes_filtrado['Tempo_Cartao_Meses'].min():.2f} meses")
print(f"   • Máximo: {df_cartoes_filtrado['Tempo_Cartao_Meses'].max():.2f} meses")
print(f"   • Média: {df_cartoes_filtrado['Tempo_Cartao_Meses'].mean():.2f} meses")
print()

# =============================================================================
# CONECTAR DADOS PARA ANÁLISE DE CHURN
# =============================================================================

print("🔗 CONECTANDO DADOS PARA ANÁLISE:")
print("-" * 35)

# Identificar churn baseado em última transação
ultima_transacao = df_transacoes.groupby('Cliente_ID')['Data'].max().reset_index()
ultima_transacao.columns = ['Cliente_ID', 'Ultima_Transacao']

dias_churn = 90
data_limite_churn = data_referencia - timedelta(days=dias_churn)
ultima_transacao['Churn'] = ultima_transacao['Ultima_Transacao'] < data_limite_churn

print(f"🎯 CRITÉRIO DE CHURN: {dias_churn} dias sem transações")
print(f"📊 Taxa de churn geral: {ultima_transacao['Churn'].mean()*100:.1f}%")
print()

# Conectar cartões filtrados com clientes que têm transações
cartao_cliente = df_transacoes[['Cliente_ID', 'ID_Cartao']].drop_duplicates()

# Filtrar apenas cartões válidos (>= 2023) que têm transações
cartoes_validos = cartao_cliente.merge(df_cartoes_filtrado, on='ID_Cartao', how='inner')
print(f"✅ Cartões válidos com transações: {len(cartoes_validos):,}")

# Conectar com dados de clientes e churn
df_analise = cartoes_validos.merge(df_clientes[['Cliente_ID', 'Data_Criacao_Conta']], 
                                  on='Cliente_ID', how='left')
df_analise = df_analise.merge(ultima_transacao[['Cliente_ID', 'Churn']], 
                             on='Cliente_ID', how='left')

# Recalcular tempos na base conectada
df_analise['Tempo_Conta_Meses'] = ((data_referencia - df_analise['Data_Criacao_Conta']).dt.days / 30.44)
df_analise['Tempo_Cartao_Meses'] = ((data_referencia - df_analise['Data_Emissao']).dt.days / 30.44)

print(f"📊 BASE FINAL PARA ANÁLISE:")
print(f"   • Registros: {len(df_analise):,}")
print(f"   • Clientes únicos: {df_analise['Cliente_ID'].nunique():,}")
print(f"   • Taxa de churn: {df_analise['Churn'].mean()*100:.1f}%")
print()
print(f"   TEMPOS NA BASE CONECTADA:")
print(f"   • Conta - Min: {df_analise['Tempo_Conta_Meses'].min():.1f}, Max: {df_analise['Tempo_Conta_Meses'].max():.1f}")
print(f"   • Cartão - Min: {df_analise['Tempo_Cartao_Meses'].min():.1f}, Max: {df_analise['Tempo_Cartao_Meses'].max():.1f}")
print()

# =============================================================================
# DEFINIR INTERVALOS CONSISTENTES
# =============================================================================

print("📏 DEFININDO INTERVALOS CONSISTENTES:")
print("-" * 40)

# Usar o menor máximo para garantir consistência
tempo_max_conta = df_analise['Tempo_Conta_Meses'].max()
tempo_max_cartao = df_analise['Tempo_Cartao_Meses'].max()
tempo_max_comum = min(tempo_max_conta, tempo_max_cartao)

print(f"📊 TEMPOS MÁXIMOS PARA DEFINIR INTERVALOS:")
print(f"   • Máximo tempo de conta: {tempo_max_conta:.1f} meses")
print(f"   • Máximo tempo de cartão: {tempo_max_cartao:.1f} meses")
print(f"   • Máximo comum (usado): {tempo_max_comum:.1f} meses")
print()

# Definir intervalos baseados no tempo máximo comum
if tempo_max_comum >= 24:
    intervalos = [0, 6, 12, 18, 24, 1000]
    labels = ['0-6 meses', '6-12 meses', '12-18 meses', '18-24 meses', '24+ meses']
elif tempo_max_comum >= 18:
    intervalos = [0, 6, 12, 18, 1000]
    labels = ['0-6 meses', '6-12 meses', '12-18 meses', '18+ meses']
else:
    intervalos = [0, 6, 12, 1000]
    labels = ['0-6 meses', '6-12 meses', '12+ meses']

print(f"✅ INTERVALOS DEFINIDOS: {labels}")
print()

# =============================================================================
# FUNÇÃO PARA ANÁLISE RIGOROSA
# =============================================================================

def analisar_churn_rigoroso(df, coluna_tempo, titulo):
    """
    Análise rigorosa de churn por tempo
    """
    print(f"🔍 ANÁLISE: {titulo}")
    print("-" * 50)
    
    # Filtrar dados válidos
    df_clean = df.dropna(subset=[coluna_tempo, 'Churn']).copy()
    df_clean = df_clean[df_clean[coluna_tempo] >= 0]
    
    # Criar faixas
    df_clean['Faixa_Tempo'] = pd.cut(df_clean[coluna_tempo], bins=intervalos, 
                                    labels=labels, include_lowest=True)
    
    # Análise detalhada
    analise = df_clean.groupby('Faixa_Tempo', observed=True).agg({
        'Churn': ['count', 'sum', 'mean'],
        coluna_tempo: ['min', 'max', 'mean']
    }).round(2)
    
    # Flatten columns
    analise.columns = ['Total_Clientes', 'Clientes_Churn', 'Taxa_Churn_Calc', 
                      'Tempo_Min', 'Tempo_Max', 'Tempo_Medio']
    
    analise['Taxa_Churn'] = (analise['Taxa_Churn_Calc'] * 100).round(1)
    analise['Pct_Base'] = (analise['Total_Clientes'] / analise['Total_Clientes'].sum() * 100).round(1)
    
    # Exibir resultados
    print("📊 RESULTADOS DETALHADOS:")
    for idx, row in analise.iterrows():
        print(f"   • {idx}:")
        print(f"     - Taxa de churn: {row['Taxa_Churn']:.1f}%")
        print(f"     - Clientes: {int(row['Total_Clientes']):,} ({row['Pct_Base']:.1f}% da base)")
        print(f"     - Em churn: {int(row['Clientes_Churn']):,}")
        print(f"     - Tempo médio: {row['Tempo_Medio']:.1f} meses")
        print()
    
    return analise

# =============================================================================
# ANÁLISES RIGOROSAS
# =============================================================================

print("="*80)
print("📊 ANÁLISES RIGOROSAS - DADOS CONSISTENTES")
print("="*80)
print()

# Análise por tempo de conta
resultado_conta = analisar_churn_rigoroso(df_analise, 'Tempo_Conta_Meses', 
                                         'CHURN POR TEMPO DE CONTA')

# Análise por tempo de cartão
resultado_cartao = analisar_churn_rigoroso(df_analise, 'Tempo_Cartao_Meses', 
                                          'CHURN POR TEMPO DE CARTÃO')

# =============================================================================
# COMPARAÇÃO DIRETA RIGOROSA
# =============================================================================

print("="*80)
print("🔍 COMPARAÇÃO DIRETA - CONTA vs CARTÃO")
print("="*80)
print()

# Criar tabela comparativa
comparacao = pd.DataFrame(index=labels)
comparacao['Taxa_Churn_Conta'] = 0.0
comparacao['Taxa_Churn_Cartao'] = 0.0
comparacao['Clientes_Conta'] = 0
comparacao['Clientes_Cartao'] = 0

# Preencher dados disponíveis
for faixa in labels:
    if faixa in resultado_conta.index:
        comparacao.loc[faixa, 'Taxa_Churn_Conta'] = resultado_conta.loc[faixa, 'Taxa_Churn']
        comparacao.loc[faixa, 'Clientes_Conta'] = int(resultado_conta.loc[faixa, 'Total_Clientes'])
    
    if faixa in resultado_cartao.index:
        comparacao.loc[faixa, 'Taxa_Churn_Cartao'] = resultado_cartao.loc[faixa, 'Taxa_Churn']
        comparacao.loc[faixa, 'Clientes_Cartao'] = int(resultado_cartao.loc[faixa, 'Total_Clientes'])

# Calcular diferenças
comparacao['Diferenca_Taxa'] = comparacao['Taxa_Churn_Cartao'] - comparacao['Taxa_Churn_Conta']

print("📊 COMPARAÇÃO DETALHADA:")
print("=" * 110)
print(f"{'Faixa Temporal':<15} {'Churn Conta':<12} {'Churn Cartão':<14} {'Diferença':<10} {'Clientes Conta':<15} {'Clientes Cartão':<16}")
print("=" * 110)

for faixa, row in comparacao.iterrows():
    diferenca_str = f"{row['Diferenca_Taxa']:+.1f}pp" if row['Diferenca_Taxa'] != 0 else "0.0pp"
    print(f"{faixa:<15} {row['Taxa_Churn_Conta']:<11.1f}% {row['Taxa_Churn_Cartao']:<13.1f}% "
          f"{diferenca_str:<10} {row['Clientes_Conta']:<15,} {row['Clientes_Cartao']:<16,}")

print("=" * 110)
print()

# =============================================================================
# ANÁLISE ESTATÍSTICA
# =============================================================================

print("📈 ANÁLISE ESTATÍSTICA:")
print("-" * 25)

# Correlação entre tempos
correlacao_tempos = df_analise[['Tempo_Conta_Meses', 'Tempo_Cartao_Meses']].corr().iloc[0,1]
print(f"🔗 Correlação entre tempo de conta e cartão: {correlacao_tempos:.3f}")

# Correlação com churn
from scipy import stats

correlacao_conta_churn = stats.pearsonr(df_analise['Tempo_Conta_Meses'], df_analise['Churn'])[0]
correlacao_cartao_churn = stats.pearsonr(df_analise['Tempo_Cartao_Meses'], df_analise['Churn'])[0]

print(f"📊 Correlação tempo conta × churn: {correlacao_conta_churn:.3f}")
print(f"📊 Correlação tempo cartão × churn: {correlacao_cartao_churn:.3f}")
print()

# Teste de diferença de médias
from scipy.stats import ttest_ind

clientes_churn = df_analise[df_analise['Churn'] == True]
clientes_ativo = df_analise[df_analise['Churn'] == False]

if len(clientes_churn) > 0 and len(clientes_ativo) > 0:
    # Teste para tempo de conta
    t_stat_conta, p_val_conta = ttest_ind(clientes_churn['Tempo_Conta_Meses'], 
                                         clientes_ativo['Tempo_Conta_Meses'])
    
    # Teste para tempo de cartão
    t_stat_cartao, p_val_cartao = ttest_ind(clientes_churn['Tempo_Cartao_Meses'], 
                                           clientes_ativo['Tempo_Cartao_Meses'])
    
    print(f"🔬 TESTES ESTATÍSTICOS (Diferença de médias):")
    print(f"   • Tempo de conta - t: {t_stat_conta:.3f}, p-valor: {p_val_conta:.4f}")
    print(f"   • Tempo de cartão - t: {t_stat_cartao:.3f}, p-valor: {p_val_cartao:.4f}")
    print()

# =============================================================================
# GRÁFICOS COMPARATIVOS FINAIS
# =============================================================================

print("📊 GERANDO GRÁFICOS COMPARATIVOS...")

# Criar gráfico comparativo
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('COMPARAÇÃO RIGOROSA: CHURN TEMPO CONTA vs CARTÃO (>=2023)', 
             fontsize=16, fontweight='bold')

# Preparar dados para gráficos
faixas_graficos = []
churn_conta_graficos = []
churn_cartao_graficos = []
clientes_conta_graficos = []
clientes_cartao_graficos = []

for faixa, row in comparacao.iterrows():
    if row['Clientes_Conta'] > 0 or row['Clientes_Cartao'] > 0:  # Apenas faixas com dados
        faixas_graficos.append(faixa)
        churn_conta_graficos.append(row['Taxa_Churn_Conta'])
        churn_cartao_graficos.append(row['Taxa_Churn_Cartao'])
        clientes_conta_graficos.append(row['Clientes_Conta'])
        clientes_cartao_graficos.append(row['Clientes_Cartao'])

x = np.arange(len(faixas_graficos))
width = 0.35

# Gráfico 1: Comparação Taxa de Churn
bars1 = ax1.bar(x - width/2, churn_conta_graficos, width, label='Tempo de Conta', 
                color='skyblue', alpha=0.8)
bars2 = ax1.bar(x + width/2, churn_cartao_graficos, width, label='Tempo de Cartão', 
                color='salmon', alpha=0.8)

ax1.set_xlabel('Faixa Temporal')
ax1.set_ylabel('Taxa de Churn (%)')
ax1.set_title('Comparação: Taxa de Churn')
ax1.set_xticks(x)
ax1.set_xticklabels(faixas_graficos, rotation=45)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Adicionar valores nas barras
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

for bar in bars2:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

# Gráfico 2: Diferença de Taxa de Churn
diferencas = [comparacao.loc[faixa, 'Diferenca_Taxa'] for faixa in faixas_graficos]
colors = ['green' if d < 0 else 'red' for d in diferencas]

bars3 = ax2.bar(faixas_graficos, diferencas, color=colors, alpha=0.7)
ax2.set_xlabel('Faixa Temporal')
ax2.set_ylabel('Diferença (Cartão - Conta) pp')
ax2.set_title('Diferença de Taxa de Churn\n(Valores negativos = Conta pior)')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)

# Adicionar valores
for bar, diff in zip(bars3, diferencas):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height > 0 else -0.3),
             f'{diff:+.1f}pp', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

# Gráfico 3: Distribuição de Clientes - Conta
bars4 = ax3.bar(faixas_graficos, clientes_conta_graficos, color='skyblue', alpha=0.8)
ax3.set_xlabel('Faixa Temporal')
ax3.set_ylabel('Número de Clientes')
ax3.set_title('Distribuição de Clientes - Tempo de Conta')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3)

# Adicionar valores
for bar, valor in zip(bars4, clientes_conta_graficos):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{valor:,}', ha='center', va='bottom', fontsize=9)

# Gráfico 4: Distribuição de Clientes - Cartão
bars5 = ax4.bar(faixas_graficos, clientes_cartao_graficos, color='salmon', alpha=0.8)
ax4.set_xlabel('Faixa Temporal')
ax4.set_ylabel('Número de Clientes')
ax4.set_title('Distribuição de Clientes - Tempo de Cartão')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)

# Adicionar valores
for bar, valor in zip(bars5, clientes_cartao_graficos):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{valor:,}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('comparacao_rigorosa_churn_tempo_conta_cartao.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: comparacao_rigorosa_churn_tempo_conta_cartao.png")
print()

# =============================================================================
# CONCLUSÕES FINAIS
# =============================================================================

print("="*80)
print("🎯 CONCLUSÕES FINAIS - ANÁLISE RIGOROSA")
print("="*80)
print()

print("✅ DADOS CORRIGIDOS E CONSISTENTES:")
print(f"   • Apenas cartões >= 2023: {len(df_cartoes_filtrado):,}")
print(f"   • Base de análise: {len(df_analise):,} registros")
print(f"   • Correlação tempos: {correlacao_tempos:.3f}")
print()

print("🚨 PRINCIPAIS DESCOBERTAS:")

# Identificar maior diferença
maior_diferenca_idx = abs(comparacao['Diferenca_Taxa']).idxmax()
maior_diferenca = comparacao.loc[maior_diferenca_idx, 'Diferenca_Taxa']

print(f"   1. MAIOR DIFERENÇA: {maior_diferenca_idx}")
print(f"      • Diferença: {maior_diferenca:+.1f}pp")
print(f"      • Cartão: {comparacao.loc[maior_diferenca_idx, 'Taxa_Churn_Cartao']:.1f}% churn")
print(f"      • Conta: {comparacao.loc[maior_diferenca_idx, 'Taxa_Churn_Conta']:.1f}% churn")
print()

print(f"   2. CORRELAÇÕES:")
print(f"      • Tempo conta × churn: {correlacao_conta_churn:.3f}")
print(f"      • Tempo cartão × churn: {correlacao_cartao_churn:.3f}")
print()

print("🎯 RECOMENDAÇÕES BASEADAS NOS DADOS:")
print("   • Foco nas faixas com MAIOR diferença de churn")
print("   • Investigar causas específicas das divergências")
print("   • Desenvolver estratégias diferenciadas por tipo de tempo")
print()

print("="*80)
print("✅ ANÁLISE RIGOROSA COMPLETA")
print("="*80)