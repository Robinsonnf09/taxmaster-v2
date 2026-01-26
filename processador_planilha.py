"""
Processador de planilhas com dados de precatórios
"""

import pandas as pd
import openpyxl
from datetime import datetime

class ProcessadorPlanilha:
    def __init__(self, arquivo_path):
        self.arquivo = arquivo_path
        self.df = None
        self.resultados = []
        
    def carregar_planilha(self):
        """Carrega planilha Excel ou CSV"""
        try:
            if self.arquivo.endswith('.xlsx') or self.arquivo.endswith('.xls'):
                self.df = pd.read_excel(self.arquivo)
            elif self.arquivo.endswith('.csv'):
                self.df = pd.read_csv(self.arquivo)
            else:
                return {
                    'sucesso': False,
                    'erro': 'Formato não suportado. Use .xlsx, .xls ou .csv'
                }
            
            return {
                'sucesso': True,
                'total_processos': len(self.df),
                'colunas': list(self.df.columns)
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def validar_colunas(self, colunas_obrigatorias):
        """Valida se planilha tem colunas necessárias"""
        if self.df is None:
            return False
        
        colunas_faltando = []
        for col in colunas_obrigatorias:
            if col not in self.df.columns:
                colunas_faltando.append(col)
        
        if colunas_faltando:
            return {
                'valido': False,
                'colunas_faltando': colunas_faltando
            }
        
        return {'valido': True}
    
    def obter_processos(self):
        """Retorna lista de processos"""
        if self.df is None:
            return []
        
        processos = []
        for idx, row in self.df.iterrows():
            processo = {
                'numero_processo': str(row.get('numero_processo', '')),
                'tribunal': str(row.get('tribunal', '')),
                'valor': row.get('valor', 0),
                'linha': idx + 2  # +2 porque Excel começa em 1 e tem header
            }
            processos.append(processo)
        
        return processos
    
    def adicionar_resultado(self, linha, status, mensagem, arquivo_baixado=None):
        """Adiciona resultado da busca"""
        self.resultados.append({
            'linha': linha,
            'status': status,
            'mensagem': mensagem,
            'arquivo': arquivo_baixado,
            'timestamp': datetime.now().isoformat()
        })
    
    def gerar_relatorio(self, caminho_saida):
        """Gera relatório Excel com resultados"""
        try:
            df_resultados = pd.DataFrame(self.resultados)
            df_resultados.to_excel(caminho_saida, index=False)
            
            return {
                'sucesso': True,
                'arquivo': caminho_saida
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
