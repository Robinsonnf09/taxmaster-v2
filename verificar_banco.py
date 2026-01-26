import sqlite3

conn = sqlite3.connect('taxmaster.db')
cursor = conn.cursor()

# Pegar estrutura da tabela processos
cursor.execute("PRAGMA table_info(processos)")
colunas = cursor.fetchall()

print('\n📊 COLUNAS DA TABELA PROCESSOS:')
print('=' * 60)
for col in colunas:
    print(f'   {col[0]:2d}. {col[1]:30s} | {col[2]:10s} | NULL: {col[3]}')

print('\n✅ Total de colunas:', len(colunas))

# Verificar se numero_processo existe
tem_numero_processo = any(col[1] == 'numero_processo' for col in colunas)
print('\n🔍 Coluna "numero_processo" existe?', '✅ SIM' if tem_numero_processo else '❌ NÃO')

conn.close()
