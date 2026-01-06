"""
Módulo de Automação - Atualização Automática de Valores
"""

import sys
sys.path.append("src")

from database import SessionLocal
from models import Processo
from calculadora_juros import CalculadoraPrecatorio
from sqlalchemy import text
from datetime import datetime, date

class AtualizadorValores:
    """Atualiza valores automaticamente com juros e correção"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.resultados = {
            'processados': 0,
            'sucesso': 0,
            'erros': 0,
            'valor_total_atualizado': 0,
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
    
    def atualizar_todos(self, tribunal='TODOS', filtro_processos='TODOS'):
        """Atualiza valores de todos os processos"""
        try:
            self.log("Iniciando atualização de valores...", 'info')
            
            # Buscar processos
            query = self.db.query(Processo)
            
            if tribunal != 'TODOS':
                query = query.filter(Processo.tribunal == tribunal)
            
            processos = query.all()
            total = len(processos)
            
            self.log(f"Total de processos para atualizar: {total}", 'info')
            
            # Atualizar cada processo
            for i, processo in enumerate(processos, 1):
                self.resultados['processados'] += 1
                
                self.log(f"[{i}/{total}] Atualizando: {processo.numero_processo}", 'info')
                
                try:
                    resultado = self.atualizar_processo(processo)
                    
                    if resultado['sucesso']:
                        self.resultados['sucesso'] += 1
                        self.resultados['valor_total_atualizado'] += resultado['valor_total']
                        self.log(f"  ✓ Valor atualizado: R$ {resultado['valor_total']:,.2f}", 'success')
                    else:
                        self.log(f"  - Não foi possível atualizar", 'warning')
                    
                except Exception as e:
                    self.resultados['erros'] += 1
                    self.log(f"  ✗ Erro: {str(e)}", 'error')
            
            self.log(f"Atualização concluída! Valor total: R$ {self.resultados['valor_total_atualizado']:,.2f}", 'success')
            
            return self.resultados
            
        except Exception as e:
            self.log(f"Erro geral: {str(e)}", 'error')
            return self.resultados
        finally:
            self.db.close()
    
    def atualizar_processo(self, processo):
        """Atualiza valores de um processo específico"""
        try:
            # Verificar se tem valor principal
            if not processo.valor_atualizado:
                return {'sucesso': False}
            
            # Definir data base (usar data de cadastro ou data específica)
            data_base = processo.data_base_calculo or processo.data_cadastro or date(2020, 1, 1)
            data_final = date.today()
            
            # Criar calculadora
            calc = CalculadoraPrecatorio(
                valor_principal=float(processo.valor_atualizado),
                data_base=data_base,
                data_final=data_final,
                taxa_juros_mensal=processo.taxa_juros_mensal or 0.5,
                indice_correcao=processo.indice_correcao or 'IPCA'
            )
            
            # Calcular valores
            resultado = calc.calcular_tudo(tipo_juros='SIMPLES')
            
            # Atualizar no banco
            self.db.execute(text("""
                UPDATE processos 
                SET valor_principal = :valor_principal,
                    valor_juros = :valor_juros,
                    valor_correcao_monetaria = :valor_correcao,
                    valor_atualizado = :valor_total,
                    data_ultima_atualizacao_valor = :data_atualizacao
                WHERE id = :id
            """), {
                'valor_principal': resultado['valor_principal'],
                'valor_juros': resultado['valor_juros'],
                'valor_correcao': resultado['valor_correcao'],
                'valor_total': resultado['valor_total'],
                'data_atualizacao': datetime.now(),
                'id': processo.id
            })
            
            # Salvar no histórico
            self.db.execute(text("""
                INSERT INTO historico_valores 
                (processo_id, data_atualizacao, valor_principal, valor_juros, 
                 valor_correcao, valor_total, taxa_juros, indice_correcao, 
                 periodo_inicio, periodo_fim, usuario)
                VALUES 
                (:processo_id, :data_atualizacao, :valor_principal, :valor_juros,
                 :valor_correcao, :valor_total, :taxa_juros, :indice_correcao,
                 :periodo_inicio, :periodo_fim, :usuario)
            """), {
                'processo_id': processo.id,
                'data_atualizacao': datetime.now(),
                'valor_principal': resultado['valor_principal'],
                'valor_juros': resultado['valor_juros'],
                'valor_correcao': resultado['valor_correcao'],
                'valor_total': resultado['valor_total'],
                'taxa_juros': resultado['taxa_juros_mensal'],
                'indice_correcao': resultado['indice_correcao'],
                'periodo_inicio': data_base,
                'periodo_fim': data_final,
                'usuario': 'Sistema Automático'
            })
            
            self.db.commit()
            
            return {
                'sucesso': True,
                'valor_total': resultado['valor_total']
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar processo: {e}")
            return {'sucesso': False}

# Teste
if __name__ == "__main__":
    atualizador = AtualizadorValores()
    resultado = atualizador.atualizar_todos()
    
    print("\n" + "="*70)
    print("RESULTADO DA ATUALIZAÇÃO")
    print("="*70)
    print(f"Processados: {resultado['processados']}")
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Erros: {resultado['erros']}")
    print(f"Valor Total: R$ {resultado['valor_total_atualizado']:,.2f}")
    print("="*70)
