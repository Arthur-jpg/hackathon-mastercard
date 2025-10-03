"""
Análise e Segmentação de Clientes - Priceless Bank
Mastercard Challenge 2025

Este script realiza a análise completa de segmentação de clientes
utilizando dados demográficos e machine learning.
"""

# ============================================================================
# 1. IMPORTAR BIBLIOTECAS
# ============================================================================
print("🔄 Importando bibliotecas...")

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
sns.set_palette('husl')
plt.rcParams['figure.figsize'] = (12, 6)

print("✓ Bibliotecas importadas com sucesso!\n")

# ============================================================================
# 2. CARREGAR E EXPLORAR DADOS
# ============================================================================
print("="*80)
print("📊 CARREGANDO BASE DE DADOS")
print("="*80)

df_clientes = pd.read_csv('Base_clientes.csv')

print(f"\n📊 Total de clientes: {len(df_clientes):,}")
print(f"📋 Colunas disponíveis: {list(df_clientes.columns)}")
print("\n" + "="*80)
print("Primeiras 10 linhas:")
print(df_clientes.head(10))

# Informações do dataset
print("\n" + "="*80)
print("📈 INFORMAÇÕES DO DATASET:")
print("="*80)
df_clientes.info()

print("\n" + "="*80)
print("📊 ESTATÍSTICAS DESCRITIVAS:")
print("="*80)
print(df_clientes.describe())

# Valores ausentes
print("\n" + "="*80)
print("❓ VALORES AUSENTES POR COLUNA:")
print("="*80)
missing_data = pd.DataFrame({
    'Total Missing': df_clientes.isnull().sum(),
    'Percentual (%)': (df_clientes.isnull().sum() / len(df_clientes) * 100).round(2)
})
missing_data = missing_data[missing_data['Total Missing'] > 0].sort_values('Total Missing', ascending=False)
print(missing_data)

# ============================================================================
# 3. PREPARAÇÃO E ENGENHARIA DE FEATURES
# ============================================================================
print("\n" + "="*80)
print("🔧 PREPARAÇÃO E ENGENHARIA DE FEATURES")
print("="*80)

df = df_clientes.copy()

# Converter datas
df['Data_Nascimento'] = pd.to_datetime(df['Data_Nascimento'], format='%d/%m/%Y', errors='coerce')
df['Data_Criacao_Conta'] = pd.to_datetime(df['Data_Criacao_Conta'], errors='coerce')

# Calcular idade atual
data_referencia = datetime(2025, 10, 3)
df['Idade'] = ((data_referencia - df['Data_Nascimento']).dt.days / 365.25).round(0)

# Calcular tempo como cliente
df['Tempo_Cliente_Anos'] = ((data_referencia - df['Data_Criacao_Conta']).dt.days / 365.25).round(2)

# Criar faixas etárias
df['Faixa_Etaria'] = pd.cut(df['Idade'], 
                             bins=[0, 25, 35, 45, 55, 65, 100],
                             labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])

# Criar faixas de renda
df['Faixa_Renda'] = pd.cut(df['Renda_Anual'], 
                            bins=[0, 30000, 50000, 80000, 120000, np.inf],
                            labels=['Até 30k', '30k-50k', '50k-80k', '80k-120k', 'Acima 120k'])

# Converter conta adicional para binário
df['Possui_Conta_Adicional_Bin'] = df['Possui_Conta_Adicional'].map({'Sim': 1, 'Não': 0})

print(f"\n✓ Features criadas com sucesso!")
print(f"📊 Dataset atualizado: {df.shape[0]} linhas x {df.shape[1]} colunas\n")

# ============================================================================
# 4. ANÁLISE DEMOGRÁFICA - IDADE
# ============================================================================
print("="*80)
print("📊 ANÁLISE DEMOGRÁFICA - IDADE")
print("="*80)

print("\n📈 Estatísticas de Idade:")
print(f"  • Idade Média: {df['Idade'].mean():.1f} anos")
print(f"  • Idade Mediana: {df['Idade'].median():.1f} anos")
print(f"  • Idade Mínima: {df['Idade'].min():.0f} anos")
print(f"  • Idade Máxima: {df['Idade'].max():.0f} anos")
print(f"  • Desvio Padrão: {df['Idade'].std():.1f} anos")

print("\n📊 Distribuição por Faixa Etária:")
print(df['Faixa_Etaria'].value_counts().sort_index())

# Visualização
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Distribuição de Idade', 'Box Plot - Idade', 
                    'Distribuição por Faixa Etária', 'Idade Média por Estado'),
    specs=[[{'type': 'histogram'}, {'type': 'box'}],
           [{'type': 'bar'}, {'type': 'bar'}]]
)

fig.add_trace(
    go.Histogram(x=df['Idade'].dropna(), nbinsx=30, name='Idade',
                marker_color='rgb(55, 83, 109)'),
    row=1, col=1
)

fig.add_trace(
    go.Box(y=df['Idade'].dropna(), name='Idade', marker_color='rgb(26, 118, 255)'),
    row=1, col=2
)

faixa_etaria_count = df['Faixa_Etaria'].value_counts().sort_index()
fig.add_trace(
    go.Bar(x=faixa_etaria_count.index.astype(str), y=faixa_etaria_count.values,
          marker_color='rgb(50, 171, 96)', name='Faixa Etária'),
    row=2, col=1
)

idade_por_estado = df.groupby('Estado')['Idade'].mean().sort_values(ascending=False)
fig.add_trace(
    go.Bar(x=idade_por_estado.index, y=idade_por_estado.values,
          marker_color='rgb(219, 64, 82)', name='Idade Média'),
    row=2, col=2
)

fig.update_layout(height=800, showlegend=False, title_text="📊 Análise Completa - Idade dos Clientes")
fig.write_html('analise_idade.html')
print("\n✓ Gráfico salvo: analise_idade.html")

# ============================================================================
# 5. ANÁLISE DEMOGRÁFICA - RENDA
# ============================================================================
print("\n" + "="*80)
print("💰 ANÁLISE DEMOGRÁFICA - RENDA")
print("="*80)

print("\n💵 Estatísticas de Renda Anual:")
print(f"  • Renda Média: R$ {df['Renda_Anual'].mean():,.2f}")
print(f"  • Renda Mediana: R$ {df['Renda_Anual'].median():,.2f}")
print(f"  • Renda Mínima: R$ {df['Renda_Anual'].min():,.2f}")
print(f"  • Renda Máxima: R$ {df['Renda_Anual'].max():,.2f}")
print(f"  • Desvio Padrão: R$ {df['Renda_Anual'].std():,.2f}")

print("\n📊 Distribuição por Faixa de Renda:")
print(df['Faixa_Renda'].value_counts().sort_index())

# Visualização
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Distribuição de Renda Anual', 'Box Plot - Renda', 
                    'Distribuição por Faixa de Renda', 'Renda Média por Estado'),
    specs=[[{'type': 'histogram'}, {'type': 'box'}],
           [{'type': 'bar'}, {'type': 'bar'}]]
)

fig.add_trace(
    go.Histogram(x=df['Renda_Anual'].dropna(), nbinsx=40, name='Renda',
                marker_color='rgb(55, 128, 191)'),
    row=1, col=1
)

fig.add_trace(
    go.Box(y=df['Renda_Anual'].dropna(), name='Renda', marker_color='rgb(128, 0, 128)'),
    row=1, col=2
)

faixa_renda_count = df['Faixa_Renda'].value_counts().sort_index()
fig.add_trace(
    go.Bar(x=faixa_renda_count.index.astype(str), y=faixa_renda_count.values,
          marker_color='rgb(255, 144, 14)', name='Faixa Renda'),
    row=2, col=1
)

renda_por_estado = df.groupby('Estado')['Renda_Anual'].mean().sort_values(ascending=False)
fig.add_trace(
    go.Bar(x=renda_por_estado.index, y=renda_por_estado.values,
          marker_color='rgb(44, 160, 101)', name='Renda Média'),
    row=2, col=2
)

fig.update_layout(height=800, showlegend=False, title_text="💰 Análise Completa - Renda dos Clientes")
fig.write_html('analise_renda.html')
print("\n✓ Gráfico salvo: analise_renda.html")

# ============================================================================
# 6. ANÁLISE DEMOGRÁFICA - LOCALIZAÇÃO
# ============================================================================
print("\n" + "="*80)
print("🗺️ ANÁLISE DEMOGRÁFICA - LOCALIZAÇÃO")
print("="*80)

print(f"\n🌎 Estatísticas Geográficas:")
print(f"  • Total de Estados: {df['Estado'].nunique()}")
print(f"  • Total de Cidades: {df['Cidade'].nunique()}")

print("\n📊 Top 5 Estados por número de clientes:")
estado_count = df['Estado'].value_counts()
print(estado_count.head())

print("\n📊 Top 10 Cidades:")
print(df['Cidade'].value_counts().head(10))

# Visualização
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Top 10 Cidades', 'Distribuição por Estado', 
                    'Clientes por Estado (Pizza)', 'Renda Média vs Clientes por Estado'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}],
           [{'type': 'pie'}, {'type': 'scatter'}]]
)

top_cidades = df['Cidade'].value_counts().head(10)
fig.add_trace(
    go.Bar(y=top_cidades.index, x=top_cidades.values, orientation='h',
          marker_color='rgb(158, 202, 225)', name='Cidades'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=estado_count.index, y=estado_count.values,
          marker_color='rgb(94, 204, 243)', name='Estados'),
    row=1, col=2
)

fig.add_trace(
    go.Pie(labels=estado_count.index, values=estado_count.values),
    row=2, col=1
)

estado_stats = df.groupby('Estado').agg({
    'Cliente_ID': 'count',
    'Renda_Anual': 'mean'
}).reset_index()
estado_stats.columns = ['Estado', 'Num_Clientes', 'Renda_Media']

fig.add_trace(
    go.Scatter(x=estado_stats['Num_Clientes'], y=estado_stats['Renda_Media'],
              mode='markers+text', text=estado_stats['Estado'],
              textposition='top center',
              marker=dict(size=15, color='rgb(255, 127, 14)'),
              name='Estados'),
    row=2, col=2
)

fig.update_layout(height=900, showlegend=False, title_text="🗺️ Análise Geográfica dos Clientes")
fig.write_html('analise_localizacao.html')
print("\n✓ Gráfico salvo: analise_localizacao.html")

# ============================================================================
# 7. ANÁLISE DE CORRELAÇÃO
# ============================================================================
print("\n" + "="*80)
print("🔗 ANÁLISE DE CORRELAÇÃO")
print("="*80)

correlation_vars = ['Idade', 'Renda_Anual', 'Numero_Cartoes', 
                    'Possui_Conta_Adicional_Bin', 'Tempo_Cliente_Anos']
corr_matrix = df[correlation_vars].corr()

print("\n🔍 Principais Correlações:")
corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        corr_pairs.append((
            corr_matrix.columns[i],
            corr_matrix.columns[j],
            corr_matrix.iloc[i, j]
        ))
corr_pairs_sorted = sorted(corr_pairs, key=lambda x: abs(x[2]), reverse=True)
for var1, var2, corr in corr_pairs_sorted[:5]:
    print(f"  • {var1} <-> {var2}: {corr:.3f}")

# Visualização
fig = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    colorscale='RdBu',
    zmid=0,
    text=corr_matrix.values.round(2),
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title="Correlação")
))

fig.update_layout(
    title='🔗 Matriz de Correlação entre Variáveis',
    height=600,
    xaxis_title='',
    yaxis_title=''
)
fig.write_html('analise_correlacao.html')
print("\n✓ Gráfico salvo: analise_correlacao.html")

# ============================================================================
# 8. SEGMENTAÇÃO - K-MEANS CLUSTERING
# ============================================================================
print("\n" + "="*80)
print("🎯 SEGMENTAÇÃO DE CLIENTES - K-MEANS CLUSTERING")
print("="*80)

# Preparar dados para clustering
df_cluster = df[['Idade', 'Renda_Anual', 'Numero_Cartoes', 
                 'Possui_Conta_Adicional_Bin', 'Tempo_Cliente_Anos']].dropna()

print(f"\n📊 Clientes com dados completos para clustering: {len(df_cluster):,}")

# Padronizar os dados
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_cluster)

# Método do cotovelo
print("\n🔍 Determinando número ótimo de clusters...")
inertias = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df_scaled)
    inertias.append(kmeans.inertia_)

# Plotar método do cotovelo
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(K_range),
    y=inertias,
    mode='lines+markers',
    marker=dict(size=10, color='rgb(55, 83, 109)'),
    line=dict(color='rgb(55, 83, 109)', width=2)
))

fig.update_layout(
    title='📈 Método do Cotovelo - Determinação do Número Ótimo de Clusters',
    xaxis_title='Número de Clusters',
    yaxis_title='Inércia (Within-Cluster Sum of Squares)',
    height=500
)
fig.write_html('metodo_cotovelo.html')
print("✓ Gráfico salvo: metodo_cotovelo.html")

# Aplicar K-Means com 5 clusters
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
df_cluster['Segmento'] = kmeans.fit_predict(df_scaled)

# Adicionar segmentos ao dataframe original
df_with_segments = df.copy()
df_with_segments.loc[df_cluster.index, 'Segmento'] = df_cluster['Segmento']

print(f"\n✓ Segmentação concluída! {n_clusters} segmentos identificados.")
print(f"\n📊 Distribuição de Clientes por Segmento:")
segment_dist = df_cluster['Segmento'].value_counts().sort_index()
for seg, count in segment_dist.items():
    pct = (count / len(df_cluster)) * 100
    print(f"  • Segmento {seg}: {count:,} clientes ({pct:.1f}%)")

# ============================================================================
# 9. VISUALIZAÇÃO DOS SEGMENTOS
# ============================================================================
print("\n" + "="*80)
print("📊 VISUALIZAÇÃO DOS SEGMENTOS")
print("="*80)

# PCA para visualização 2D
pca = PCA(n_components=2)
df_pca = pca.fit_transform(df_scaled)
df_cluster['PCA1'] = df_pca[:, 0]
df_cluster['PCA2'] = df_pca[:, 1]

fig = px.scatter(
    df_cluster,
    x='PCA1',
    y='PCA2',
    color='Segmento',
    title='🎯 Visualização dos Segmentos (PCA 2D)',
    labels={'PCA1': f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variância)',
            'PCA2': f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variância)'},
    color_continuous_scale='Viridis',
    height=600
)
fig.update_traces(marker=dict(size=8, opacity=0.7))
fig.write_html('segmentos_pca_2d.html')
print("\n✓ Gráfico salvo: segmentos_pca_2d.html")

# Visualização 3D
fig = px.scatter_3d(
    df_cluster,
    x='Idade',
    y='Renda_Anual',
    z='Numero_Cartoes',
    color='Segmento',
    title='🎯 Visualização 3D dos Segmentos (Idade x Renda x Cartões)',
    color_continuous_scale='Plasma',
    height=700,
    opacity=0.7
)
fig.update_traces(marker=dict(size=5))
fig.write_html('segmentos_3d.html')
print("✓ Gráfico salvo: segmentos_3d.html")

# ============================================================================
# 10. PERFIL DETALHADO DOS SEGMENTOS
# ============================================================================
print("\n" + "="*80)
print("📋 PERFIL DETALHADO DOS SEGMENTOS")
print("="*80)

segment_profile = df_cluster.groupby('Segmento').agg({
    'Idade': ['mean', 'std'],
    'Renda_Anual': ['mean', 'std'],
    'Numero_Cartoes': ['mean'],
    'Possui_Conta_Adicional_Bin': 'mean',
    'Tempo_Cliente_Anos': 'mean'
}).round(2)

segment_profile.columns = ['Idade_Média', 'Idade_Desvio', 'Renda_Média', 'Renda_Desvio',
                           'Cartões_Média', 'Pct_Conta_Adicional', 'Tempo_Médio_Anos']

segment_profile['Num_Clientes'] = df_cluster['Segmento'].value_counts().sort_index()
segment_profile['Pct_Total'] = (segment_profile['Num_Clientes'] / len(df_cluster) * 100).round(1)

print("\n" + segment_profile.to_string())

print("\n\n🎯 CARACTERIZAÇÃO DOS SEGMENTOS:\n")

for seg in sorted(df_cluster['Segmento'].unique()):
    seg_data = segment_profile.loc[seg]
    
    print(f"\n{'='*80}")
    print(f"SEGMENTO {seg}")
    print(f"{'='*80}")
    print(f"👥 Tamanho: {seg_data['Num_Clientes']:,.0f} clientes ({seg_data['Pct_Total']:.1f}% do total)")
    print(f"\n📊 Perfil Demográfico:")
    print(f"   • Idade Média: {seg_data['Idade_Média']:.0f} anos (± {seg_data['Idade_Desvio']:.1f})")
    print(f"   • Renda Média: R$ {seg_data['Renda_Média']:,.2f} (± R$ {seg_data['Renda_Desvio']:,.2f})")
    print(f"   • Cartões por Cliente: {seg_data['Cartões_Média']:.1f} em média")
    print(f"   • Conta Adicional: {seg_data['Pct_Conta_Adicional']*100:.1f}% possuem")
    print(f"   • Tempo Médio como Cliente: {seg_data['Tempo_Médio_Anos']:.1f} anos")
    
    seg_geo = df_with_segments[df_with_segments['Segmento'] == seg]
    top_estado = seg_geo['Estado'].mode()[0] if len(seg_geo) > 0 else 'N/A'
    top_cidade = seg_geo['Cidade'].mode()[0] if len(seg_geo) > 0 else 'N/A'
    print(f"\n🗺️ Localização:")
    print(f"   • Estado predominante: {top_estado}")
    print(f"   • Cidade predominante: {top_cidade}")

# ============================================================================
# 11. SUMÁRIO EXECUTIVO
# ============================================================================
print("\n\n" + "="*80)
print("🎯 SUMÁRIO EXECUTIVO - SEGMENTAÇÃO DE CLIENTES PRICELESS BANK")
print("="*80)

print(f"\n📊 VISÃO GERAL:")
print(f"   • Total de Clientes Analisados: {len(df_cluster):,}")
print(f"   • Número de Segmentos Identificados: {n_clusters}")
print(f"   • Taxa de Dados Completos: {(len(df_cluster)/len(df)*100):.1f}%")

print(f"\n💼 PRINCIPAIS ACHADOS:")
seg_maior_renda = segment_profile['Renda_Média'].idxmax()
print(f"   • Segmento de Maior Renda: Segmento {seg_maior_renda} (R$ {segment_profile.loc[seg_maior_renda, 'Renda_Média']:,.2f})")

seg_maior_base = segment_profile['Num_Clientes'].idxmax()
print(f"   • Segmento com Maior Base: Segmento {seg_maior_base} ({segment_profile.loc[seg_maior_base, 'Num_Clientes']:,.0f} clientes)")

seg_mais_jovem = segment_profile['Idade_Média'].idxmin()
print(f"   • Segmento Mais Jovem: Segmento {seg_mais_jovem} ({segment_profile.loc[seg_mais_jovem, 'Idade_Média']:.0f} anos)")

seg_mais_cartoes = segment_profile['Cartões_Média'].idxmax()
print(f"   • Segmento com Mais Cartões: Segmento {seg_mais_cartoes} ({segment_profile.loc[seg_mais_cartoes, 'Cartões_Média']:.1f} cartões/cliente)")

print(f"\n🎯 OPORTUNIDADES IDENTIFICADAS:")
print(f"   1. Cross-sell de cartões para segmentos com baixa penetração")
print(f"   2. Programas de retenção para segmentos com menor tempo médio")
print(f"   3. Produtos premium para segmentos de alta renda")
print(f"   4. Ofertas regionalizadas baseadas na concentração geográfica")
print(f"   5. Estratégias digitais para segmentos mais jovens")

# ============================================================================
# 12. EXPORTAR RESULTADOS
# ============================================================================
print("\n" + "="*80)
print("💾 EXPORTANDO RESULTADOS")
print("="*80)

output_file = 'clientes_segmentados.csv'
df_with_segments.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✓ Arquivo exportado: {output_file}")

profile_file = 'perfil_segmentos.csv'
segment_profile.to_csv(profile_file, encoding='utf-8-sig')
print(f"✓ Perfil dos segmentos exportado: {profile_file}")

print("\n" + "="*80)
print("✅ ANÁLISE COMPLETA!")
print("="*80)
print("\n📂 Arquivos gerados:")
print("   • analise_idade.html")
print("   • analise_renda.html")
print("   • analise_localizacao.html")
print("   • analise_correlacao.html")
print("   • metodo_cotovelo.html")
print("   • segmentos_pca_2d.html")
print("   • segmentos_3d.html")
print("   • clientes_segmentados.csv")
print("   • perfil_segmentos.csv")
print("\n🌐 Abra os arquivos .html no navegador para visualizar os gráficos interativos!")
print("="*80)
