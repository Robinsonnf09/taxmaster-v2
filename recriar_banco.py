from src.database import engine, Base, SessionLocal
from src.models import Processo, Contato

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

# Verificar
import sqlite3
conn = sqlite3.connect('taxmaster.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(processos)")
colunas = cursor.fetchall()

print(f'\n✅ Banco recriado com {len(colunas)} colunas!')

# Verificar numero_processo
tem_numero_processo = any(col[1] == 'numero_processo' for col in colunas)
if tem_numero_processo:
    print('✅ Coluna "numero_processo" existe!')
else:
    print('❌ ERRO: Coluna "numero_processo" ainda não existe!')

conn.close()
