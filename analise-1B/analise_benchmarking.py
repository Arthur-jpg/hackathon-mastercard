import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configurações de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Dados de benchmarking dos bancos competidores
bancos_data = {
    'Banco': ['Priceless Bank', 'LuminaPay', 'Papaya Bank', 'Aurora Bank', 'Lux Bank'],
    'Perfil': [
        'Banco tradicional em transição',
        'Nativo digital, poucos anos de atuação',
        'Banco tradicional, bem consolidado no mercado',
        'Nativo digital, com foco em investimentos',
        'Banco Affluent, com clientes selecionados'
    ],
    'Tipo': ['Tradicional', 'Digital', 'Tradicional', 'Digital', 'Affluent'],
    'Maturidade': ['Estabelecido', 'Jovem', 'Consolidado', 'Jovem', 'Estabelecido'],
    
    # Público-alvo (escala numérica para visualização)
    'Idade_Target': [40, 25, 55, 28, 45],  # Idade média do target
    'Renda_Target': [3, 1, 2, 5, 5],  # 1=baixa, 5=muito alta
    
    # Diferenciais (pontuação de 0-10)
    'Score_Digital': [5, 9, 4, 8, 6],
    'Score_Cashback': [6, 8, 5, 4, 3],
    'Score_Pontos': [7, 3, 9, 2, 4],
    'Score_Investimentos': [4, 2, 6, 10, 8],
    'Score_Exclusividade': [5, 3, 6, 7, 10],
}

# Categorias de gastos (normalizado)
gastos_data = {
    'Banco': ['Priceless Bank', 'LuminaPay', 'Papaya Bank', 'Aurora Bank', 'Lux Bank'],
    'Restaurantes': [25, 40, 15, 35, 30],
    'Mercados': [30, 35, 30, 10, 5],
    'Transporte': [20, 25, 10, 5, 2],
    'Automotivo': [10, 0, 25, 25, 20],
    'Saúde': [8, 0, 20, 5, 8],
    'Lazer': [5, 0, 0, 15, 10],
    'Viagem': [2, 0, 0, 5, 25],
}

df_bancos = pd.DataFrame(bancos_data)
df_gastos = pd.DataFrame(gastos_data)

# ============================================================================
# GRÁFICO 1: Matriz de Posicionamento (Digital vs Renda)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
sizes = [300, 250, 350, 280, 300]

for i, (idx, row) in enumerate(df_bancos.iterrows()):
    ax.scatter(row['Score_Digital'], row['Renda_Target'], 
              s=sizes[i], c=colors[i], alpha=0.6, edgecolors='black', linewidth=2)
    
    # Adicionar labels
    offset_x = 0.3 if row['Banco'] != 'Papaya Bank' else -0.5
    offset_y = 0.15
    ax.annotate(row['Banco'], 
               (row['Score_Digital'], row['Renda_Target']),
               xytext=(offset_x, offset_y), 
               textcoords='offset points',
               fontsize=11, 
               fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i], alpha=0.3))

ax.axvline(x=df_bancos['Score_Digital'][0], color='red', linestyle='--', linewidth=2, alpha=0.5, label='Priceless Bank (Digital)')
ax.axhline(y=df_bancos['Renda_Target'][0], color='red', linestyle='--', linewidth=2, alpha=0.5, label='Priceless Bank (Renda)')

ax.set_xlabel('Score Digital (0-10)', fontsize=13, fontweight='bold')
ax.set_ylabel('Nível de Renda do Target (1-5)', fontsize=13, fontweight='bold')
ax.set_title('Posicionamento Competitivo: Digitalização vs Público-Alvo\n(Priceless Bank em relação aos competidores)', 
            fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper left', fontsize=10)

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_1_posicionamento.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 1 criado: Posicionamento Competitivo")

# ============================================================================
# GRÁFICO 2: Radar Chart - Diferenciais
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

categories = ['Digital', 'Cashback', 'Pontos', 'Investimentos', 'Exclusividade']
N = len(categories)

angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# Plot para cada banco
for i, (idx, row) in enumerate(df_bancos.iterrows()):
    values = [row['Score_Digital'], row['Score_Cashback'], row['Score_Pontos'], 
              row['Score_Investimentos'], row['Score_Exclusividade']]
    values += values[:1]
    
    linewidth = 3 if row['Banco'] == 'Priceless Bank' else 1.5
    alpha = 0.7 if row['Banco'] == 'Priceless Bank' else 0.3
    
    ax.plot(angles, values, 'o-', linewidth=linewidth, label=row['Banco'], 
            color=colors[i], alpha=alpha)
    ax.fill(angles, values, alpha=0.15 if row['Banco'] == 'Priceless Bank' else 0.05, 
            color=colors[i])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=12, fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], size=10)
ax.set_title('Comparação de Diferenciais Competitivos\n(Priceless Bank em destaque)', 
            size=15, fontweight='bold', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
ax.grid(True)

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_diferenciais.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2 criado: Diferenciais Competitivos (Radar)")

# ============================================================================
# GRÁFICO 3: Comparação de Diferenciais (Barras Agrupadas)
# ============================================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Análise Detalhada de Diferenciais por Banco\n(Comparação com Priceless Bank)', 
            fontsize=16, fontweight='bold', y=1.02)

diferenciais = ['Score_Digital', 'Score_Cashback', 'Score_Pontos', 'Score_Investimentos', 'Score_Exclusividade']
titulos = ['Nível de Digitalização', 'Programa de Cashback', 'Programa de Pontos', 'Produtos de Investimentos', 'Exclusividade/VIP']

for idx, (diferencial, titulo) in enumerate(zip(diferenciais, titulos)):
    ax = axes[idx // 3, idx % 3]
    
    values = df_bancos[diferencial].values
    bars = ax.bar(df_bancos['Banco'], values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Destacar Priceless Bank
    bars[0].set_color('#FF6B6B')
    bars[0].set_alpha(1.0)
    bars[0].set_linewidth(3)
    
    # Adicionar linha de referência do Priceless Bank
    priceless_value = df_bancos[diferencial].iloc[0]
    ax.axhline(y=priceless_value, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Priceless Bank')
    
    # Adicionar valores nas barras
    for i, bar in enumerate(bars):
        height = bar.get_height()
        diff = height - priceless_value if i > 0 else 0
        label = f'{height:.1f}'
        if i > 0:
            label += f'\n({diff:+.1f})'
        ax.text(bar.get_x() + bar.get_width()/2., height,
               label, ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Score (0-10)', fontsize=10, fontweight='bold')
    ax.set_title(titulo, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_xticklabels(df_bancos['Banco'], rotation=45, ha='right', fontsize=9)

# Remover o último subplot (vazio)
axes[1, 2].axis('off')

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_3_barras_diferenciais.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 3 criado: Comparação Detalhada de Diferenciais")

# ============================================================================
# GRÁFICO 4: Perfil de Gastos por Categoria
# ============================================================================
fig, ax = plt.subplots(figsize=(14, 8))

x = np.arange(len(df_gastos['Banco']))
width = 0.12

categorias_gastos = ['Restaurantes', 'Mercados', 'Transporte', 'Automotivo', 'Saúde', 'Lazer', 'Viagem']
cores_gastos = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']

for i, categoria in enumerate(categorias_gastos):
    offset = width * (i - 3)
    bars = ax.bar(x + offset, df_gastos[categoria], width, label=categoria, color=cores_gastos[i], alpha=0.8)

ax.set_xlabel('Bancos', fontsize=13, fontweight='bold')
ax.set_ylabel('Proporção de Gastos (%)', fontsize=13, fontweight='bold')
ax.set_title('Comparação de Perfil de Gastos por Categoria\n(Principais categorias de cada banco)', 
            fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(df_gastos['Banco'], fontsize=11, fontweight='bold')
ax.legend(loc='upper right', fontsize=10, ncol=2)
ax.grid(True, alpha=0.3, axis='y')

# Destacar Priceless Bank com uma linha vertical
ax.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_4_perfil_gastos.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 4 criado: Perfil de Gastos por Categoria")

# ============================================================================
# GRÁFICO 5: Heatmap de Comparação
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

# Preparar dados para heatmap
heatmap_data = df_bancos[['Score_Digital', 'Score_Cashback', 'Score_Pontos', 
                           'Score_Investimentos', 'Score_Exclusividade']].T

# Criar heatmap
im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=10)

# Configurar ticks
ax.set_xticks(np.arange(len(df_bancos['Banco'])))
ax.set_yticks(np.arange(len(categories)))
ax.set_xticklabels(df_bancos['Banco'], fontsize=11, fontweight='bold')
ax.set_yticklabels(categories, fontsize=11, fontweight='bold')

# Rotacionar labels
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Adicionar valores no heatmap
for i in range(len(categories)):
    for j in range(len(df_bancos['Banco'])):
        text = ax.text(j, i, f'{heatmap_data.iloc[i, j]:.1f}',
                      ha="center", va="center", color="black", fontweight='bold', fontsize=10)

# Destacar coluna Priceless Bank
ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, len(categories), fill=False, edgecolor='red', linewidth=4))

ax.set_title('Matriz de Comparação: Scores de Diferenciais\n(Priceless Bank destacado em vermelho)', 
            fontsize=15, fontweight='bold', pad=20)

# Adicionar colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Score (0-10)', rotation=270, labelpad=20, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_5_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 5 criado: Matriz de Comparação (Heatmap)")

# ============================================================================
# GRÁFICO 6: Análise de Público-Alvo
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Subplot 1: Idade do Target
ax1 = axes[0]
bars1 = ax1.barh(df_bancos['Banco'], df_bancos['Idade_Target'], color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
bars1[0].set_color('#FF6B6B')
bars1[0].set_alpha(1.0)
bars1[0].set_linewidth(3)

ax1.axvline(x=df_bancos['Idade_Target'].iloc[0], color='red', linestyle='--', linewidth=2, alpha=0.5, label='Priceless Bank')

for i, bar in enumerate(bars1):
    width = bar.get_width()
    diff = width - df_bancos['Idade_Target'].iloc[0] if i > 0 else 0
    label = f'{width:.0f} anos'
    if i > 0:
        label += f' ({diff:+.0f})'
    ax1.text(width, bar.get_y() + bar.get_height()/2.,
           label, ha='left', va='center', fontsize=10, fontweight='bold', style='italic')

ax1.set_xlabel('Idade Média do Público-Alvo', fontsize=12, fontweight='bold')
ax1.set_title('Faixa Etária do Público-Alvo', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')
ax1.legend()

# Subplot 2: Nível de Renda
ax2 = axes[1]
bars2 = ax2.barh(df_bancos['Banco'], df_bancos['Renda_Target'], color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
bars2[0].set_color('#FF6B6B')
bars2[0].set_alpha(1.0)
bars2[0].set_linewidth(3)

ax2.axvline(x=df_bancos['Renda_Target'].iloc[0], color='red', linestyle='--', linewidth=2, alpha=0.5, label='Priceless Bank')

renda_labels = ['Baixa', 'Média-Baixa', 'Média', 'Média-Alta', 'Alta']
for i, bar in enumerate(bars2):
    width = bar.get_width()
    diff = width - df_bancos['Renda_Target'].iloc[0] if i > 0 else 0
    label = f'{renda_labels[int(width)-1]}'
    if i > 0:
        label += f' ({diff:+.0f})'
    ax2.text(width, bar.get_y() + bar.get_height()/2.,
           label, ha='left', va='center', fontsize=10, fontweight='bold', style='italic')

ax2.set_xlabel('Nível de Renda do Target (1-5)', fontsize=12, fontweight='bold')
ax2.set_title('Perfil de Renda do Público-Alvo', fontsize=13, fontweight='bold')
ax2.set_xticks([1, 2, 3, 4, 5])
ax2.set_xticklabels(renda_labels, rotation=45, ha='right')
ax2.grid(True, alpha=0.3, axis='x')
ax2.legend()

plt.suptitle('Análise Comparativa de Público-Alvo\n(Priceless Bank vs Competidores)', 
            fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_6_publico_alvo.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 6 criado: Análise de Público-Alvo")

# ============================================================================
# RESUMO EXECUTIVO
# ============================================================================
print("\n" + "="*80)
print("RESUMO EXECUTIVO - POSICIONAMENTO PRICELESS BANK")
print("="*80)

print("\n📊 POSIÇÃO ATUAL DO PRICELESS BANK:")
print(f"  • Perfil: {df_bancos['Perfil'].iloc[0]}")
print(f"  • Score Digital: {df_bancos['Score_Digital'].iloc[0]}/10 (Intermediário)")
print(f"  • Público-Alvo: Idade {df_bancos['Idade_Target'].iloc[0]} anos, Renda {renda_labels[df_bancos['Renda_Target'].iloc[0]-1]}")

print("\n🎯 PRINCIPAIS COMPETIDORES:")
for i in range(1, len(df_bancos)):
    print(f"\n  {i}. {df_bancos['Banco'].iloc[i]}")
    print(f"     Perfil: {df_bancos['Perfil'].iloc[i]}")
    print(f"     Destaque: ", end="")
    scores = [df_bancos['Score_Digital'].iloc[i], df_bancos['Score_Cashback'].iloc[i],
              df_bancos['Score_Pontos'].iloc[i], df_bancos['Score_Investimentos'].iloc[i],
              df_bancos['Score_Exclusividade'].iloc[i]]
    max_idx = scores.index(max(scores))
    print(categories[max_idx])

print("\n💡 PONTOS FORTES DO PRICELESS BANK:")
scores_pb = [df_bancos['Score_Digital'].iloc[0], df_bancos['Score_Cashback'].iloc[0],
             df_bancos['Score_Pontos'].iloc[0], df_bancos['Score_Investimentos'].iloc[0],
             df_bancos['Score_Exclusividade'].iloc[0]]
for i, (cat, score) in enumerate(zip(categories, scores_pb)):
    if score >= 6:
        print(f"  ✓ {cat}: {score}/10")

print("\n⚠️  ÁREAS DE MELHORIA:")
for i, (cat, score) in enumerate(zip(categories, scores_pb)):
    if score < 6:
        competidores_melhores = [df_bancos['Banco'].iloc[j] for j in range(1, len(df_bancos))
                                  if [df_bancos['Score_Digital'].iloc[j], df_bancos['Score_Cashback'].iloc[j],
                                      df_bancos['Score_Pontos'].iloc[j], df_bancos['Score_Investimentos'].iloc[j],
                                      df_bancos['Score_Exclusividade'].iloc[j]][i] > score]
        print(f"  ⚠ {cat}: {score}/10 (Atrás de: {', '.join(competidores_melhores)})")

print("\n" + "="*80)
print("✅ Análise completa! 6 gráficos salvos no diretório do projeto.")
print("="*80)
