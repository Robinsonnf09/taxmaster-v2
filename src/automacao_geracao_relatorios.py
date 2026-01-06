"""
Módulo de Automação - Geração Automática de Relatórios
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models import Processo
from sqlalchemy import text
from datetime import datetime
import pandas as pd

class GeradorRelatorios:
    """Gera relatórios automáticos"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.resultados = {
            'processados': 0,
            'sucesso': 0,
            'erros': 0,
            'relatorios_gerados': [],
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
    
    def gerar_todos(self, tribunal='TODOS'):
        """Gera todos os relatórios"""
        try:
            self.log("Iniciando geração de relatórios...", 'info')
            
            # Gerar relatório geral
            self.gerar_relatorio_geral(tribunal)
            
            # Gerar relatório por tribunal
            self.gerar_relatorio_por_tribunal()
            
            # Gerar relatório por natureza
            self.gerar_relatorio_por_natureza()
            
            # Gerar relatório de valores
            self.gerar_relatorio_valores()
            
            self.log(f"Relatórios gerados: {len(self.resultados['relatorios_gerados'])}", 'success')
            
            return self.resultados
            
        except Exception as e:
            self.log(f"Erro geral: {str(e)}", 'error')
            return self.resultados
        finally:
            self.db.close()
    
    def gerar_relatorio_geral(self, tribunal='TODOS'):
        """Gera relatório geral"""
        try:
            self.log("Gerando relatório geral...", 'info')
            
            query = """
                SELECT 
                    numero_processo,
                    tribunal,
                    credor_nome,
                    valor_atualizado,
                    natureza,
                    status,
                    tem_oficio
                FROM processos
            """
            
            if tribunal != 'TODOS':
                query += f" WHERE tribunal = '{tribunal}'"
            
            df = pd.read_sql(query, self.db.bind)
            
            # Salvar Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_geral_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            
            self.resultados['relatorios_gerados'].append(filename)
            self.log(f"  ✓ Relatório salvo: {filename}", 'success')
            
        except Exception as e:
            self.log(f"  ✗ Erro: {str(e)}", 'error')
    
    def gerar_relatorio_por_tribunal(self):
        """Gera relatório por tribunal"""
        try:
            self.log("Gerando relatório por tribunal...", 'info')
            
            query = """
                SELECT 
                    tribunal,
                    COUNT(*) as total_processos,
                    SUM(valor_atualizado) as valor_total,
                    SUM(CASE WHEN tem_oficio = 1 THEN 1 ELSE 0 END) as com_oficio
                FROM processos
                GROUP BY tribunal
            """
            
            df = pd.read_sql(query, self.db.bind)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_por_tribunal_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            
            self.resultados['relatorios_gerados'].append(filename)
            self.log(f"  ✓ Relatório salvo: {filename}", 'success')
            
        except Exception as e:
            self.log(f"  ✗ Erro: {str(e)}", 'error')
    
    def gerar_relatorio_por_natureza(self):
        """Gera relatório por natureza"""
        try:
            self.log("Gerando relatório por natureza...", 'info')
            
            query = """
                SELECT 
                    natureza,
                    COUNT(*) as total_processos,
                    SUM(valor_atualizado) as valor_total
                FROM processos
                GROUP BY natureza
            """
            
            df = pd.read_sql(query, self.db.bind)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_por_natureza_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            
            self.resultados['relatorios_gerados'].append(filename)
            self.log(f"  ✓ Relatório salvo: {filename}", 'success')
            
        except Exception as e:
            self.log(f"  ✗ Erro: {str(e)}", 'error')
    
    def gerar_relatorio_valores(self):
        """Gera relatório de valores"""
        try:
            self.log("Gerando relatório de valores...", 'info')
            
            query = """
                SELECT 
                    numero_processo,
                    valor_principal,
                    valor_juros,
                    valor_correcao_monetaria,
                    valor_atualizado,
                    data_ultima_atualizacao_valor
                FROM processos
                WHERE valor_atualizado IS NOT NULL
            """
            
            df = pd.read_sql(query, self.db.bind)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_valores_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            
            self.resultados['relatorios_gerados'].append(filename)
            self.log(f"  ✓ Relatório salvo: {filename}", 'success')
            
        except Exception as e:
            self.log(f"  ✗ Erro: {str(e)}", 'error')

# Teste
if __name__ == "__main__":
    gerador = GeradorRelatorios()
    resultado = gerador.gerar_todos()
    
    print("\n" + "="*70)
    print("RESULTADO DA GERAÇÃO")
    print("="*70)
    print(f"Relatórios gerados: {len(resultado['relatorios_gerados'])}")
    for rel in resultado['relatorios_gerados']:
        print(f"  - {rel}")
    print("="*70)
