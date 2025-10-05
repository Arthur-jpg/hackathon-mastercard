#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRIADOR DE BANCO SQLITE - PRICELESS BANK
Criação de banco SQLite com as 3 tabelas principais para análises SQL
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🗄️ CRIANDO BANCO SQLITE - PRICELESS BANK")
print("="*80)
print()

# =============================================================================
# CONFIGURAÇÕES DO BANCO
# =============================================================================

nome_banco = "priceless_bank.db"
print(f"📊 Nome do banco: {nome_banco}")

# Remover banco existente se houver
if os.path.exists(nome_banco):
    os.remove(nome_banco)
    print("🗑️ Banco anterior removido")

# Conectar ao banco SQLite
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

print("✅ Conexão com SQLite estabelecida")
print()

# =============================================================================
# CARREGAR E PROCESSAR DADOS
# =============================================================================

print("📂 CARREGANDO DADOS DOS CSVs:")
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
# PROCESSAR DADOS PARA MELHOR ESTRUTURA SQL
# =============================================================================

print("🔧 PROCESSANDO DADOS PARA ESTRUTURA SQL:")
print("-" * 40)

# Processar dados de clientes
df_clientes_sql = df_clientes.copy()
df_clientes_sql['Data_Nascimento'] = pd.to_datetime(df_clientes_sql['Data_Nascimento'], format='%d/%m/%Y')
df_clientes_sql['Data_Criacao_Conta'] = pd.to_datetime(df_clientes_sql['Data_Criacao_Conta'])

# Calcular idade
data_referencia = datetime(2024, 12, 30)  # Data de referência das análises
df_clientes_sql['Idade'] = ((pd.to_datetime(data_referencia) - df_clientes_sql['Data_Nascimento']).dt.days / 365.25).astype(int)

# Calcular tempo de conta em meses
df_clientes_sql['Tempo_Conta_Meses'] = ((pd.to_datetime(data_referencia) - df_clientes_sql['Data_Criacao_Conta']).dt.days / 30.44).round(2)

print("✅ Clientes processados (idade e tempo de conta calculados)")

# Processar dados de cartões
df_cartoes_sql = df_cartoes.copy()
df_cartoes_sql['Data_Emissao'] = pd.to_datetime(df_cartoes_sql['Data_Emissao'])
df_cartoes_sql['Data_Ativacao'] = pd.to_datetime(df_cartoes_sql['Data_Ativacao'])
df_cartoes_sql['Data_Validade'] = pd.to_datetime(df_cartoes_sql['Data_Validade'])

# Calcular tempo de cartão em meses
df_cartoes_sql['Tempo_Cartao_Meses'] = ((pd.to_datetime(data_referencia) - df_cartoes_sql['Data_Emissao']).dt.days / 30.44).round(2)

# Flag para cartões recentes (>= 2023)
df_cartoes_sql['Cartao_Recente'] = (df_cartoes_sql['Data_Emissao'] >= '2023-01-01').astype(int)

print("✅ Cartões processados (tempo de cartão e flag recente calculados)")

# Processar dados de transações
df_transacoes_sql = df_transacoes.copy()
df_transacoes_sql['Data'] = pd.to_datetime(df_transacoes_sql['Data'])

# Extrair componentes da data
df_transacoes_sql['Ano'] = df_transacoes_sql['Data'].dt.year
df_transacoes_sql['Mes'] = df_transacoes_sql['Data'].dt.month
df_transacoes_sql['Dia_Semana'] = df_transacoes_sql['Data'].dt.dayofweek
df_transacoes_sql['Trimestre'] = df_transacoes_sql['Data'].dt.quarter

# Categorizar valores
df_transacoes_sql['Faixa_Valor'] = pd.cut(df_transacoes_sql['Valor_Compra'], 
                                         bins=[0, 100, 500, 1000, float('inf')],
                                         labels=['Baixo', 'Médio', 'Alto', 'Premium'])

# Flag para métodos digitais
wallets_digitais = ['Apple Pay', 'Google Pay', 'Samsung Pay']
df_transacoes_sql['Pagamento_Digital'] = df_transacoes_sql['Wallet'].isin(wallets_digitais).astype(int)
df_transacoes_sql['PayPass'] = (df_transacoes_sql['Input_Mode'] == 'PayPass').astype(int)

print("✅ Transações processadas (componentes de data e flags digitais)")
print()

# =============================================================================
# CRIAR TABELAS NO BANCO
# =============================================================================

print("🏗️ CRIANDO ESTRUTURA DO BANCO:")
print("-" * 35)

# Criar tabela CLIENTES
cursor.execute('''
CREATE TABLE clientes (
    cliente_id INTEGER PRIMARY KEY,
    data_nascimento DATE,
    renda_anual REAL,
    data_criacao_conta DATE,
    numero_cartoes INTEGER,
    cidade TEXT,
    estado TEXT,
    possui_conta_adicional TEXT,
    idade INTEGER,
    tempo_conta_meses REAL
)
''')

print("✅ Tabela 'clientes' criada")

# Criar tabela CARTOES
cursor.execute('''
CREATE TABLE cartoes (
    id_cartao INTEGER PRIMARY KEY,
    produto_mastercard TEXT,
    tipo_cartao TEXT,
    data_emissao DATE,
    data_ativacao DATE,
    data_validade DATE,
    limite_cartao REAL,
    tempo_cartao_meses REAL,
    cartao_recente INTEGER
)
''')

print("✅ Tabela 'cartoes' criada")

# Criar tabela TRANSACOES
cursor.execute('''
CREATE TABLE transacoes (
    id_transacao INTEGER PRIMARY KEY,
    data DATE,
    valor_compra REAL,
    industria TEXT,
    tipo_compra TEXT,
    qtd_parcelas INTEGER,
    wallet TEXT,
    cliente_id INTEGER,
    id_cartao INTEGER,
    input_mode TEXT,
    input_mode_code INTEGER,
    crossborder INTEGER,
    contactless INTEGER,
    ano INTEGER,
    mes INTEGER,
    dia_semana INTEGER,
    trimestre INTEGER,
    faixa_valor TEXT,
    pagamento_digital INTEGER,
    paypass INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes (cliente_id),
    FOREIGN KEY (id_cartao) REFERENCES cartoes (id_cartao)
)
''')

print("✅ Tabela 'transacoes' criada")
print()

# =============================================================================
# INSERIR DADOS NAS TABELAS
# =============================================================================

print("📥 INSERINDO DADOS NO BANCO:")
print("-" * 30)

# Inserir clientes
df_clientes_sql.to_sql('clientes', conn, if_exists='replace', index=False)
print(f"✅ {len(df_clientes_sql):,} clientes inseridos")

# Inserir cartões
df_cartoes_sql.to_sql('cartoes', conn, if_exists='replace', index=False)
print(f"✅ {len(df_cartoes_sql):,} cartões inseridos")

# Inserir transações
df_transacoes_sql.to_sql('transacoes', conn, if_exists='replace', index=False)
print(f"✅ {len(df_transacoes_sql):,} transações inseridas")
print()

# =============================================================================
# CRIAR VIEWS ÚTEIS PARA ANÁLISES
# =============================================================================

print("👁️ CRIANDO VIEWS PARA ANÁLISES:")
print("-" * 35)

# View: Análise de Churn
cursor.execute('''
CREATE VIEW vw_analise_churn AS
SELECT 
    c.cliente_id,
    c.idade,
    c.renda_anual,
    c.tempo_conta_meses,
    c.estado,
    c.possui_conta_adicional,
    MAX(t.data) as ultima_transacao,
    COUNT(t.id_transacao) as total_transacoes,
    SUM(t.valor_compra) as valor_total,
    AVG(t.valor_compra) as ticket_medio,
    CASE 
        WHEN MAX(t.data) < DATE('2024-12-30', '-90 days') THEN 1 
        ELSE 0 
    END as churn,
    CASE 
        WHEN c.tempo_conta_meses <= 6 THEN '0-6 meses'
        WHEN c.tempo_conta_meses <= 12 THEN '6-12 meses'
        WHEN c.tempo_conta_meses <= 18 THEN '12-18 meses'
        WHEN c.tempo_conta_meses <= 24 THEN '18-24 meses'
        ELSE '24+ meses'
    END as faixa_tempo_conta
FROM clientes c
LEFT JOIN transacoes t ON c.cliente_id = t.cliente_id
GROUP BY c.cliente_id
''')

print("✅ View 'vw_analise_churn' criada")

# View: Análise de Cartões
cursor.execute('''
CREATE VIEW vw_analise_cartoes AS
SELECT 
    cart.id_cartao,
    cart.produto_mastercard,
    cart.tipo_cartao,
    cart.limite_cartao,
    cart.tempo_cartao_meses,
    cart.cartao_recente,
    c.cliente_id,
    c.estado,
    COUNT(t.id_transacao) as total_transacoes,
    SUM(t.valor_compra) as valor_total,
    MAX(t.data) as ultima_transacao,
    CASE 
        WHEN MAX(t.data) < DATE('2024-12-30', '-90 days') THEN 1 
        ELSE 0 
    END as churn,
    CASE 
        WHEN cart.tempo_cartao_meses <= 6 THEN '0-6 meses'
        WHEN cart.tempo_cartao_meses <= 12 THEN '6-12 meses'
        WHEN cart.tempo_cartao_meses <= 18 THEN '12-18 meses'
        WHEN cart.tempo_cartao_meses <= 24 THEN '18-24 meses'
        ELSE '24+ meses'
    END as faixa_tempo_cartao
FROM cartoes cart
LEFT JOIN transacoes t ON cart.id_cartao = t.id_cartao
LEFT JOIN clientes c ON t.cliente_id = c.cliente_id
WHERE cart.cartao_recente = 1  -- Apenas cartões >= 2023
GROUP BY cart.id_cartao
''')

print("✅ View 'vw_analise_cartoes' criada")

# View: Transações Enriquecidas
cursor.execute('''
CREATE VIEW vw_transacoes_completas AS
SELECT 
    t.*,
    c.idade,
    c.renda_anual,
    c.estado,
    c.cidade,
    c.possui_conta_adicional,
    cart.produto_mastercard,
    cart.tipo_cartao,
    cart.limite_cartao
FROM transacoes t
JOIN clientes c ON t.cliente_id = c.cliente_id
JOIN cartoes cart ON t.id_cartao = cart.id_cartao
''')

print("✅ View 'vw_transacoes_completas' criada")

# View: Resumo por Cliente
cursor.execute('''
CREATE VIEW vw_resumo_cliente AS
SELECT 
    c.cliente_id,
    c.idade,
    c.renda_anual,
    c.estado,
    c.tempo_conta_meses,
    COUNT(DISTINCT t.id_cartao) as qtd_cartoes_ativos,
    COUNT(t.id_transacao) as total_transacoes,
    SUM(t.valor_compra) as receita_total,
    AVG(t.valor_compra) as ticket_medio,
    SUM(t.pagamento_digital) as transacoes_digitais,
    ROUND(SUM(t.pagamento_digital) * 100.0 / COUNT(t.id_transacao), 2) as pct_digital,
    MAX(t.data) as ultima_transacao,
    CASE 
        WHEN MAX(t.data) < DATE('2024-12-30', '-90 days') THEN 'Churn' 
        ELSE 'Ativo' 
    END as status_cliente
FROM clientes c
LEFT JOIN transacoes t ON c.cliente_id = t.cliente_id
GROUP BY c.cliente_id
''')

print("✅ View 'vw_resumo_cliente' criada")
print()

# =============================================================================
# CRIAR ÍNDICES PARA PERFORMANCE
# =============================================================================

print("⚡ CRIANDO ÍNDICES PARA PERFORMANCE:")
print("-" * 40)

indices = [
    "CREATE INDEX idx_cliente_id ON transacoes(cliente_id)",
    "CREATE INDEX idx_cartao_id ON transacoes(id_cartao)",
    "CREATE INDEX idx_data_transacao ON transacoes(data)",
    "CREATE INDEX idx_estado_cliente ON clientes(estado)",
    "CREATE INDEX idx_produto_cartao ON cartoes(produto_mastercard)",
    "CREATE INDEX idx_cartao_recente ON cartoes(cartao_recente)"
]

for idx in indices:
    cursor.execute(idx)
    
print(f"✅ {len(indices)} índices criados")
print()

# =============================================================================
# CRIAR ARQUIVO COM QUERIES DE EXEMPLO
# =============================================================================

queries_exemplo = '''-- QUERIES DE EXEMPLO PARA O BANCO PRICELESS BANK

-- 1. ANÁLISE DE CHURN POR FAIXA ETÁRIA
SELECT 
    CASE 
        WHEN idade <= 25 THEN '18-25'
        WHEN idade <= 35 THEN '26-35'
        WHEN idade <= 45 THEN '36-45'
        WHEN idade <= 55 THEN '46-55'
        WHEN idade <= 65 THEN '56-65'
        ELSE '65+'
    END as faixa_etaria,
    COUNT(*) as total_clientes,
    SUM(churn) as clientes_churn,
    ROUND(AVG(churn) * 100, 2) as taxa_churn
FROM vw_analise_churn
GROUP BY faixa_etaria
ORDER BY taxa_churn DESC;

-- 2. CHURN POR TEMPO DE CONTA vs TEMPO DE CARTÃO
SELECT 
    'Tempo de Conta' as tipo_tempo,
    faixa_tempo_conta as faixa,
    COUNT(*) as total,
    SUM(churn) as churns,
    ROUND(AVG(churn) * 100, 2) as taxa_churn
FROM vw_analise_churn
GROUP BY faixa_tempo_conta
UNION ALL
SELECT 
    'Tempo de Cartão' as tipo_tempo,
    faixa_tempo_cartao as faixa,
    COUNT(*) as total,
    SUM(churn) as churns,
    ROUND(AVG(churn) * 100, 2) as taxa_churn
FROM vw_analise_cartoes
WHERE faixa_tempo_cartao IS NOT NULL
GROUP BY faixa_tempo_cartao
ORDER BY tipo_tempo, taxa_churn DESC;

-- 3. TOP 10 CLIENTES POR RECEITA (ATIVOS)
SELECT 
    cliente_id,
    idade,
    estado,
    receita_total,
    total_transacoes,
    ticket_medio,
    pct_digital
FROM vw_resumo_cliente
WHERE status_cliente = 'Ativo'
ORDER BY receita_total DESC
LIMIT 10;

-- 4. ANÁLISE DE DIGITALIZAÇÃO POR ESTADO
SELECT 
    estado,
    COUNT(*) as total_clientes,
    AVG(pct_digital) as media_digital,
    SUM(CASE WHEN status_cliente = 'Churn' THEN 1 ELSE 0 END) as churns,
    ROUND(AVG(CASE WHEN status_cliente = 'Churn' THEN 1 ELSE 0 END) * 100, 2) as taxa_churn
FROM vw_resumo_cliente
GROUP BY estado
ORDER BY taxa_churn DESC;

-- 5. TRANSAÇÕES POR MÉTODO DE PAGAMENTO
SELECT 
    CASE 
        WHEN pagamento_digital = 1 THEN 'Digital (Wallet)'
        WHEN paypass = 1 THEN 'Contactless'
        ELSE 'Tradicional'
    END as metodo_pagamento,
    COUNT(*) as total_transacoes,
    SUM(valor_compra) as valor_total,
    AVG(valor_compra) as ticket_medio
FROM transacoes
GROUP BY metodo_pagamento
ORDER BY valor_total DESC;

-- 6. EVOLUÇÃO MENSAL DE TRANSAÇÕES DIGITAIS
SELECT 
    ano,
    mes,
    COUNT(*) as total_transacoes,
    SUM(pagamento_digital) as transacoes_digitais,
    ROUND(SUM(pagamento_digital) * 100.0 / COUNT(*), 2) as pct_digital
FROM transacoes
WHERE ano >= 2023
GROUP BY ano, mes
ORDER BY ano, mes;

-- 7. PRODUTOS MASTERCARD COM MAIOR CHURN
SELECT 
    produto_mastercard,
    COUNT(*) as total_cartoes,
    SUM(churn) as cartoes_churn,
    ROUND(AVG(churn) * 100, 2) as taxa_churn,
    AVG(limite_cartao) as limite_medio
FROM vw_analise_cartoes
GROUP BY produto_mastercard
ORDER BY taxa_churn DESC;

-- 8. CLIENTES EM RISCO (Alta receita + Churn)
SELECT 
    cliente_id,
    idade,
    estado,
    receita_total,
    pct_digital,
    ultima_transacao,
    JULIANDAY('2024-12-30') - JULIANDAY(ultima_transacao) as dias_sem_transacao
FROM vw_resumo_cliente
WHERE status_cliente = 'Churn' 
AND receita_total > 10000
ORDER BY receita_total DESC;

-- 9. CORRELAÇÃO RENDA vs DIGITALIZAÇÃO vs CHURN
SELECT 
    CASE 
        WHEN renda_anual <= 30000 THEN 'Baixa'
        WHEN renda_anual <= 75000 THEN 'Média'
        WHEN renda_anual <= 150000 THEN 'Alta'
        ELSE 'Premium'
    END as faixa_renda,
    COUNT(*) as total_clientes,
    AVG(pct_digital) as media_digital,
    SUM(CASE WHEN status_cliente = 'Churn' THEN 1 ELSE 0 END) as churns,
    ROUND(AVG(CASE WHEN status_cliente = 'Churn' THEN 1 ELSE 0 END) * 100, 2) as taxa_churn,
    AVG(receita_total) as receita_media
FROM vw_resumo_cliente
GROUP BY faixa_renda
ORDER BY receita_media DESC;

-- 10. ANÁLISE DE CARTÕES RECENTES (>= 2023) vs ANTIGOS
SELECT 
    CASE WHEN cartao_recente = 1 THEN 'Recente (>=2023)' ELSE 'Antigo (<2023)' END as tipo_cartao,
    COUNT(*) as total_cartoes,
    COUNT(CASE WHEN churn = 1 THEN 1 END) as cartoes_churn,
    ROUND(AVG(churn) * 100, 2) as taxa_churn,
    AVG(valor_total) as receita_media
FROM vw_analise_cartoes
GROUP BY cartao_recente;

-- ESTRUTURA DAS TABELAS
.schema clientes
.schema cartoes  
.schema transacoes
'''

# Salvar queries de exemplo
with open('queries_exemplo.sql', 'w', encoding='utf-8') as f:
    f.write(queries_exemplo)

print("✅ Arquivo 'queries_exemplo.sql' criado com 10 queries de exemplo")
print()

# =============================================================================
# TESTES E VALIDAÇÕES
# =============================================================================

print("🧪 EXECUTANDO TESTES DE VALIDAÇÃO:")
print("-" * 40)

# Teste 1: Contagem de registros
cursor.execute("SELECT COUNT(*) FROM clientes")
count_clientes = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM cartoes")  
count_cartoes = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM transacoes")
count_transacoes = cursor.fetchone()[0]

print(f"✅ Clientes no banco: {count_clientes:,}")
print(f"✅ Cartões no banco: {count_cartoes:,}")
print(f"✅ Transações no banco: {count_transacoes:,}")

# Teste 2: Query de exemplo - Taxa de churn geral
cursor.execute("SELECT ROUND(AVG(churn) * 100, 2) as taxa_churn FROM vw_analise_churn")
taxa_churn = cursor.fetchone()[0]
print(f"✅ Taxa de churn geral: {taxa_churn}%")

# Teste 3: Query de exemplo - Transações digitais
cursor.execute("SELECT ROUND(AVG(pagamento_digital) * 100, 2) as pct_digital FROM transacoes")
pct_digital = cursor.fetchone()[0]
print(f"✅ % Transações digitais: {pct_digital}%")

# Teste 4: Query de exemplo - Churn por faixa de tempo de cartão
cursor.execute("""
SELECT faixa_tempo_cartao, COUNT(*) as total, ROUND(AVG(churn) * 100, 2) as taxa_churn
FROM vw_analise_cartoes 
WHERE faixa_tempo_cartao IS NOT NULL
GROUP BY faixa_tempo_cartao
ORDER BY taxa_churn DESC
""")

print("\n🔍 CHURN POR TEMPO DE CARTÃO (validação):")
for row in cursor.fetchall():
    print(f"   • {row[0]}: {row[2]}% churn ({row[1]} cartões)")

print()

# =============================================================================
# FINALIZAR
# =============================================================================

# Commit e fechar conexão
conn.commit()
conn.close()

print("="*80)
print("🎯 BANCO SQLITE CRIADO COM SUCESSO!")
print("="*80)
print()

print("📊 RESUMO:")
print(f"   • Arquivo: {nome_banco}")
print(f"   • Tabelas: 3 (clientes, cartoes, transacoes)")
print(f"   • Views: 4 (análises pré-construídas)")
print(f"   • Índices: {len(indices)} (para performance)")
print(f"   • Queries exemplo: queries_exemplo.sql")
print()

print("🔧 COMO USAR:")
print("   1. Instalar SQLite browser: https://sqlitebrowser.org/")
print("   2. Abrir arquivo priceless_bank.db")
print("   3. Usar queries do arquivo queries_exemplo.sql")
print("   4. Ou conectar via Python/outras linguagens")
print()

print("💡 VIEWS DISPONÍVEIS:")
print("   • vw_analise_churn - Análise completa de churn por cliente")
print("   • vw_analise_cartoes - Análise de churn por cartão (>=2023)")
print("   • vw_transacoes_completas - Transações com dados dos clientes")
print("   • vw_resumo_cliente - Resumo executivo por cliente")
print()

print("🎯 PRÓXIMOS PASSOS:")
print("   • Use as queries de exemplo para explorar os dados")
print("   • Crie suas próprias análises SQL personalizadas")
print("   • Conecte o banco a ferramentas de BI (Power BI, Tableau)")
print()

print("="*80)
print("✅ BANCO PRONTO PARA ANÁLISES SQL!")
print("="*80)