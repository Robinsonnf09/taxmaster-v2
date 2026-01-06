"""
Script para marcar alguns processos como "sem pendência" (pagos)
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models_atualizado import Processo

def marcar_processos_pagos():
    """Marca alguns processos como pagos (sem pendência)"""
    db = SessionLocal()
    
    try:
        # Pegar 2 processos para marcar como pagos
        processos = db.query(Processo).limit(2).all()
        
        if len(processos) >= 2:
            # Marcar primeiro processo como pago
            processos[0].possui_pendencia_pagamento = False
            processos[0].observacoes = (processos[0].observacoes or "") + " | PAGAMENTO REALIZADO EM 15/12/2023"
            
            # Marcar segundo processo como pago
            processos[1].possui_pendencia_pagamento = False
            processos[1].observacoes = (processos[1].observacoes or "") + " | PAGAMENTO REALIZADO EM 20/11/2023"
            
            db.commit()
            
            print(f"[OK] {len(processos)} processos marcados como PAGOS (sem pendencia)")
            print(f"   - {processos[0].numero_processo}")
            print(f"   - {processos[1].numero_processo}")
        else:
            print("[INFO] Nao ha processos suficientes para marcar")
            
    except Exception as e:
        db.rollback()
        print(f"[ERRO] {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    marcar_processos_pagos()
