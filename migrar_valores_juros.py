"""
Migração para adicionar campos de atualização de valores
"""

import sys
sys.path.append("src")

from database import SessionLocal
from sqlalchemy import text

def adicionar_campos_valores():
    """Adiciona campos de atualização de valores"""
    
    print("\n" + "="*70)
    print("MIGRANDO BANCO DE DADOS - VALORES E JUROS")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Verificar campos existentes
        result = db.execute(text("PRAGMA table_info(processos)"))
        colunas_existentes = [row[1] for row in result]
        
        # Adicionar campos se não existirem
        campos_novos = {
            'valor_principal': 'FLOAT',
            'valor_juros': 'FLOAT',
            'valor_correcao_monetaria': 'FLOAT',
            'taxa_juros_mensal': 'FLOAT DEFAULT 0.5',
            'indice_correcao': 'VARCHAR(20) DEFAULT "IPCA"',
            'data_base_calculo': 'DATE',
            'data_ultima_atualizacao_valor': 'DATETIME'
        }
        
        for campo, tipo in campos_novos.items():
            if campo not in colunas_existentes:
                print(f"\n[+] Adicionando campo: {campo}")
                db.execute(text(f"""
                    ALTER TABLE processos 
                    ADD COLUMN {campo} {tipo}
                """))
                db.commit()
                print(f"   [OK] Campo {campo} adicionado")
            else:
                print(f"   [OK] Campo {campo} já existe")
        
        # Criar tabela de histórico de valores
        print("\n[+] Criando tabela historico_valores...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS historico_valores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                data_atualizacao DATETIME NOT NULL,
                valor_principal FLOAT,
                valor_juros FLOAT,
                valor_correcao FLOAT,
                valor_total FLOAT,
                taxa_juros FLOAT,
                indice_correcao VARCHAR(20),
                periodo_inicio DATE,
                periodo_fim DATE,
                observacoes TEXT,
                usuario VARCHAR(100),
                FOREIGN KEY (processo_id) REFERENCES processos(id)
            )
        """))
        db.commit()
        print("   [OK] Tabela historico_valores criada")
        
        # Criar índices
        print("\n[+] Criando índices...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_historico_processo 
            ON historico_valores(processo_id)
        """))
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_historico_data 
            ON historico_valores(data_atualizacao)
        """))
        db.commit()
        print("   [OK] Índices criados")
        
        print("\n" + "="*70)
        print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    adicionar_campos_valores()
