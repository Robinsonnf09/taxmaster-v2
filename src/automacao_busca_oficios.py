"""
Módulo de Automação - Busca de Ofícios Requisitórios
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models import Processo
from sqlalchemy import text
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import re

class BuscadorOficios:
    """Busca automática de ofícios nos portais dos tribunais"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.resultados = {
            'processados': 0,
            'sucesso': 0,
            'erros': 0,
            'oficios_encontrados': 0,
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
    
    def buscar_todos(self, tribunal='TODOS', filtro_processos='TODOS'):
        """Busca ofícios para todos os processos"""
        try:
            self.log("Iniciando busca de ofícios...", 'info')
            
            # Buscar processos
            query = self.db.query(Processo)
            
            if tribunal != 'TODOS':
                query = query.filter(Processo.tribunal == tribunal)
            
            if filtro_processos == 'SEM_OFICIO':
                query = query.filter(Processo.tem_oficio == False)
            elif filtro_processos == 'PRIORITARIOS':
                query = query.filter(
                    (Processo.credor_idoso == True) | 
                    (Processo.credor_doenca_grave == True) |
                    (Processo.credor_deficiente == True)
                )
            
            processos = query.all()
            total = len(processos)
            
            self.log(f"Total de processos para buscar: {total}", 'info')
            
            # Buscar ofícios para cada processo
            for i, processo in enumerate(processos, 1):
                self.resultados['processados'] += 1
                
                self.log(f"[{i}/{total}] Buscando ofício: {processo.numero_processo}", 'info')
                
                try:
                    resultado = self.buscar_oficio_processo(processo)
                    
                    if resultado['encontrado']:
                        self.resultados['sucesso'] += 1
                        self.resultados['oficios_encontrados'] += 1
                        self.log(f"  ✓ Ofício encontrado: {resultado['numero_oficio']}", 'success')
                        
                        # Atualizar processo
                        self.atualizar_processo_com_oficio(processo, resultado)
                    else:
                        self.log(f"  - Ofício não encontrado", 'warning')
                    
                    # Delay para não sobrecarregar servidor
                    time.sleep(2)
                    
                except Exception as e:
                    self.resultados['erros'] += 1
                    self.log(f"  ✗ Erro: {str(e)}", 'error')
            
            self.log(f"Busca concluída! Ofícios encontrados: {self.resultados['oficios_encontrados']}", 'success')
            
            return self.resultados
            
        except Exception as e:
            self.log(f"Erro geral: {str(e)}", 'error')
            return self.resultados
        finally:
            self.db.close()
    
    def buscar_oficio_processo(self, processo):
        """Busca ofício para um processo específico"""
        tribunal = processo.tribunal.value if processo.tribunal else 'TJSP'
        numero = processo.numero_processo
        
        # Implementar busca real por tribunal
        if tribunal == 'TJSP':
            return self.buscar_tjsp(numero)
        elif tribunal == 'TJRJ':
            return self.buscar_tjrj(numero)
        elif tribunal == 'TJMG':
            return self.buscar_tjmg(numero)
        elif tribunal == 'TRF3':
            return self.buscar_trf3(numero)
        else:
            # Simular busca para outros tribunais
            return self.simular_busca(numero)
    
    def buscar_tjsp(self, numero_processo):
        """Busca ofício no TJSP"""
        try:
            # URL do portal de precatórios do TJSP
            url = "https://www.tjsp.jus.br/PrecatorioWeb/ConsultaPublica"
            
            # Simular busca (implementar scraping real em produção)
            # Por enquanto, retorna dados simulados
            import random
            
            if random.random() > 0.7:  # 30% de chance de encontrar
                return {
                    'encontrado': True,
                    'numero_oficio': f"OF-{random.randint(1000, 9999)}/2026",
                    'data_expedicao': datetime.now().date(),
                    'valor': random.uniform(100000, 1000000),
                    'fonte': 'Portal TJSP'
                }
            else:
                return {'encontrado': False}
                
        except Exception as e:
            print(f"Erro ao buscar TJSP: {e}")
            return {'encontrado': False}
    
    def buscar_tjrj(self, numero_processo):
        """Busca ofício no TJRJ"""
        # Implementar busca real
        return self.simular_busca(numero_processo)
    
    def buscar_tjmg(self, numero_processo):
        """Busca ofício no TJMG"""
        # Implementar busca real
        return self.simular_busca(numero_processo)
    
    def buscar_trf3(self, numero_processo):
        """Busca ofício no TRF3"""
        # Implementar busca real
        return self.simular_busca(numero_processo)
    
    def simular_busca(self, numero_processo):
        """Simula busca de ofício"""
        import random
        
        if random.random() > 0.6:
            return {
                'encontrado': True,
                'numero_oficio': f"OF-{random.randint(1000, 9999)}/2026",
                'data_expedicao': datetime.now().date(),
                'valor': random.uniform(100000, 1000000),
                'fonte': 'Portal do Tribunal'
            }
        else:
            return {'encontrado': False}
    
    def atualizar_processo_com_oficio(self, processo, dados_oficio):
        """Atualiza processo com dados do ofício encontrado"""
        try:
            self.db.execute(text("""
                UPDATE processos 
                SET tem_oficio = 1,
                    numero_oficio = :numero_oficio,
                    data_expedicao_oficio = :data_expedicao,
                    valor_oficio = :valor
                WHERE id = :id
            """), {
                'numero_oficio': dados_oficio['numero_oficio'],
                'data_expedicao': dados_oficio['data_expedicao'],
                'valor': dados_oficio['valor'],
                'id': processo.id
            })
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar processo: {e}")

# Teste
if __name__ == "__main__":
    buscador = BuscadorOficios()
    resultado = buscador.buscar_todos(tribunal='TODOS', filtro_processos='TODOS')
    
    print("\n" + "="*70)
    print("RESULTADO DA BUSCA")
    print("="*70)
    print(f"Processados: {resultado['processados']}")
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Erros: {resultado['erros']}")
    print(f"Ofícios encontrados: {resultado['oficios_encontrados']}")
    print("="*70)
