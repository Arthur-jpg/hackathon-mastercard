import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("ANÁLISE CORRIGIDA: LIMITES DE CARTÃO vs GASTOS MENSAIS")
print("Identificação de Inconsistências e Potencial Evasão de Clientes")
print("=" * 100)

# Carregar dados
clientes = pd.read_csv('data/Base_clientes.csv')
transacoes = pd.read_csv('data/Base_transacoes.csv')
cartoes = pd.read_csv('data/Base_cartoes.csv')

# Preparar dados
transacoes['Data'] = pd.to_datetime(transacoes['Data'])
transacoes['Ano_Mes'] = transacoes['Data'].dt.to_period('M')

print("\n🔍 INVESTIGAÇÃO ESPECÍFICA: CARTÕES COM LIMITE ZERO")
print("=" * 60)

# Investigar cartões com limite zero
cartoes_limite_zero = cartoes[cartoes['Limite_Cartao'] == 0]
print(f"Cartões com limite R$ 0: {len(cartoes_limite_zero)}")
print("Tipos de cartão com limite zero:")
print(cartoes_limite_zero['Produto_Mastercard'].value_counts())

# Verificar se cartões de débito têm transações de crédito
cartoes_debito = cartoes[cartoes['Tipo_Cartao'] == 'Débito']['ID_Cartao'].unique()
transacoes_cartoes_debito = transacoes[transacoes['ID_Cartao'].isin(cartoes_debito)]

print(f"\nTransações em cartões de débito: {len(transacoes_cartoes_debito)}")
print("Tipos de compra em cartões de débito:")
if len(transacoes_cartoes_debito) > 0:
    print(transacoes_cartoes_debito['Tipo_Compra'].value_counts())

print("\n🔍 ANÁLISE CORRIGIDA: APENAS CARTÕES DE CRÉDITO")
print("=" * 60)

# Filtrar apenas cartões de crédito para análise de limite
cartoes_credito = cartoes[cartoes['Tipo_Cartao'] == 'Crédito'].copy()
print(f"Cartões de crédito: {len(cartoes_credito)}")
print(f"Cartões de crédito com limite > 0: {(cartoes_credito['Limite_Cartao'] > 0).sum()}")
print(f"Cartões de crédito com limite = 0: {(cartoes_credito['Limite_Cartao'] == 0).sum()}")

# Casos problemáticos: cartões de crédito com limite zero
credito_limite_zero = cartoes_credito[cartoes_credito['Limite_Cartao'] == 0]
print(f"\n🚨 PROBLEMA CRÍTICO: {len(credito_limite_zero)} cartões de CRÉDITO com limite R$ 0")

if len(credito_limite_zero) > 0:
    # Verificar se estes cartões têm transações
    transacoes_credito_zero = transacoes[transacoes['ID_Cartao'].isin(credito_limite_zero['ID_Cartao'])]
    print(f"Transações em cartões de crédito com limite R$ 0: {len(transacoes_credito_zero)}")
    
    if len(transacoes_credito_zero) > 0:
        volume_impossivel = transacoes_credito_zero['Valor_Compra'].sum()
        print(f"Volume 'impossível' transacionado: R$ {volume_impossivel:,.2f}")
        
        clientes_afetados = transacoes_credito_zero['Cliente_ID'].nunique()
        print(f"Clientes afetados por este problema: {clientes_afetados}")

print("\n🔍 ANÁLISE LIMITES vs GASTOS (APENAS CRÉDITO)")
print("=" * 60)

# Recalcular análise apenas com cartões de crédito válidos
cartoes_credito_validos = cartoes_credito[cartoes_credito['Limite_Cartao'] > 0].copy()

# Relacionamento cliente -> cartões de crédito -> limites
cliente_cartao = transacoes[['Cliente_ID', 'ID_Cartao']].drop_duplicates()
cliente_cartao_credito = cliente_cartao.merge(
    cartoes_credito_validos[['ID_Cartao', 'Limite_Cartao', 'Produto_Mastercard']], 
    on='ID_Cartao', how='inner'
)

# Limites por cliente (apenas cartões de crédito válidos)
limite_por_cliente = cliente_cartao_credito.groupby('Cliente_ID').agg({
    'Limite_Cartao': ['sum', 'max', 'count']
}).round(2)

limite_por_cliente.columns = ['Limite_Total', 'Limite_Maximo', 'Qtd_Cartoes_Credito']
limite_por_cliente = limite_por_cliente.reset_index()

print(f"Clientes com cartões de crédito válidos: {len(limite_por_cliente)}")
print(f"Limite médio total (crédito): R$ {limite_por_cliente['Limite_Total'].mean():,.2f}")

# Gastos mensais por cliente
gastos_mensais = transacoes.groupby(['Cliente_ID', 'Ano_Mes']).agg({
    'Valor_Compra': ['sum', 'count', 'mean']
}).round(2)

gastos_mensais.columns = ['Gasto_Mensal', 'Qtd_Transacoes', 'Ticket_Medio']
gastos_mensais = gastos_mensais.reset_index()

# Juntar gastos com limites (apenas clientes com cartão de crédito)
analise_corrigida = gastos_mensais.merge(limite_por_cliente, on='Cliente_ID', how='inner')

# Adicionar renda
analise_corrigida = analise_corrigida.merge(
    clientes[['Cliente_ID', 'Renda_Anual']], on='Cliente_ID', how='left'
)

# Calcular métricas corrigidas
analise_corrigida['Utilizacao_Limite'] = (analise_corrigida['Gasto_Mensal'] / analise_corrigida['Limite_Total']) * 100
analise_corrigida['Renda_Mensal'] = analise_corrigida['Renda_Anual'] / 12

# Classificar situações (sem valores infinitos)
analise_corrigida['Situacao'] = 'Normal'

# Utilização alta
mask_utilizacao_muito_alta = analise_corrigida['Utilizacao_Limite'] > 90
analise_corrigida.loc[mask_utilizacao_muito_alta, 'Situacao'] = 'CRÍTICO: Utilização >90%'

mask_utilizacao_alta = (analise_corrigida['Utilizacao_Limite'] > 70) & (analise_corrigida['Utilizacao_Limite'] <= 90)
analise_corrigida.loc[mask_utilizacao_alta, 'Situacao'] = 'ALTO RISCO: Utilização 70-90%'

# Limite inadequado para renda (apenas onde temos renda)
mask_renda_valida = analise_corrigida['Renda_Anual'].notna()
analise_corrigida_com_renda = analise_corrigida[mask_renda_valida].copy()

if len(analise_corrigida_com_renda) > 0:
    # Limite muito baixo: < 30% da renda mensal
    mask_limite_baixo = (analise_corrigida_com_renda['Limite_Total'] < (analise_corrigida_com_renda['Renda_Mensal'] * 0.3))
    analise_corrigida.loc[analise_corrigida_com_renda[mask_limite_baixo].index, 'Situacao'] = 'Limite inadequado: Muito baixo'
    
    # Limite muito alto: > 200% da renda mensal  
    mask_limite_alto = (analise_corrigida_com_renda['Limite_Total'] > (analise_corrigida_com_renda['Renda_Mensal'] * 2))
    analise_corrigida.loc[analise_corrigida_com_renda[mask_limite_alto].index, 'Situacao'] = 'Limite inadequado: Muito alto'

print(f"\nTotal de registros analisados: {len(analise_corrigida)}")
print("DISTRIBUIÇÃO POR SITUAÇÃO (CORRIGIDA):")
situacao_counts = analise_corrigida['Situacao'].value_counts()
print(situacao_counts)

problematicos = len(analise_corrigida[analise_corrigida['Situacao'] != 'Normal'])
print(f"\nCasos problemáticos: {problematicos:,} de {len(analise_corrigida):,} ({problematicos/len(analise_corrigida)*100:.1f}%)")

print("\n🔍 ESTATÍSTICAS DETALHADAS")
print("=" * 60)

print("UTILIZAÇÃO DE LIMITE:")
print(f"• Média: {analise_corrigida['Utilizacao_Limite'].mean():.1f}%")
print(f"• Mediana: {analise_corrigida['Utilizacao_Limite'].median():.1f}%")
print(f"• Máxima: {analise_corrigida['Utilizacao_Limite'].max():.1f}%")

# Distribuição de utilização
utilizacao_ranges = pd.cut(analise_corrigida['Utilizacao_Limite'], 
                          bins=[0, 10, 30, 50, 70, 90, 100, float('inf')],
                          labels=['0-10%', '10-30%', '30-50%', '50-70%', '70-90%', '90-100%', '>100%'])

print(f"\nDISTRIBUIÇÃO DE UTILIZAÇÃO:")
print(utilizacao_ranges.value_counts().sort_index())

print("\n🔍 ANÁLISE POR PRODUTO MASTERCARD")
print("=" * 60)

# Análise por produto
if len(cliente_cartao_credito) > 0:
    analise_produto = analise_corrigida.merge(
        cliente_cartao_credito[['Cliente_ID', 'Produto_Mastercard']].drop_duplicates(),
        on='Cliente_ID', how='left'
    )
    
    produto_stats = analise_produto.groupby('Produto_Mastercard').agg({
        'Utilizacao_Limite': ['mean', 'median', 'count'],
        'Limite_Total': ['mean', 'median'],
        'Gasto_Mensal': ['mean', 'median']
    }).round(2)
    
    print("ESTATÍSTICAS POR PRODUTO:")
    print(produto_stats)

print("\n🔍 CASOS EXTREMOS IDENTIFICADOS")
print("=" * 60)

# Top utilizadores
top_utilizacao = analise_corrigida.nlargest(10, 'Utilizacao_Limite')
print("TOP 10 UTILIZADORES DE LIMITE:")
for _, row in top_utilizacao.iterrows():
    print(f"Cliente {row['Cliente_ID']}: {row['Utilizacao_Limite']:.1f}% - R$ {row['Gasto_Mensal']:,.0f} de R$ {row['Limite_Total']:,.0f}")

# Casos acima de 100%
acima_limite = analise_corrigida[analise_corrigida['Utilizacao_Limite'] > 100]
print(f"\n🚨 CASOS CRÍTICOS - GASTO > LIMITE: {len(acima_limite)}")

if len(acima_limite) > 0:
    print("DETALHES DOS CASOS CRÍTICOS:")
    for _, row in acima_limite.head().iterrows():
        print(f"Cliente {row['Cliente_ID']} ({row['Ano_Mes']}): Gastou R$ {row['Gasto_Mensal']:,.0f} com limite R$ {row['Limite_Total']:,.0f} ({row['Utilizacao_Limite']:.1f}%)")

print("\n🔍 RECOMENDAÇÕES BASEADAS NA ANÁLISE CORRIGIDA")
print("=" * 60)

# Identificar oportunidades
alta_utilizacao = analise_corrigida[analise_corrigida['Utilizacao_Limite'] > 70]
print(f"CLIENTES PARA AUMENTO DE LIMITE: {alta_utilizacao['Cliente_ID'].nunique()}")
print(f"Volume mensal desses clientes: R$ {alta_utilizacao['Gasto_Mensal'].sum():,.2f}")

baixa_utilizacao = analise_corrigida[analise_corrigida['Utilizacao_Limite'] < 10]
print(f"\nCLIENTES COM BAIXA UTILIZAÇÃO: {baixa_utilizacao['Cliente_ID'].nunique()}")
print(f"Limite total subutilizado: R$ {baixa_utilizacao['Limite_Total'].sum():,.2f}")

# Salvar análise corrigida
analise_corrigida.to_csv('analise_limites_corrigida.csv', index=False)
print(f"\n💾 Análise corrigida salva em: analise_limites_corrigida.csv")

# Criar visualizações corrigidas
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 15))

# Gráfico 1: Distribuição de Utilização (sem infinitos)
utilizacao_finita = analise_corrigida[analise_corrigida['Utilizacao_Limite'] < 200]['Utilizacao_Limite']  # Cap em 200%
ax1.hist(utilizacao_finita, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
ax1.axvline(utilizacao_finita.mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {utilizacao_finita.mean():.1f}%')
ax1.axvline(70, color='orange', linestyle='--', linewidth=2, label='Alerta: 70%')
ax1.axvline(90, color='red', linestyle='--', linewidth=2, label='Crítico: 90%')
ax1.set_title('Distribuição da Utilização de Limite (Cartões Crédito)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Utilização do Limite (%)')
ax1.set_ylabel('Número de Casos')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico 2: Situações por Casos
situacao_counts_plot = situacao_counts.head(6)  # Top 6 situações
colors = ['green', 'yellow', 'orange', 'red', 'purple', 'brown']
situacao_counts_plot.plot(kind='bar', ax=ax2, color=colors[:len(situacao_counts_plot)])
ax2.set_title('Distribuição por Situação de Risco (Corrigida)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Número de Casos')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3, axis='y')

# Gráfico 3: Limite vs Gasto (scatter)
sample_data = analise_corrigida.sample(min(1000, len(analise_corrigida)))
scatter = ax3.scatter(sample_data['Limite_Total'], sample_data['Gasto_Mensal'], 
                     c=sample_data['Utilizacao_Limite'], cmap='RdYlBu_r', alpha=0.6)
ax3.plot([0, sample_data['Limite_Total'].max()], [0, sample_data['Limite_Total'].max()], 
         'r--', alpha=0.8, label='Limite = Gasto')
ax3.set_title('Limite Total vs Gasto Mensal', fontsize=14, fontweight='bold')
ax3.set_xlabel('Limite Total (R$)')
ax3.set_ylabel('Gasto Mensal (R$)')
ax3.legend()
plt.colorbar(scatter, ax=ax3, label='Utilização (%)')
ax3.grid(True, alpha=0.3)

# Gráfico 4: Utilização por Produto Mastercard
if 'analise_produto' in locals():
    produto_utilizacao = analise_produto.groupby('Produto_Mastercard')['Utilizacao_Limite'].mean().sort_values(ascending=False)
    produto_utilizacao.plot(kind='bar', ax=ax4, color='lightcoral', alpha=0.7)
    ax4.set_title('Utilização Média por Produto Mastercard', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Utilização Média (%)')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('analise_limites_corrigida_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"\n📊 Dashboard corrigido salvo em: analise_limites_corrigida_dashboard.png")
print(f"🎯 Análise completa e corrigida finalizada!")

# Resumo executivo
print(f"\n" + "="*100)
print("RESUMO EXECUTIVO - ANÁLISE CORRIGIDA")
print("="*100)

print(f"📊 NÚMEROS PRINCIPAIS:")
print(f"• Clientes analisados: {analise_corrigida['Cliente_ID'].nunique():,}")
print(f"• Registros cliente-mês: {len(analise_corrigida):,}")
print(f"• Utilização média de limite: {analise_corrigida['Utilizacao_Limite'].mean():.1f}%")
print(f"• Casos com utilização >70%: {(analise_corrigida['Utilizacao_Limite'] > 70).sum():,}")
print(f"• Casos com utilização >100%: {(analise_corrigida['Utilizacao_Limite'] > 100).sum():,}")

volume_alto_risco = analise_corrigida[analise_corrigida['Utilizacao_Limite'] > 70]['Gasto_Mensal'].sum()
volume_total = analise_corrigida['Gasto_Mensal'].sum()

print(f"\n💰 IMPACTO FINANCEIRO:")
print(f"• Volume mensal total: R$ {volume_total:,.2f}")
print(f"• Volume alto risco (>70%): R$ {volume_alto_risco:,.2f} ({volume_alto_risco/volume_total*100:.1f}%)")
print(f"• Potencial perda anual: R$ {volume_alto_risco * 12:,.2f}")

print(f"\n🎯 CONCLUSÃO:")
print(f"A análise corrigida mostra que {problematicos/len(analise_corrigida)*100:.1f}% dos casos")
print(f"apresentam algum tipo de inconsistência na gestão de limites,")  
print(f"representando um risco real de evasão e perda de receita.")