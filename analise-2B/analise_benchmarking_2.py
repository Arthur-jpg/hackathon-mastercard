import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configurações de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Dados de benchmarking operacional dos bancos competidores
bancos_data_2 = {
    'Banco': ['Priceless Bank', 'LuminaPay', 'Papaya Bank', 'Aurora Bank', 'Lux Bank'],
    
    # Maturidade Digital
    'Maturidade_Digital': ['Média', 'Alta', 'Baixa', 'Média', 'Baixa'],
    'Maturidade_Digital_Score': [5, 9, 3, 6, 3],  # Score numérico para visualização
    
    # Canal de Abertura
    'Canal_Digital': [50, 100, 50, 100, 0],  # % de abertura digital
    'Canal_Fisico': [50, 0, 50, 0, 100],     # % de abertura física
    
    # Banco Principal
    'Percentual_Banco_Principal': [0, 37.4, 42.7, 13.6, 6.4],  # Priceless Bank precisa ser estimado
    
    # Open Finance
    'Aceita_Open_Finance': ['?', 'Sim', 'Sim', 'Sim', 'Não'],
    'Open_Finance_Binary': [0.5, 1, 1, 1, 0],  # Para visualização
    'Percentual_Exportacao_Open_Finance': [0, 62, 44, 79, 82],  # Priceless Bank a definir
    
    # NPS
    'NPS': [0, 76, 64, 55, 82],  # Priceless Bank a definir
}

df_bancos_2 = pd.DataFrame(bancos_data_2)

# Cores consistentes
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

# ============================================================================
# GRÁFICO 1: Comparação de Maturidade Digital
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

y_pos = np.arange(len(df_bancos_2['Banco']))
bars = ax.barh(y_pos, df_bancos_2['Maturidade_Digital_Score'], color=colors, alpha=0.7, edgecolor='black', linewidth=2)

# Destacar Priceless Bank
bars[0].set_color('#FF6B6B')
bars[0].set_alpha(1.0)
bars[0].set_linewidth(3)

# Adicionar labels nas barras
for i, (bar, label) in enumerate(zip(bars, df_bancos_2['Maturidade_Digital'])):
    width = bar.get_width()
    ax.text(width + 0.2, bar.get_y() + bar.get_height()/2.,
           f'{label} ({width:.0f}/10)', ha='left', va='center', fontsize=11, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(df_bancos_2['Banco'], fontsize=12, fontweight='bold')
ax.set_xlabel('Score de Maturidade Digital (0-10)', fontsize=13, fontweight='bold')
ax.set_title('Comparação de Maturidade Digital\n(Alta = Banco nativo digital com tecnologia avançada)', 
            fontsize=15, fontweight='bold', pad=20)
ax.set_xlim(0, 11)
ax.grid(True, alpha=0.3, axis='x')

# Linha de referência
ax.axvline(x=df_bancos_2['Maturidade_Digital_Score'].iloc[0], color='red', linestyle='--', linewidth=2, alpha=0.5)

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_1_maturidade_digital.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.1 criado: Maturidade Digital")

# ============================================================================
# GRÁFICO 2: Canais de Abertura de Conta
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

x = np.arange(len(df_bancos_2['Banco']))
width = 0.35

bars1 = ax.bar(x - width/2, df_bancos_2['Canal_Digital'], width, label='Digital', 
              color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, df_bancos_2['Canal_Fisico'], width, label='Físico (Agência)', 
              color='#FFA07A', alpha=0.8, edgecolor='black', linewidth=1.5)

# Destacar Priceless Bank
bars1[0].set_color('#FF6B6B')
bars1[0].set_alpha(1.0)
bars1[0].set_linewidth(3)
bars2[0].set_color('#FF6B6B')
bars2[0].set_alpha(0.5)
bars2[0].set_linewidth(3)

# Adicionar valores nas barras
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   f'{height:.0f}%', ha='center', va='center', 
                   fontsize=11, fontweight='bold', color='white')

ax.set_ylabel('Percentual de Atendimento (%)', fontsize=13, fontweight='bold')
ax.set_title('Canais de Abertura de Conta e Atendimento\n(Distribuição entre canais digitais e físicos)', 
            fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(df_bancos_2['Banco'], fontsize=11, fontweight='bold')
ax.legend(fontsize=12, loc='upper right')
ax.set_ylim(0, 120)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_2_canais_abertura.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.2 criado: Canais de Abertura de Conta")

# ============================================================================
# GRÁFICO 3: Percentual de Clientes que Consideram Banco como Principal
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Remover Priceless Bank desta análise (valor = 0)
df_temp = df_bancos_2[df_bancos_2['Percentual_Banco_Principal'] > 0].copy()
colors_temp = [colors[i] for i in range(1, len(colors))]

bars = ax.bar(df_temp['Banco'], df_temp['Percentual_Banco_Principal'], 
             color=colors_temp, alpha=0.7, edgecolor='black', linewidth=2)

# Adicionar valores nas barras
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Percentual de Clientes (%)', fontsize=13, fontweight='bold')
ax.set_title('Clientes que Consideram o Banco como Principal\n(Maior percentual = Maior fidelização e engajamento)', 
            fontsize=15, fontweight='bold', pad=20)
ax.set_ylim(0, 50)
ax.grid(True, alpha=0.3, axis='y')

# Adicionar texto informativo
ax.text(0.5, 0.95, 'Nota: Priceless Bank não possui dados disponíveis', 
       transform=ax.transAxes, ha='center', va='top',
       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3), fontsize=10, style='italic')

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_3_banco_principal.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.3 criado: Banco Principal")

# ============================================================================
# GRÁFICO 4: Open Finance - Adoção e Uso
# ============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Subplot 1: Aceita Open Finance
aceita_labels = ['?', 'Sim', 'Sim', 'Sim', 'Não']
aceita_colors = ['gray' if label == '?' else '#2ECC71' if label == 'Sim' else '#E74C3C' 
                for label in aceita_labels]

bars1 = ax1.barh(df_bancos_2['Banco'], [1]*len(df_bancos_2), color=aceita_colors, alpha=0.7, edgecolor='black', linewidth=2)

# Destacar Priceless Bank
bars1[0].set_linewidth(3)

for i, (bar, label) in enumerate(zip(bars1, aceita_labels)):
    ax1.text(0.5, bar.get_y() + bar.get_height()/2., label,
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')

ax1.set_xlim(0, 1.2)
ax1.set_title('Aceita Open Finance?', fontsize=13, fontweight='bold')
ax1.set_xlabel('')
ax1.set_xticks([])
ax1.grid(False)

# Subplot 2: Percentual de Exportação
df_temp2 = df_bancos_2[df_bancos_2['Percentual_Exportacao_Open_Finance'] > 0].copy()
colors_temp2 = [colors[i] for i, perc in enumerate(df_bancos_2['Percentual_Exportacao_Open_Finance']) if perc > 0]

bars2 = ax2.barh(df_temp2['Banco'], df_temp2['Percentual_Exportacao_Open_Finance'], 
                color=colors_temp2, alpha=0.7, edgecolor='black', linewidth=2)

for bar in bars2:
    width = bar.get_width()
    ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
            f'{width:.0f}%', ha='left', va='center', fontsize=11, fontweight='bold')

ax2.set_xlabel('Percentual de Clientes (%)', fontsize=12, fontweight='bold')
ax2.set_title('% de Clientes que Exportaram Dados via Open Finance', fontsize=13, fontweight='bold')
ax2.set_xlim(0, 90)
ax2.grid(True, alpha=0.3, axis='x')

# Adicionar texto informativo
ax2.text(0.5, 0.05, 'Priceless Bank: Dados não disponíveis', 
        transform=ax2.transAxes, ha='center', va='bottom',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3), fontsize=9, style='italic')

plt.suptitle('Análise de Open Finance\n(Adoção da tecnologia e uso pelos clientes)', 
            fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_4_open_finance.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.4 criado: Open Finance")

# ============================================================================
# GRÁFICO 5: Net Promoter Score (NPS)
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Remover Priceless Bank desta análise (valor = 0)
df_temp3 = df_bancos_2[df_bancos_2['NPS'] > 0].copy()
colors_temp3 = [colors[i] for i in range(1, len(colors))]

bars = ax.bar(df_temp3['Banco'], df_temp3['NPS'], color=colors_temp3, alpha=0.7, edgecolor='black', linewidth=2)

# Colorir barras baseado no NPS (verde > 70, amarelo 50-70, vermelho < 50)
for i, bar in enumerate(bars):
    nps_value = df_temp3['NPS'].iloc[i]
    if nps_value >= 70:
        bar.set_color('#2ECC71')
    elif nps_value >= 50:
        bar.set_color('#F39C12')
    else:
        bar.set_color('#E74C3C')

# Adicionar valores nas barras
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{height:.0f}', ha='center', va='bottom', fontsize=13, fontweight='bold')

# Adicionar zonas de NPS
ax.axhspan(0, 50, alpha=0.1, color='red', label='Detratores dominantes')
ax.axhspan(50, 70, alpha=0.1, color='yellow', label='Zona neutra')
ax.axhspan(70, 100, alpha=0.1, color='green', label='Promotores dominantes')

ax.set_ylabel('NPS Score', fontsize=13, fontweight='bold')
ax.set_title('Net Promoter Score (NPS)\n(Métrica de satisfação e lealdade do cliente)', 
            fontsize=15, fontweight='bold', pad=20)
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3, axis='y')
ax.legend(loc='lower right', fontsize=10)

# Adicionar texto informativo
ax.text(0.5, 0.95, 'Nota: Priceless Bank não possui dados disponíveis', 
       transform=ax.transAxes, ha='center', va='top',
       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3), fontsize=10, style='italic')

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_5_nps.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.5 criado: NPS")

# ============================================================================
# GRÁFICO 6: Dashboard Comparativo Geral
# ============================================================================
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Mini-gráfico 1: Maturidade Digital (Pizza)
ax1 = fig.add_subplot(gs[0, 0])
maturidade_counts = df_bancos_2['Maturidade_Digital'].value_counts()
colors_pizza = ['#2ECC71', '#F39C12', '#E74C3C']
ax1.pie(maturidade_counts.values, labels=maturidade_counts.index, autopct='%1.0f%%',
       colors=colors_pizza, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('Distribuição de Maturidade Digital', fontsize=12, fontweight='bold')

# Mini-gráfico 2: Canais de Abertura (Pizza)
ax2 = fig.add_subplot(gs[0, 1])
canal_totals = [df_bancos_2['Canal_Digital'].sum(), df_bancos_2['Canal_Fisico'].sum()]
ax2.pie(canal_totals, labels=['Digital', 'Físico'], autopct='%1.0f%%',
       colors=['#4ECDC4', '#FFA07A'], startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax2.set_title('Distribuição Total de Canais\n(Soma de todos os bancos)', fontsize=12, fontweight='bold')

# Mini-gráfico 3: Banco Principal (Barras Horizontais)
ax3 = fig.add_subplot(gs[1, :])
df_principal = df_bancos_2[df_bancos_2['Percentual_Banco_Principal'] > 0].copy()
df_principal = df_principal.sort_values('Percentual_Banco_Principal', ascending=True)
colors_principal = ['#4ECDC4', '#FFA07A', '#98D8C8', '#45B7D1']
bars = ax3.barh(df_principal['Banco'], df_principal['Percentual_Banco_Principal'], 
               color=colors_principal, alpha=0.7, edgecolor='black', linewidth=1.5)
for bar in bars:
    width = bar.get_width()
    ax3.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
            f'{width:.1f}%', ha='left', va='center', fontsize=10, fontweight='bold')
ax3.set_xlabel('Percentual (%)', fontsize=11, fontweight='bold')
ax3.set_title('Clientes que Consideram Banco como Principal', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# Mini-gráfico 4: NPS Comparativo
ax4 = fig.add_subplot(gs[2, 0])
df_nps = df_bancos_2[df_bancos_2['NPS'] > 0].copy()
df_nps = df_nps.sort_values('NPS', ascending=True)
colors_nps = ['#E74C3C' if nps < 50 else '#F39C12' if nps < 70 else '#2ECC71' 
             for nps in df_nps['NPS']]
bars = ax4.barh(df_nps['Banco'], df_nps['NPS'], color=colors_nps, alpha=0.7, edgecolor='black', linewidth=1.5)
for bar in bars:
    width = bar.get_width()
    ax4.text(width + 1, bar.get_y() + bar.get_height()/2.,
            f'{width:.0f}', ha='left', va='center', fontsize=10, fontweight='bold')
ax4.set_xlabel('NPS Score', fontsize=11, fontweight='bold')
ax4.set_title('Net Promoter Score', fontsize=12, fontweight='bold')
ax4.set_xlim(0, 90)
ax4.grid(True, alpha=0.3, axis='x')

# Mini-gráfico 5: Open Finance
ax5 = fig.add_subplot(gs[2, 1])
df_of = df_bancos_2[df_bancos_2['Percentual_Exportacao_Open_Finance'] > 0].copy()
df_of = df_of.sort_values('Percentual_Exportacao_Open_Finance', ascending=True)
bars = ax5.barh(df_of['Banco'], df_of['Percentual_Exportacao_Open_Finance'], 
               color=['#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'], alpha=0.7, edgecolor='black', linewidth=1.5)
for bar in bars:
    width = bar.get_width()
    ax5.text(width + 1, bar.get_y() + bar.get_height()/2.,
            f'{width:.0f}%', ha='left', va='center', fontsize=10, fontweight='bold')
ax5.set_xlabel('% de Exportação', fontsize=11, fontweight='bold')
ax5.set_title('Uso de Open Finance pelos Clientes', fontsize=12, fontweight='bold')
ax5.set_xlim(0, 90)
ax5.grid(True, alpha=0.3, axis='x')

plt.suptitle('Dashboard Comparativo: Métricas Operacionais e de Satisfação\n(Priceless Bank vs Competidores)', 
            fontsize=16, fontweight='bold', y=0.995)
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_6_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.6 criado: Dashboard Comparativo")

# ============================================================================
# GRÁFICO 7: Análise de Correlação entre Métricas
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

# Criar scatter plot: Maturidade Digital vs NPS
df_scatter = df_bancos_2[(df_bancos_2['NPS'] > 0)].copy()

for i, row in df_scatter.iterrows():
    if row['Banco'] == 'Priceless Bank':
        continue
    ax.scatter(row['Maturidade_Digital_Score'], row['NPS'], 
              s=row['Percentual_Banco_Principal']*30,  # Tamanho proporcional ao % banco principal
              c=colors[df_bancos_2[df_bancos_2['Banco'] == row['Banco']].index[0]], 
              alpha=0.6, edgecolors='black', linewidth=2)
    
    # Adicionar labels
    ax.annotate(row['Banco'], 
               (row['Maturidade_Digital_Score'], row['NPS']),
               xytext=(5, 5), 
               textcoords='offset points',
               fontsize=10, 
               fontweight='bold')

# Adicionar linha de tendência
if len(df_scatter) > 2:
    z = np.polyfit(df_scatter['Maturidade_Digital_Score'], df_scatter['NPS'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(df_scatter['Maturidade_Digital_Score'].min(), 
                         df_scatter['Maturidade_Digital_Score'].max(), 100)
    ax.plot(x_trend, p(x_trend), "r--", alpha=0.5, linewidth=2, label='Linha de Tendência')

ax.set_xlabel('Maturidade Digital (0-10)', fontsize=13, fontweight='bold')
ax.set_ylabel('NPS Score', fontsize=13, fontweight='bold')
ax.set_title('Correlação: Maturidade Digital vs Satisfação do Cliente (NPS)\n(Tamanho da bolha = % de clientes que consideram o banco como principal)', 
            fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

# Adicionar anotação sobre Priceless Bank
ax.text(0.02, 0.98, 'Priceless Bank:\n• Maturidade Digital: Média (5/10)\n• NPS: Não disponível\n• Posição estimada: Zona de incerteza', 
       transform=ax.transAxes, ha='left', va='top',
       bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.3), fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/arthurschiller/Documents/ibmec-rio/2025.2/hackathon-mastercard/grafico_2_7_correlacao.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Gráfico 2.7 criado: Análise de Correlação")

# ============================================================================
# RESUMO EXECUTIVO 2
# ============================================================================
print("\n" + "="*80)
print("RESUMO EXECUTIVO - BENCHMARKING OPERACIONAL E SATISFAÇÃO")
print("="*80)

print("\n📊 POSIÇÃO ATUAL DO PRICELESS BANK:")
print(f"  • Maturidade Digital: {df_bancos_2['Maturidade_Digital'].iloc[0]} ({df_bancos_2['Maturidade_Digital_Score'].iloc[0]}/10)")
print(f"  • Canais de Abertura: {df_bancos_2['Canal_Digital'].iloc[0]}% Digital / {df_bancos_2['Canal_Fisico'].iloc[0]}% Físico")
print(f"  • Open Finance: {df_bancos_2['Aceita_Open_Finance'].iloc[0]} (Status incerto)")
print(f"  • NPS: Não disponível")
print(f"  • % Banco Principal: Não disponível")

print("\n🎯 INSIGHTS DOS COMPETIDORES:")

print("\n  1. MATURIDADE DIGITAL:")
print(f"     • Líder: LuminaPay (Alta - 9/10)")
print(f"     • Priceless Bank: Média (5/10) - Espaço para evolução")
print(f"     • Desafio: Aurora Bank também é digital média (6/10) mas com melhor foco")

print("\n  2. SATISFAÇÃO DO CLIENTE (NPS):")
print(f"     • Excelente (>70): Lux Bank (82), LuminaPay (76)")
print(f"     • Bom (50-70): Papaya Bank (64)")
print(f"     • Precisa melhorar (<50): Aurora Bank (55)")
print(f"     • Priceless Bank: SEM DADOS - CRÍTICO!")

print("\n  3. FIDELIZAÇÃO (Banco Principal):")
print(f"     • Líder: Papaya Bank (42.7%) - Alta consolidação")
print(f"     • LuminaPay: 37.4% - Forte para banco jovem")
print(f"     • Aurora Bank: 13.6% - Foco em nicho específico")
print(f"     • Lux Bank: 6.4% - Exclusivo mas menor base")
print(f"     • Priceless Bank: SEM DADOS")

print("\n  4. OPEN FINANCE:")
print(f"     • Maior adoção: Lux Bank (82% exportaram dados)")
print(f"     • Aurora Bank: 79% - Alta digitalização refletida")
print(f"     • LuminaPay: 62% - Bom engajamento")
print(f"     • Papaya Bank: 44% - Tradicional, menor adoção")
print(f"     • Priceless Bank: Status incerto")

print("\n  5. CANAIS DE ATENDIMENTO:")
print(f"     • 100% Digital: LuminaPay, Aurora Bank")
print(f"     • Híbrido (50/50): Priceless Bank, Papaya Bank")
print(f"     • 100% Físico: Lux Bank (público affluent prefere)")

print("\n⚠️  ALERTAS CRÍTICOS PARA PRICELESS BANK:")
print("  ❌ NPS não disponível - Impossível medir satisfação!")
print("  ❌ % Banco Principal não disponível - Fidelização desconhecida!")
print("  ⚠️  Status Open Finance incerto - Pode estar perdendo oportunidades")
print("  ⚠️  Maturidade Digital média - Competidores digitais avançando rápido")
print("  ⚠️  Canal híbrido (50/50) - Custos altos, precisa otimizar")

print("\n💡 RECOMENDAÇÕES ESTRATÉGICAS:")
print("  1. URGENTE: Implementar medição de NPS")
print("  2. URGENTE: Pesquisar % de clientes que consideram banco principal")
print("  3. Definir estratégia Open Finance clara (aceitar ou não)")
print("  4. Avaliar viabilidade de aumentar canal digital (reduzir custos)")
print("  5. Investir em maturidade digital para competir com nativos digitais")
print("  6. Buscar NPS alvo de 70+ (zona de promotores)")

print("\n🎯 BENCHMARKS SUGERIDOS:")
print("  • NPS Mínimo: 70 (igual ou superior a LuminaPay)")
print("  • Banco Principal: 30%+ (para garantir fidelização)")
print("  • Open Finance: Se implementar, buscar 60%+ de adoção")
print("  • Maturidade Digital: Evoluir para 7/10 (digital avançado)")
print("  • Canal Digital: Aumentar para 70%+ (reduzir custos operacionais)")

print("\n" + "="*80)
print("✅ Análise completa! 7 gráficos salvos no diretório do projeto.")
print("="*80)
