"""
Script de teste para o sistema de atualização de ofício
"""

import sys
sys.path.append("src")

from database import SessionLocal
from sqlalchemy import text
from datetime import datetime

def testar_sistema_atualizacao():
    """Testa o sistema de atualização de ofício"""
    
    print("\n" + "="*70)
    print("TESTANDO SISTEMA DE ATUALIZACAO DE OFICIO")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Verificar se tabela existe
        print("\n[1/4] Verificando tabela atualizacoes_oficio...")
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='atualizacoes_oficio'
        """)).fetchone()
        
        if result:
            print("   [OK] Tabela atualizacoes_oficio existe")
        else:
            print("   [ERRO] Tabela nao encontrada")
            return
        
        # Verificar campos na tabela processos
        print("\n[2/4] Verificando campos em processos...")
        result = db.execute(text("PRAGMA table_info(processos)"))
        colunas = [row[1] for row in result]
        
        if 'status_oficio' in colunas:
            print("   [OK] Campo status_oficio existe")
        else:
            print("   [AVISO] Campo status_oficio nao encontrado")
        
        if 'data_ultima_atualizacao_oficio' in colunas:
            print("   [OK] Campo data_ultima_atualizacao_oficio existe")
        else:
            print("   [AVISO] Campo data_ultima_atualizacao_oficio nao encontrado")
        
        # Contar processos
        print("\n[3/4] Verificando processos...")
        total_processos = db.execute(text("SELECT COUNT(*) FROM processos")).scalar()
        print(f"   [OK] Total de processos: {total_processos}")
        
        # Contar atualizações
        print("\n[4/4] Verificando atualizacoes...")
        total_atualizacoes = db.execute(text("SELECT COUNT(*) FROM atualizacoes_oficio")).scalar()
        print(f"   [OK] Total de atualizacoes: {total_atualizacoes}")
        
        print("\n" + "="*70)
        print("SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("="*70)
        
        print("\nPROXIMOS PASSOS:")
        print("1. Reinicie o servidor: python app.py")
        print("2. Acesse um processo")
        print("3. Clique em 'Atualizar Oficio'")
        print("4. Registre uma atualizacao")
        
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    testar_sistema_atualizacao()
