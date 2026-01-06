"""
Módulo de Automação - Consulta de Status dos Processos
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models import Processo
from sqlalchemy import text
from datetime import datetime
import time
import random

class ConsultadorStatus:
    """Consulta status dos processos nos tribunais"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.resultados = {
            'processados': 0,
            'sucesso': 0,
            'erros': 0,
            'atualizacoes': 0,
            'logs': []
        }
    
    def log(self, mensagem, tipo='info'):
        """Adiciona log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.resultados['logs'].append({
            'timestamp': timestamp,
            'mensagem': mensagem,
            'tipo': tipo
        })
        print(f"[{timestamp}] {mensagem}")
    
    def consultar_todos(self, tribunal='TODOS', filtro_processos='TODOS'):
        """Consulta status de todos os processos"""
        try:
            self.log("Iniciando consulta de status...", 'info')
            
            # Buscar processos
            query = self.db.query(Processo)
            
            if tribunal != 'TODOS':
                query = query.filter(Processo.tribunal == tribunal)
            
            processos = query.all()
            total = len(processos)
            
            self.log(f"Total de processos para consultar: {total}", 'info')
            
            # Consultar cada processo
            for i, processo in enumerate(processos, 1):
                self.resultados['processados'] += 1
                
                self.log(f"[{i}/{total}] Consultando: {processo.numero_processo}", 'info')
                
                try:
                    resultado = self.consultar_processo(processo)
                    
                    if resultado['atualizado']:
                        self.resultados['sucesso'] += 1
                        self.resultados['atualizacoes'] += 1
                        self.log(f"  ✓ Status atualizado: {resultado['status']}", 'success')
                    else:
                        self.log(f"  - Sem alterações", 'info')
                    
                    # Delay
                    time.sleep(1)
                    
                except Exception as e:
                    self.resultados['erros'] += 1
                    self.log(f"  ✗ Erro: {str(e)}", 'error')
            
            self.log(f"Consulta concluída! Atualizações: {self.resultados['atualizacoes']}", 'success')
            
            return self.resultados
            
        except Exception as e:
            self.log(f"Erro geral: {str(e)}", 'error')
            return self.resultados
        finally:
            self.db.close()
    
    def consultar_processo(self, processo):
        """Consulta status de um processo específico"""
        try:
            # Simular consulta (implementar busca real em produção)
            status_possiveis = [
                'Em Análise', 'Validado', 'Ofício Baixado', 
                'Em Lista de Pagamento', 'Pago'
            ]
            
            # 20% de chance de ter mudança de status
            if random.random() &lt; 0.2:
                novo_status = random.choice(status_possiveis)
                
                # Atualizar no banco
                self.db.execute(text("""
                    UPDATE processos 
                    SET status = :status,
                        data_atualizacao = :data_atualizacao
                    WHERE id = :id
                """), {
                    'status': novo_status,
                    'data_atualizacao': datetime.now(),
                    'id': processo.id
                })
                self.db.commit()
                
                return {
                    'atualizado': True,
                    'status': novo_status
                }
            else:
                return {'atualizado': False}
                
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao consultar processo: {e}")
            return {'atualizado': False}

# Teste
if __name__ == "__main__":
    consultador = ConsultadorStatus()
    resultado = consultador.consultar_todos()
    
    print("\n" + "="*70)
    print("RESULTADO DA CONSULTA")
    print("="*70)
    print(f"Processados: {resultado['processados']}")
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Erros: {resultado['erros']}")
    print(f"Atualizações: {resultado['atualizacoes']}")
    print("="*70)
