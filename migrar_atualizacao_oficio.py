"""
Script para adicionar campos de atualização de ofício ao banco existente
"""

import sys
sys.path.append("src")

from database import SessionLocal, engine
from sqlalchemy import text

def adicionar_campos_atualizacao_oficio():
    """Adiciona novos campos à tabela processos"""
    
    print("\n" + "="*70)
    print("MIGRANDO BANCO DE DADOS")
    print("Adicionando campos de atualização de ofício")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Verificar se campos já existem
        result = db.execute(text("PRAGMA table_info(processos)"))
        colunas_existentes = [row[1] for row in result]
        
        # Adicionar status_oficio se não existir
        if 'status_oficio' not in colunas_existentes:
            print("\n[1/2] Adicionando coluna status_oficio...")
            db.execute(text("""
                ALTER TABLE processos 
                ADD COLUMN status_oficio VARCHAR(50) DEFAULT 'NAO_EXPEDIDO'
            """))
            db.commit()
            print("   [OK] Coluna status_oficio adicionada")
        else:
            print("\n[1/2] Coluna status_oficio já existe")
        
        # Adicionar data_ultima_atualizacao_oficio se não existir
        if 'data_ultima_atualizacao_oficio' not in colunas_existentes:
            print("\n[2/2] Adicionando coluna data_ultima_atualizacao_oficio...")
            db.execute(text("""
                ALTER TABLE processos 
                ADD COLUMN data_ultima_atualizacao_oficio DATETIME
            """))
            db.commit()
            print("   [OK] Coluna data_ultima_atualizacao_oficio adicionada")
        else:
            print("\n[2/2] Coluna data_ultima_atualizacao_oficio já existe")
        
        # Criar tabela de atualizações se não existir
        print("\n[3/3] Criando tabela atualizacoes_oficio...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS atualizacoes_oficio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                data_atualizacao DATETIME NOT NULL,
                status_anterior VARCHAR(50),
                status_novo VARCHAR(50) NOT NULL,
                descricao TEXT,
                observacoes TEXT,
                valor_atualizado FLOAT,
                numero_oficio VARCHAR(50),
                numero_precatorio VARCHAR(50),
                origem VARCHAR(50),
                usuario VARCHAR(100),
                validado BOOLEAN DEFAULT 0,
                data_validacao DATETIME,
                FOREIGN KEY (processo_id) REFERENCES processos(id)
            )
        """))
        db.commit()
        print("   [OK] Tabela atualizacoes_oficio criada")
        
        # Criar índices
        print("\n[4/4] Criando índices...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_atualizacoes_processo 
            ON atualizacoes_oficio(processo_id)
        """))
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_atualizacoes_data 
            ON atualizacoes_oficio(data_atualizacao)
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
    adicionar_campos_atualizacao_oficio()
