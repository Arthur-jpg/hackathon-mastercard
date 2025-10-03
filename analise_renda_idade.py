"""
Análise de Correlação: Renda x Idade
Priceless Bank - Mastercard Challenge 2025

Objetivo: Identificar quais faixas etárias possuem maior poder aquisitivo
"""

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("💰 ANÁLISE DETALHADA: RENDA x IDADE")
print("="*80)

# ============================================================================
# CARREGAR E PREPARAR DADOS
# ============================================================================
print("\n📊 Carregando dados...")

df = pd.read_csv('Base_clientes.csv')

# Converter datas e calcular idade
df['Data_Nascimento'] = pd.to_datetime(df['Data_Nascimento'], format='%d/%m/%Y', errors='coerce')
data_referencia = datetime(2025, 10, 3)
df['Idade'] = ((data_referencia - df['Data_Nascimento']).dt.days / 365.25).round(0)

# Criar faixas etárias detalhadas
df['Faixa_Etaria'] = pd.cut(df['Idade'], 
                             bins=[0, 25, 30, 35, 40, 45, 50, 55, 60, 65, 100],
                             labels=['18-25', '26-30', '31-35', '36-40', '41-45', 
                                    '46-50', '51-55', '56-60', '61-65', '65+'])

# Remover valores nulos
df_analise = df[['Cliente_ID', 'Idade', 'Renda_Anual', 'Faixa_Etaria', 'Estado', 'Cidade', 'Numero_Cartoes']].dropna()

print(f"✓ {len(df_analise):,} clientes com dados completos\n")

# ============================================================================
# 1. ANÁLISE DE CORRELAÇÃO
# ============================================================================
print("="*80)
print("🔍 CORRELAÇÃO ENTRE RENDA E IDADE")
print("="*80)

correlacao = df_analise['Renda_Anual'].corr(df_analise['Idade'])
print(f"\n📊 Coeficiente de Correlação de Pearson: {correlacao:.4f}")

if abs(correlacao) < 0.1:
    interpretacao = "MUITO FRACA - Praticamente sem relação linear"
elif abs(correlacao) < 0.3:
    interpretacao = "FRACA - Pouca relação linear"
elif abs(correlacao) < 0.5:
    interpretacao = "MODERADA - Relação linear moderada"
elif abs(correlacao) < 0.7:
    interpretacao = "FORTE - Forte relação linear"
else:
    interpretacao = "MUITO FORTE - Relação linear muito forte"

print(f"Interpretação: {interpretacao}")

if correlacao > 0:
    print("\n💡 Tendência: Quanto MAIOR a idade, MAIOR tende a ser a renda")
elif correlacao < 0:
    print("\n💡 Tendência: Quanto MAIOR a idade, MENOR tende a ser a renda")
else:
    print("\n💡 Não há relação linear entre idade e renda")

# ============================================================================
# 2. RENDA MÉDIA POR FAIXA ETÁRIA
# ============================================================================
print("\n" + "="*80)
print("💰 RENDA MÉDIA POR FAIXA ETÁRIA")
print("="*80)

renda_por_faixa = df_analise.groupby('Faixa_Etaria').agg({
    'Renda_Anual': ['mean', 'median', 'std', 'count']
}).round(2)

renda_por_faixa.columns = ['Renda_Média', 'Renda_Mediana', 'Desvio_Padrão', 'Num_Clientes']
renda_por_faixa = renda_por_faixa.sort_values('Renda_Média', ascending=False)

print("\n📊 Ranking das Faixas Etárias por Renda Média:")
print(renda_por_faixa.to_string())

# Identificar faixa com maior renda
faixa_mais_rica = renda_por_faixa.index[0]
renda_mais_alta = renda_por_faixa.iloc[0]['Renda_Média']

print(f"\n🏆 FAIXA ETÁRIA MAIS RICA: {faixa_mais_rica} anos")
print(f"   💵 Renda Média: R$ {renda_mais_alta:,.2f}")
print(f"   👥 Número de Clientes: {int(renda_por_faixa.iloc[0]['Num_Clientes'])}")

# Faixa com menor renda
faixa_mais_pobre = renda_por_faixa.index[-1]
renda_mais_baixa = renda_por_faixa.iloc[-1]['Renda_Média']

print(f"\n📉 FAIXA ETÁRIA COM MENOR RENDA: {faixa_mais_pobre} anos")
print(f"   💵 Renda Média: R$ {renda_mais_baixa:,.2f}")
print(f"   👥 Número de Clientes: {int(renda_por_faixa.iloc[-1]['Num_Clientes'])}")

diferenca_percentual = ((renda_mais_alta - renda_mais_baixa) / renda_mais_baixa * 100)
print(f"\n📈 Diferença: A faixa mais rica ganha {diferenca_percentual:.1f}% a mais que a mais pobre")

# ============================================================================
# 3. DISTRIBUIÇÃO DE RENDA POR IDADE EXATA
# ============================================================================
print("\n" + "="*80)
print("🎯 TOP 10 IDADES COM MAIOR RENDA MÉDIA")
print("="*80)

renda_por_idade = df_analise.groupby('Idade').agg({
    'Renda_Anual': ['mean', 'count']
}).round(2)
renda_por_idade.columns = ['Renda_Média', 'Num_Clientes']
renda_por_idade = renda_por_idade[renda_por_idade['Num_Clientes'] >= 5]  # Pelo menos 5 clientes
renda_por_idade = renda_por_idade.sort_values('Renda_Média', ascending=False)

print("\n📊 Top 10 Idades Específicas com Maior Renda:")
for idx, (idade, row) in enumerate(renda_por_idade.head(10).iterrows(), 1):
    print(f"{idx:2d}. {int(idade)} anos → R$ {row['Renda_Média']:>12,.2f} ({int(row['Num_Clientes'])} clientes)")

# ============================================================================
# 4. CLIENTES DE ALTA RENDA (TOP 10%)
# ============================================================================
print("\n" + "="*80)
print("💎 PERFIL DOS CLIENTES DE ALTA RENDA (TOP 10%)")
print("="*80)

percentil_90 = df_analise['Renda_Anual'].quantile(0.90)
clientes_ricos = df_analise[df_analise['Renda_Anual'] >= percentil_90]

print(f"\n💰 Renda mínima para TOP 10%: R$ {percentil_90:,.2f}")
print(f"👥 Quantidade de clientes: {len(clientes_ricos)}")
print(f"\n📊 Perfil dos Clientes de Alta Renda:")
print(f"   • Idade Média: {clientes_ricos['Idade'].mean():.1f} anos")
print(f"   • Idade Mediana: {clientes_ricos['Idade'].median():.0f} anos")
print(f"   • Renda Média: R$ {clientes_ricos['Renda_Anual'].mean():,.2f}")
print(f"   • Cartões Médio: {clientes_ricos['Numero_Cartoes'].mean():.1f}")

print(f"\n🎂 Distribuição Etária dos Ricos (TOP 10%):")
dist_ricos = clientes_ricos['Faixa_Etaria'].value_counts().sort_index()
for faixa, count in dist_ricos.items():
    pct = (count / len(clientes_ricos)) * 100
    print(f"   • {faixa} anos: {count} clientes ({pct:.1f}%)")

# ============================================================================
# 5. ANÁLISE POR ESTADO
# ============================================================================
print("\n" + "="*80)
print("🗺️ RENDA x IDADE POR ESTADO")
print("="*80)

print("\n📊 Renda Média e Idade Média por Estado:")
por_estado = df_analise.groupby('Estado').agg({
    'Renda_Anual': 'mean',
    'Idade': 'mean',
    'Cliente_ID': 'count'
}).round(2)
por_estado.columns = ['Renda_Média', 'Idade_Média', 'Num_Clientes']
por_estado = por_estado.sort_values('Renda_Média', ascending=False)

for estado, row in por_estado.iterrows():
    print(f"\n{estado}:")
    print(f"   💵 Renda Média: R$ {row['Renda_Média']:,.2f}")
    print(f"   🎂 Idade Média: {row['Idade_Média']:.1f} anos")
    print(f"   👥 Clientes: {int(row['Num_Clientes'])}")

# ============================================================================
# 6. VISUALIZAÇÕES INTERATIVAS
# ============================================================================
print("\n" + "="*80)
print("📊 GERANDO VISUALIZAÇÕES INTERATIVAS")
print("="*80)

# 1. Scatter plot Renda x Idade
fig1 = px.scatter(
    df_analise,
    x='Idade',
    y='Renda_Anual',
    color='Estado',
    size='Numero_Cartoes',
    hover_data=['Cidade'],
    title='💰 Correlação: Renda x Idade (tamanho = número de cartões)',
    labels={'Idade': 'Idade (anos)', 'Renda_Anual': 'Renda Anual (R$)'},
    height=600
)
fig1.write_html('correlacao_renda_idade_scatter.html')
print("\n✓ Gráfico salvo: correlacao_renda_idade_scatter.html")

# 2. Box plot Renda por Faixa Etária
fig2 = go.Figure()
for faixa in sorted(df_analise['Faixa_Etaria'].dropna().unique()):
    dados_faixa = df_analise[df_analise['Faixa_Etaria'] == faixa]['Renda_Anual']
    fig2.add_trace(go.Box(
        y=dados_faixa,
        name=str(faixa),
        boxmean='sd'
    ))

fig2.update_layout(
    title='📊 Distribuição de Renda por Faixa Etária (Box Plot)',
    yaxis_title='Renda Anual (R$)',
    xaxis_title='Faixa Etária',
    height=600
)
fig2.write_html('distribuicao_renda_faixa_etaria.html')
print("✓ Gráfico salvo: distribuicao_renda_faixa_etaria.html")

# 3. Gráfico de barras - Renda Média por Faixa Etária
fig3 = go.Figure()

renda_por_faixa_sorted = df_analise.groupby('Faixa_Etaria')['Renda_Anual'].mean().sort_index()

fig3.add_trace(go.Bar(
    x=renda_por_faixa_sorted.index.astype(str),
    y=renda_por_faixa_sorted.values,
    marker_color='rgb(55, 128, 191)',
    text=[f'R$ {val:,.0f}' for val in renda_por_faixa_sorted.values],
    textposition='outside'
))

fig3.update_layout(
    title='💵 Renda Média por Faixa Etária',
    xaxis_title='Faixa Etária',
    yaxis_title='Renda Média Anual (R$)',
    height=600
)
fig3.write_html('renda_media_faixa_etaria.html')
print("✓ Gráfico salvo: renda_media_faixa_etaria.html")

# 4. Heatmap Renda Média por Estado e Faixa Etária
pivot_renda = df_analise.pivot_table(
    values='Renda_Anual',
    index='Estado',
    columns='Faixa_Etaria',
    aggfunc='mean'
).round(0)

fig4 = go.Figure(data=go.Heatmap(
    z=pivot_renda.values,
    x=pivot_renda.columns.astype(str),
    y=pivot_renda.index,
    colorscale='RdYlGn',
    text=pivot_renda.values.astype(int),
    texttemplate='R$%{text}',
    textfont={"size": 10},
    colorbar=dict(title="Renda Média<br>(R$)")
))

fig4.update_layout(
    title='🔥 Heatmap: Renda Média por Estado e Faixa Etária',
    xaxis_title='Faixa Etária',
    yaxis_title='Estado',
    height=500
)
fig4.write_html('heatmap_renda_estado_idade.html')
print("✓ Gráfico salvo: heatmap_renda_estado_idade.html")

# 5. Histograma 2D - Densidade de Renda x Idade
fig5 = go.Figure(go.Histogram2d(
    x=df_analise['Idade'],
    y=df_analise['Renda_Anual'],
    colorscale='Viridis',
    nbinsx=30,
    nbinsy=30
))

fig5.update_layout(
    title='🎨 Densidade: Concentração de Clientes por Renda e Idade',
    xaxis_title='Idade (anos)',
    yaxis_title='Renda Anual (R$)',
    height=600
)
fig5.write_html('densidade_renda_idade.html')
print("✓ Gráfico salvo: densidade_renda_idade.html")

# 6. Comparação: TOP 10% vs Resto
fig6 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Distribuição de Idade - TOP 10%', 'Distribuição de Idade - Demais 90%'),
    specs=[[{'type': 'histogram'}, {'type': 'histogram'}]]
)

outros_clientes = df_analise[df_analise['Renda_Anual'] < percentil_90]

fig6.add_trace(
    go.Histogram(x=clientes_ricos['Idade'], name='TOP 10%', marker_color='gold', nbinsx=20),
    row=1, col=1
)

fig6.add_trace(
    go.Histogram(x=outros_clientes['Idade'], name='Demais 90%', marker_color='lightblue', nbinsx=20),
    row=1, col=2
)

fig6.update_layout(
    title_text='👑 Comparação de Distribuição Etária: Ricos vs Demais',
    height=500,
    showlegend=False
)
fig6.write_html('comparacao_idade_ricos_vs_outros.html')
print("✓ Gráfico salvo: comparacao_idade_ricos_vs_outros.html")

# ============================================================================
# 7. INSIGHTS ESTRATÉGICOS
# ============================================================================
print("\n" + "="*80)
print("💡 INSIGHTS ESTRATÉGICOS - QUEM TEM MAIS DINHEIRO?")
print("="*80)

print("\n🎯 CONCLUSÕES PRINCIPAIS:\n")

print(f"1. PERFIL DE ALTA RENDA:")
print(f"   • Faixa etária predominante: {faixa_mais_rica} anos")
print(f"   • Renda média nesta faixa: R$ {renda_mais_alta:,.2f}")
print(f"   • Idade média dos 10% mais ricos: {clientes_ricos['Idade'].mean():.1f} anos")

print(f"\n2. CORRELAÇÃO IDADE-RENDA:")
if abs(correlacao) < 0.1:
    print(f"   • A idade NÃO é um bom preditor de renda (correlação: {correlacao:.4f})")
    print(f"   • Clientes de todas as idades podem ter alta renda")
else:
    print(f"   • Correlação: {correlacao:.4f} ({interpretacao})")

print(f"\n3. DISTRIBUIÇÃO GEOGRÁFICA:")
estado_mais_rico = por_estado.index[0]
print(f"   • Estado com maior renda média: {estado_mais_rico}")
print(f"   • Renda média em {estado_mais_rico}: R$ {por_estado.loc[estado_mais_rico, 'Renda_Média']:,.2f}")

print(f"\n4. OPORTUNIDADES DE NEGÓCIO:")
print(f"   • Focar produtos premium nas faixas: {', '.join([str(f) for f in renda_por_faixa.head(3).index])}")
print(f"   • {len(clientes_ricos)} clientes (TOP 10%) representam potencial de alta margem")
print(f"   • Estados prioritários: {', '.join(por_estado.head(3).index)}")

# ============================================================================
# 8. EXPORTAR DADOS
# ============================================================================
print("\n" + "="*80)
print("💾 EXPORTANDO DADOS")
print("="*80)

# Salvar análise por faixa etária
renda_por_faixa.to_csv('analise_renda_por_faixa_etaria.csv', encoding='utf-8-sig')
print("\n✓ Arquivo salvo: analise_renda_por_faixa_etaria.csv")

# Salvar clientes de alta renda
clientes_ricos_export = df_analise[df_analise['Renda_Anual'] >= percentil_90].copy()
clientes_ricos_export.to_csv('clientes_alta_renda_top10.csv', index=False, encoding='utf-8-sig')
print("✓ Arquivo salvo: clientes_alta_renda_top10.csv")

# Salvar análise por estado
por_estado.to_csv('renda_idade_por_estado.csv', encoding='utf-8-sig')
print("✓ Arquivo salvo: renda_idade_por_estado.csv")

print("\n" + "="*80)
print("✅ ANÁLISE COMPLETA!")
print("="*80)

print("\n📂 Arquivos HTML gerados (abra no navegador):")
print("   • correlacao_renda_idade_scatter.html")
print("   • distribuicao_renda_faixa_etaria.html")
print("   • renda_media_faixa_etaria.html")
print("   • heatmap_renda_estado_idade.html")
print("   • densidade_renda_idade.html")
print("   • comparacao_idade_ricos_vs_outros.html")

print("\n📊 Arquivos CSV gerados:")
print("   • analise_renda_por_faixa_etaria.csv")
print("   • clientes_alta_renda_top10.csv")
print("   • renda_idade_por_estado.csv")

print("\n" + "="*80)
