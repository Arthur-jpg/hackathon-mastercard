import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("ANÁLISE COMPLETA: LIMITES DE CARTÃO vs GASTOS MENSAIS")
print("Identificação de Inconsistências e Potencial Evasão de Clientes")
print("=" * 100)

# Carregar dados
clientes = pd.read_csv('data/Base_clientes.csv')
transacoes = pd.read_csv('data/Base_transacoes.csv')
cartoes = pd.read_csv('data/Base_cartoes.csv')

# Preparar dados
transacoes['Data'] = pd.to_datetime(transacoes['Data'])
transacoes['Ano_Mes'] = transacoes['Data'].dt.to_period('M')
clientes['Data_Criacao_Conta'] = pd.to_datetime(clientes['Data_Criacao_Conta'])

print("\n🔍 ETAPA 1: RELACIONAMENTO CLIENTE-CARTÃO-LIMITE")
print("=" * 60)

# Criar relacionamento cliente -> cartões -> limites
cliente_cartao = transacoes[['Cliente_ID', 'ID_Cartao']].drop_duplicates()
cliente_cartao_limite = cliente_cartao.merge(cartoes[['ID_Cartao', 'Limite_Cartao', 'Tipo_Cartao', 'Produto_Mastercard']], 
                                            on='ID_Cartao', how='left')

# Calcular limite total por cliente (soma de todos os cartões)
limite_por_cliente = cliente_cartao_limite.groupby('Cliente_ID').agg({
    'Limite_Cartao': ['sum', 'max', 'count'],
    'Tipo_Cartao': lambda x: ', '.join(x.unique())
}).round(2)

limite_por_cliente.columns = ['Limite_Total', 'Limite_Maximo', 'Qtd_Cartoes', 'Tipos_Cartao']
limite_por_cliente = limite_por_cliente.reset_index()

print(f"Clientes com limites mapeados: {len(limite_por_cliente)}")
print(f"Limite médio total: R$ {limite_por_cliente['Limite_Total'].mean():,.2f}")
print(f"Limite máximo individual encontrado: R$ {limite_por_cliente['Limite_Maximo'].max():,.2f}")

print("\n🔍 ETAPA 2: GASTOS MENSAIS POR CLIENTE")
print("=" * 60)

# Calcular gastos mensais por cliente
gastos_mensais = transacoes.groupby(['Cliente_ID', 'Ano_Mes']).agg({
    'Valor_Compra': ['sum', 'count', 'mean'],
    'ID_Cartao': 'nunique'
}).round(2)

gastos_mensais.columns = ['Gasto_Mensal', 'Qtd_Transacoes', 'Ticket_Medio', 'Cartoes_Usados']
gastos_mensais = gastos_mensais.reset_index()

print(f"Total de registros cliente-mês: {len(gastos_mensais)}")
print(f"Gasto mensal médio: R$ {gastos_mensais['Gasto_Mensal'].mean():,.2f}")
print(f"Gasto mensal máximo: R$ {gastos_mensais['Gasto_Mensal'].max():,.2f}")

# Estatísticas por ano-mes
gastos_por_mes = gastos_mensais.groupby('Ano_Mes').agg({
    'Gasto_Mensal': ['mean', 'median', 'max'],
    'Cliente_ID': 'nunique'
}).round(2)

print(f"\nÚltimos 6 meses de atividade:")
print(gastos_por_mes.tail(6))

print("\n🔍 ETAPA 3: ANÁLISE LIMITE vs GASTO MENSAL")
print("=" * 60)

# Juntar limites com gastos mensais
analise_limite_gasto = gastos_mensais.merge(limite_por_cliente, on='Cliente_ID', how='inner')

# Adicionar informações de renda do cliente
analise_limite_gasto = analise_limite_gasto.merge(
    clientes[['Cliente_ID', 'Renda_Anual', 'Data_Criacao_Conta']], 
    on='Cliente_ID', how='left'
)

# Calcular métricas de utilização
analise_limite_gasto['Utilizacao_Limite'] = (analise_limite_gasto['Gasto_Mensal'] / analise_limite_gasto['Limite_Total']) * 100
analise_limite_gasto['Renda_Mensal'] = analise_limite_gasto['Renda_Anual'] / 12
analise_limite_gasto['Gasto_vs_Renda'] = (analise_limite_gasto['Gasto_Mensal'] / analise_limite_gasto['Renda_Mensal']) * 100

# Identificar situações problemáticas
analise_limite_gasto['Situacao'] = 'Normal'

# Critério 1: Gasto acima do limite (impossível, mas vamos verificar)
mask_acima_limite = analise_limite_gasto['Utilizacao_Limite'] > 100
analise_limite_gasto.loc[mask_acima_limite, 'Situacao'] = 'CRÍTICO: Gasto > Limite'

# Critério 2: Utilização muito alta (>90%)
mask_utilizacao_alta = (analise_limite_gasto['Utilizacao_Limite'] > 90) & (analise_limite_gasto['Utilizacao_Limite'] <= 100)
analise_limite_gasto.loc[mask_utilizacao_alta, 'Situacao'] = 'ALTO RISCO: Utilização >90%'

# Critério 3: Limite muito baixo para a renda (limite < 20% da renda mensal)
mask_limite_baixo = (analise_limite_gasto['Limite_Total'] < (analise_limite_gasto['Renda_Mensal'] * 0.2)) & (analise_limite_gasto['Renda_Anual'].notna())
analise_limite_gasto.loc[mask_limite_baixo, 'Situacao'] = 'INCONSISTENTE: Limite muito baixo'

# Critério 4: Limite muito alto para a renda (limite > 300% da renda mensal)
mask_limite_alto = (analise_limite_gasto['Limite_Total'] > (analise_limite_gasto['Renda_Mensal'] * 3)) & (analise_limite_gasto['Renda_Anual'].notna())
analise_limite_gasto.loc[mask_limite_alto, 'Situacao'] = 'INCONSISTENTE: Limite muito alto'

print("DISTRIBUIÇÃO POR SITUAÇÃO:")
situacao_counts = analise_limite_gasto['Situacao'].value_counts()
print(situacao_counts)

print(f"\nPERCENTUAL DE SITUAÇÕES PROBLEMÁTICAS:")
problematicos = len(analise_limite_gasto[analise_limite_gasto['Situacao'] != 'Normal'])
total = len(analise_limite_gasto)
print(f"{problematicos:,} de {total:,} registros ({problematicos/total*100:.1f}%)")

print("\n🔍 ETAPA 4: ANÁLISE DE EVASÃO POR SITUAÇÃO")
print("=" * 60)

# Identificar último mês de atividade por cliente
ultimo_mes_atividade = gastos_mensais.groupby('Cliente_ID')['Ano_Mes'].max().reset_index()
ultimo_mes_atividade.columns = ['Cliente_ID', 'Ultimo_Mes_Ativo']

# Considerar como evadido se não teve atividade nos últimos 3 meses
ultimo_mes_dataset = gastos_mensais['Ano_Mes'].max()
meses_inatividade = pd.Period('2024-08') - ultimo_mes_atividade['Ultimo_Mes_Ativo']
ultimo_mes_atividade['Meses_Inativo'] = meses_inatividade.apply(lambda x: x.n if hasattr(x, 'n') else 0)
ultimo_mes_atividade['Evadido'] = ultimo_mes_atividade['Meses_Inativo'] >= 3

# Juntar com análise de limites
evasao_por_situacao = analise_limite_gasto.merge(ultimo_mes_atividade, on='Cliente_ID', how='left')

# Calcular taxa de evasão por situação
taxa_evasao = evasao_por_situacao.groupby('Situacao').agg({
    'Cliente_ID': 'nunique',
    'Evadido': ['sum', 'mean']
}).round(3)

taxa_evasao.columns = ['Total_Clientes', 'Clientes_Evadidos', 'Taxa_Evasao']
taxa_evasao['Taxa_Evasao_Pct'] = taxa_evasao['Taxa_Evasao'] * 100

print("TAXA DE EVASÃO POR SITUAÇÃO:")
print(taxa_evasao.sort_values('Taxa_Evasao_Pct', ascending=False))

print("\n🔍 ETAPA 5: CASOS CRÍTICOS DETALHADOS")
print("=" * 60)

# Casos mais críticos
casos_criticos = analise_limite_gasto[
    (analise_limite_gasto['Situacao'].str.contains('CRÍTICO|ALTO RISCO')) |
    (analise_limite_gasto['Utilizacao_Limite'] > 80)
].copy()

casos_criticos = casos_criticos.merge(ultimo_mes_atividade[['Cliente_ID', 'Evadido']], on='Cliente_ID', how='left')

print(f"CASOS IDENTIFICADOS COMO CRÍTICOS: {len(casos_criticos)}")

if len(casos_criticos) > 0:
    print("\nAMOSTRA DE CASOS CRÍTICOS:")
    amostra_criticos = casos_criticos.nlargest(10, 'Utilizacao_Limite')[
        ['Cliente_ID', 'Ano_Mes', 'Gasto_Mensal', 'Limite_Total', 'Utilizacao_Limite', 'Renda_Mensal', 'Evadido', 'Situacao']
    ]
    for _, row in amostra_criticos.iterrows():
        print(f"Cliente {row['Cliente_ID']}: Gastou R$ {row['Gasto_Mensal']:,.0f} de limite R$ {row['Limite_Total']:,.0f} ({row['Utilizacao_Limite']:.1f}%) - {'EVADIDO' if row['Evadido'] else 'ATIVO'}")

print("\n🔍 ETAPA 6: ANÁLISE DE RENDA vs LIMITE")
print("=" * 60)

# Análise específica da relação renda vs limite
renda_limite = analise_limite_gasto[analise_limite_gasto['Renda_Anual'].notna()].copy()

# Criar faixas de renda
renda_limite['Faixa_Renda'] = pd.cut(renda_limite['Renda_Anual'], 
                                   bins=[0, 50000, 100000, 150000, float('inf')],
                                   labels=['Até 50k', '50k-100k', '100k-150k', 'Acima 150k'])

# Calcular ratio limite/renda anual
renda_limite['Ratio_Limite_Renda'] = renda_limite['Limite_Total'] / renda_limite['Renda_Anual']

print("ANÁLISE POR FAIXA DE RENDA:")
analise_faixa = renda_limite.groupby('Faixa_Renda').agg({
    'Cliente_ID': 'nunique',
    'Limite_Total': ['mean', 'median'],
    'Renda_Anual': ['mean', 'median'],
    'Ratio_Limite_Renda': ['mean', 'median'],
    'Utilizacao_Limite': ['mean', 'median']
}).round(2)

print(analise_faixa)

# Identificar casos extremos de ratio limite/renda
print(f"\nCASOS EXTREMOS:")
print(f"Ratios limite/renda > 1.5 (limite > 150% da renda anual): {(renda_limite['Ratio_Limite_Renda'] > 1.5).sum()} casos")
print(f"Ratios limite/renda < 0.1 (limite < 10% da renda anual): {(renda_limite['Ratio_Limite_Renda'] < 0.1).sum()} casos")

print("\n🔍 ETAPA 7: IMPACTO NO NEGÓCIO")
print("=" * 60)

# Calcular impacto financeiro
clientes_com_problema = analise_limite_gasto[analise_limite_gasto['Situacao'] != 'Normal']['Cliente_ID'].nunique()
total_clientes_analisados = analise_limite_gasto['Cliente_ID'].nunique()

# Volume transacional em risco
volume_em_risco = analise_limite_gasto[
    analise_limite_gasto['Situacao'] != 'Normal'
]['Gasto_Mensal'].sum()

volume_total = analise_limite_gasto['Gasto_Mensal'].sum()

print(f"IMPACTO QUANTIFICADO:")
print(f"• Clientes com situação problemática: {clientes_com_problema:,} de {total_clientes_analisados:,} ({clientes_com_problema/total_clientes_analisados*100:.1f}%)")
print(f"• Volume mensal em risco: R$ {volume_em_risco:,.2f} de R$ {volume_total:,.2f} ({volume_em_risco/volume_total*100:.1f}%)")

# Potencial perda anual
perda_anual_potencial = volume_em_risco * 12
print(f"• Potencial perda anual: R$ {perda_anual_potencial:,.2f}")

print("\n🔍 ETAPA 8: RECOMENDAÇÕES BASEADAS EM DADOS")
print("=" * 60)

# Análise de oportunidades de ajuste de limite
oportunidades = analise_limite_gasto[
    (analise_limite_gasto['Situacao'].str.contains('INCONSISTENTE')) |
    (analise_limite_gasto['Utilizacao_Limite'] > 70)
].copy()

print(f"OPORTUNIDADES DE AJUSTE IDENTIFICADAS:")
print(f"• Clientes para revisão de limite: {oportunidades['Cliente_ID'].nunique():,}")
print(f"• Volume mensal destes clientes: R$ {oportunidades['Gasto_Mensal'].sum():,.2f}")

# Sugestões específicas por tipo de problema
print(f"\nSUGESTÕES POR TIPO DE PROBLEMA:")

for situacao in analise_limite_gasto['Situacao'].unique():
    if situacao != 'Normal':
        count = (analise_limite_gasto['Situacao'] == situacao).sum()
        volume = analise_limite_gasto[analise_limite_gasto['Situacao'] == situacao]['Gasto_Mensal'].sum()
        print(f"• {situacao}: {count:,} casos, R$ {volume:,.2f} volume mensal")

print(f"\n📊 DASHBOARD DE MÉTRICAS CRÍTICAS:")
print(f"• Taxa de utilização média: {analise_limite_gasto['Utilizacao_Limite'].mean():.1f}%")
print(f"• Clientes com utilização >50%: {(analise_limite_gasto['Utilizacao_Limite'] > 50).sum():,}")
print(f"• Clientes com utilização >80%: {(analise_limite_gasto['Utilizacao_Limite'] > 80).sum():,}")
print(f"• Ticket médio dos problemáticos: R$ {analise_limite_gasto[analise_limite_gasto['Situacao'] != 'Normal']['Ticket_Medio'].mean():.2f}")

# Salvar resultados para análise posterior
analise_limite_gasto.to_csv('analise_limites_vs_gastos.csv', index=False)
print(f"\n💾 Análise completa salva em: analise_limites_vs_gastos.csv")

# Criar visualizações
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 15))

# Gráfico 1: Distribuição de Utilização de Limite
ax1.hist(analise_limite_gasto['Utilizacao_Limite'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
ax1.axvline(analise_limite_gasto['Utilizacao_Limite'].mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {analise_limite_gasto["Utilizacao_Limite"].mean():.1f}%')
ax1.axvline(80, color='orange', linestyle='--', linewidth=2, label='Limite Crítico: 80%')
ax1.set_title('Distribuição da Utilização de Limite (%)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Utilização do Limite (%)')
ax1.set_ylabel('Número de Casos')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico 2: Situação por Número de Casos
situacao_counts.plot(kind='bar', ax=ax2, color=['green', 'orange', 'red', 'purple', 'brown'])
ax2.set_title('Distribuição por Situação de Risco', fontsize=14, fontweight='bold')
ax2.set_ylabel('Número de Casos')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3, axis='y')

# Gráfico 3: Limite vs Renda por Faixa
if len(renda_limite) > 0:
    renda_limite_sample = renda_limite.sample(min(1000, len(renda_limite)))  # Sample para visualização
    scatter = ax3.scatter(renda_limite_sample['Renda_Anual'], renda_limite_sample['Limite_Total'], 
                         c=renda_limite_sample['Utilizacao_Limite'], cmap='RdYlBu_r', alpha=0.6)
    ax3.set_title('Limite vs Renda Anual (cor = utilização)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Renda Anual (R$)')
    ax3.set_ylabel('Limite Total (R$)')
    plt.colorbar(scatter, ax=ax3, label='Utilização Limite (%)')
    ax3.grid(True, alpha=0.3)

# Gráfico 4: Taxa de Evasão por Situação
if len(taxa_evasao) > 0:
    taxa_evasao['Taxa_Evasao_Pct'].plot(kind='bar', ax=ax4, color='red', alpha=0.7)
    ax4.set_title('Taxa de Evasão por Situação de Risco', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Taxa de Evasão (%)')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('analise_limites_gastos_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"\n📊 Dashboard visual salvo em: analise_limites_gastos_dashboard.png")
print(f"🎯 Análise completa finalizada com identificação de inconsistências e potencial evasão!")