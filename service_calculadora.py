import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
sys.path.append('src')
from calculadora import calculadora

class CalculadoraService:
    """Serviço avançado de cálculo de precatórios"""
    
    INDICES_DISPONIVEIS = {
        'IPCA-E': 'Índice de Preços ao Consumidor Amplo Especial',
        'INPC': 'Índice Nacional de Preços ao Consumidor',
        'SELIC': 'Taxa Selic',
        'TR': 'Taxa Referencial',
        'IGPM': 'Índice Geral de Preços do Mercado'
    }
    
    @staticmethod
    def validar_dados(dados: Dict) -> tuple[bool, Optional[str]]:
        """Valida dados de entrada"""
        erros = []
        
        # Validar valor original
        try:
            valor = float(dados.get('valor_original', 0))
            if valor <= 0:
                erros.append("Valor original deve ser maior que zero")
        except (ValueError, TypeError):
            erros.append("Valor original inválido")
        
        # Validar índice
        indice = dados.get('indice_correcao', '')
        if indice not in CalculadoraService.INDICES_DISPONIVEIS:
            erros.append(f"Índice {indice} não disponível")
        
        # Validar datas
        try:
            data_inicial = datetime.strptime(dados.get('data_inicial', ''), '%Y-%m-%d')
            data_final = datetime.strptime(dados.get('data_final', ''), '%Y-%m-%d')
            
            if data_inicial >= data_final:
                erros.append("Data inicial deve ser anterior à data final")
            
            if data_final > datetime.now():
                erros.append("Data final não pode ser futura")
                
        except ValueError:
            erros.append("Formato de data inválido (use YYYY-MM-DD)")
        
        # Validar taxa de juros
        if dados.get('incluir_juros'):
            try:
                taxa = float(dados.get('taxa_juros', 0))
                if taxa < 0 or taxa > 100:
                    erros.append("Taxa de juros deve estar entre 0 e 100")
            except (ValueError, TypeError):
                erros.append("Taxa de juros inválida")
        
        # Validar honorários
        try:
            honorarios = float(dados.get('percentual_honorarios', 0))
            if honorarios < 0 or honorarios > 100:
                erros.append("Honorários devem estar entre 0 e 100")
        except (ValueError, TypeError):
            erros.append("Percentual de honorários inválido")
        
        if erros:
            return False, "; ".join(erros)
        
        return True, None
    
    @staticmethod
    def calcular(dados: Dict) -> Dict:
        """Realiza cálculo completo"""
        
        # Validar
        valido, erro = CalculadoraService.validar_dados(dados)
        if not valido:
            return {'sucesso': False, 'erro': erro}
        
        try:
            # Preparar dados para calculadora
            calc_data = {
                'valor_original': float(dados['valor_original']),
                'indice': dados['indice_correcao'],
                'data_inicial': dados['data_inicial'],
                'data_final': dados['data_final'],
                'incluir_juros': dados.get('incluir_juros', False),
                'taxa_juros': float(dados.get('taxa_juros', 0)),
                'honorarios': float(dados.get('percentual_honorarios', 0))
            }
            
            # Chamar função de cálculo
            resultado = calculadora(calc_data)
            
            if not resultado or 'erro' in resultado:
                return {
                    'sucesso': False,
                    'erro': resultado.get('erro', 'Erro desconhecido no cálculo')
                }
            
            # Adicionar metadados
            resultado['sucesso'] = True
            resultado['dados_entrada'] = dados
            resultado['timestamp'] = datetime.now().isoformat()
            
            return resultado
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao processar cálculo: {str(e)}'
            }
    
    @staticmethod
    def comparar_indices(dados: Dict, indices: List[str]) -> Dict:
        """Compara resultado entre múltiplos índices"""
        resultados = {}
        
        for indice in indices:
            dados_calculo = dados.copy()
            dados_calculo['indice_correcao'] = indice
            
            resultado = CalculadoraService.calcular(dados_calculo)
            
            if resultado.get('sucesso'):
                resultados[indice] = {
                    'valor_corrigido': resultado.get('valor_corrigido', 0),
                    'valor_final': resultado.get('valor_liquido', 0),
                    'diferenca_percentual': ((resultado.get('valor_liquido', 0) / 
                                             dados['valor_original']) - 1) * 100
                }
        
        return {
            'sucesso': True,
            'comparacao': resultados,
            'melhor_indice': max(resultados.items(), 
                               key=lambda x: x[1]['valor_final'])[0] if resultados else None
        }
    
    @staticmethod
    def gerar_resumo(resultado: Dict) -> str:
        """Gera resumo textual do cálculo"""
        if not resultado.get('sucesso'):
            return f"Erro: {resultado.get('erro', 'Desconhecido')}"
        
        resumo = f"""
RESUMO DO CÁLCULO

Valor Original: R$ {resultado.get('valor_original', 0):,.2f}
Índice: {resultado.get('indice', 'N/A')}
Período: {resultado.get('data_inicial', 'N/A')} até {resultado.get('data_final', 'N/A')}

RESULTADOS:
Valor Corrigido: R$ {resultado.get('valor_corrigido', 0):,.2f}
Juros de Mora: R$ {resultado.get('valor_juros', 0):,.2f}
Honorários: R$ {resultado.get('valor_honorarios', 0):,.2f}
VALOR LÍQUIDO: R$ {resultado.get('valor_liquido', 0):,.2f}

Correção: {((resultado.get('valor_corrigido', 0) / resultado.get('valor_original', 1)) - 1) * 100:.2f}%
        """
        
        return resumo.strip()
