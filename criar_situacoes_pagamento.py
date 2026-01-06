"""
Script para criar processos de exemplo com diferentes situações de pagamento
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models_atualizado import Processo, StatusProcessoEnum

def criar_exemplos_situacao_pagamento():
    """Cria exemplos das 3 situações de pagamento"""
    db = SessionLocal()
    
    try:
        processos = db.query(Processo).all()
        
        if len(processos) >= 6:
            # 2 processos COM PENDÊNCIA (já existem por padrão)
            processos[0].possui_pendencia_pagamento = True
            processos[0].status = StatusProcessoEnum.PENDENTE
            processos[0].observacoes = "COM PENDÊNCIA: Aguardando documentação complementar"
            
            processos[1].possui_pendencia_pagamento = True
            processos[1].status = StatusProcessoEnum.EM_ANALISE
            processos[1].observacoes = "COM PENDÊNCIA: Em análise pelo tribunal"
            
            # 2 processos PRONTO E NÃO PAGO
            processos[2].possui_pendencia_pagamento = False
            processos[2].status = StatusProcessoEnum.VALIDADO
            processos[2].observacoes = "PRONTO E NÃO PAGO: Sem pendências, aguardando inclusão em lista de pagamento"
            
            processos[3].possui_pendencia_pagamento = False
            processos[3].status = StatusProcessoEnum.OFICIO_BAIXADO
            processos[3].observacoes = "PRONTO E NÃO PAGO: Ofício baixado, pronto para pagamento"
            
            # 2 processos PAGOS
            processos[4].possui_pendencia_pagamento = False
            processos[4].status = StatusProcessoEnum.PAGO
            processos[4].observacoes = "PAGO: Pagamento realizado em 15/12/2023"
            
            processos[5].possui_pendencia_pagamento = False
            processos[5].status = StatusProcessoEnum.PAGO
            processos[5].observacoes = "PAGO: Pagamento realizado em 20/11/2023"
            
            db.commit()
            
            print("\n[OK] Processos de exemplo criados com sucesso!")
            print("\n" + "="*70)
            print("SITUAÇÕES DE PAGAMENTO CRIADAS:")
            print("="*70)
            
            print("\n1. COM PENDÊNCIA (2 processos):")
            print(f"   - {processos[0].numero_processo}")
            print(f"   - {processos[1].numero_processo}")
            
            print("\n2. PRONTO E NÃO PAGO (2 processos):")
            print(f"   - {processos[2].numero_processo}")
            print(f"   - {processos[3].numero_processo}")
            
            print("\n3. PAGOS (2 processos):")
            print(f"   - {processos[4].numero_processo}")
            print(f"   - {processos[5].numero_processo}")
            
            print("\n" + "="*70)
        else:
            print("[INFO] Não há processos suficientes para criar exemplos")
            
    except Exception as e:
        db.rollback()
        print(f"[ERRO] {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    criar_exemplos_situacao_pagamento()
