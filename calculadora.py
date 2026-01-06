"""
Módulo de Calculadora de Atualização de Precatórios
Tax Master - Sistema de Gestão de Precatórios
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
import math

class CalculadoraPrecatorio:
    """
    Calculadora completa para atualização de valores de precatórios
    com suporte a múltiplos índices e juros
    """
    
    # Taxas mensais médias (valores aproximados - devem ser atualizados com API real)
    INDICES_MENSAIS = {
        'IPCA-E': {
            '2024-01': 0.42, '2024-02': 0.84, '2024-03': 0.16, '2024-04': 0.38,
            '2024-05': 0.46, '2024-06': 0.21, '2024-07': 0.38, '2024-08': -0.02,
            '2024-09': 0.44, '2024-10': 0.56, '2024-11': 0.62, '2024-12': 0.52,
            '2025-01': 0.50, '2025-02': 0.45, '2025-03': 0.40, '2025-04': 0.42,
            '2025-05': 0.48, '2025-06': 0.35, '2025-07': 0.38, '2025-08': 0.30,
            '2025-09': 0.40, '2025-10': 0.50, '2025-11': 0.55, '2025-12': 0.45,
            '2026-01': 0.43
        },
        'INPC': {
            '2024-01': 0.42, '2024-02': 0.78, '2024-03': 0.16, '2024-04': 0.38,
            '2024-05': 0.46, '2024-06': 0.21, '2024-07': 0.38, '2024-08': -0.02,
            '2024-09': 0.44, '2024-10': 0.61, '2024-11': 0.64, '2024-12': 0.52,
            '2025-01': 0.48, '2025-02': 0.43, '2025-03': 0.38, '2025-04': 0.40,
            '2025-05': 0.46, '2025-06': 0.33, '2025-07': 0.36, '2025-08': 0.28,
            '2025-09': 0.38, '2025-10': 0.48, '2025-11': 0.53, '2025-12': 0.43,
            '2026-01': 0.41
        },
        'TR': {
            '2024-01': 0.00, '2024-02': 0.00, '2024-03': 0.00, '2024-04': 0.00,
            '2024-05': 0.00, '2024-06': 0.00, '2024-07': 0.00, '2024-08': 0.00,
            '2024-09': 0.00, '2024-10': 0.00, '2024-11': 0.00, '2024-12': 0.00,
            '2025-01': 0.00, '2025-02': 0.00, '2025-03': 0.00, '2025-04': 0.00,
            '2025-05': 0.00, '2025-06': 0.00, '2025-07': 0.00, '2025-08': 0.00,
            '2025-09': 0.00, '2025-10': 0.00, '2025-11': 0.00, '2025-12': 0.00,
            '2026-01': 0.00
        },
        'SELIC': {
            '2024-01': 0.92, '2024-02': 0.82, '2024-03': 0.86, '2024-04': 0.88,
            '2024-05': 0.86, '2024-06': 0.88, '2024-07': 0.88, '2024-08': 0.88,
            '2024-09': 0.88, '2024-10': 0.90, '2024-11': 0.92, '2024-12': 0.96,
            '2025-01': 1.00, '2025-02': 1.02, '2025-03': 1.04, '2025-04': 1.06,
            '2025-05': 1.08, '2025-06': 1.10, '2025-07': 1.12, '2025-08': 1.14,
            '2025-09': 1.16, '2025-10': 1.18, '2025-11': 1.20, '2025-12': 1.22,
            '2026-01': 1.24
        },
        'POUPANCA': {
            '2024-01': 0.58, '2024-02': 0.58, '2024-03': 0.59, '2024-04': 0.60,
            '2024-05': 0.59, '2024-06': 0.60, '2024-07': 0.60, '2024-08': 0.60,
            '2024-09': 0.60, '2024-10': 0.61, '2024-11': 0.62, '2024-12': 0.65,
            '2025-01': 0.68, '2025-02': 0.69, '2025-03': 0.70, '2025-04': 0.72,
            '2025-05': 0.73, '2025-06': 0.75, '2025-07': 0.76, '2025-08': 0.77,
            '2025-09': 0.79, '2025-10': 0.80, '2025-11': 0.81, '2025-12': 0.83,
            '2026-01': 0.84
        },
        'IGP-DI': {
            '2024-01': 0.41, '2024-02': 0.52, '2024-03': 0.40, '2024-04': 0.38,
            '2024-05': 0.46, '2024-06': 0.50, '2024-07': 0.55, '2024-08': 0.12,
            '2024-09': 0.62, '2024-10': 1.54, '2024-11': 1.18, '2024-12': 0.87,
            '2025-01': 0.45, '2025-02': 0.50, '2025-03': 0.48, '2025-04': 0.52,
            '2025-05': 0.55, '2025-06': 0.45, '2025-07': 0.50, '2025-08': 0.40,
            '2025-09': 0.48, '2025-10': 0.60, '2025-11': 0.65, '2025-12': 0.55,
            '2026-01': 0.50
        }
    }
    
    def __init__(self):
        self.valor_original = Decimal('0')
        self.data_inicial = None
        self.data_final = None
        self.indice = 'IPCA-E'
        self.taxa_juros_mora = Decimal('1.0')  # 1% ao mês
        self.taxa_juros_compensatorios = Decimal('0.5')  # 6% ao ano = 0.5% ao mês
        self.taxa_honorarios = Decimal('0')
        
    def calcular_correcao_monetaria(self, valor, data_inicio, data_fim, indice='IPCA-E'):
        """
        Calcula a correção monetária entre duas datas
        """
        valor_decimal = Decimal(str(valor))
        data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_final = datetime.strptime(data_fim, '%Y-%m-%d')
        
        valor_corrigido = valor_decimal
        detalhamento = []
        
        while data_atual <= data_final:
            mes_ano = data_atual.strftime('%Y-%m')
            
            if mes_ano in self.INDICES_MENSAIS.get(indice, {}):
                taxa = Decimal(str(self.INDICES_MENSAIS[indice][mes_ano])) / Decimal('100')
                valor_mes = valor_corrigido * taxa
                valor_corrigido += valor_mes
                
                detalhamento.append({
                    'mes': data_atual.strftime('%m/%Y'),
                    'indice': indice,
                    'taxa': float(self.INDICES_MENSAIS[indice][mes_ano]),
                    'valor_correcao': float(valor_mes.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                    'valor_acumulado': float(valor_corrigido.quantize(Decimal('0.01'), ROUND_HALF_UP))
                })
            
            # Avançar para o próximo mês
            data_atual += relativedelta(months=1)
            data_atual = data_atual.replace(day=1)
        
        return float(valor_corrigido.quantize(Decimal('0.01'), ROUND_HALF_UP)), detalhamento
    
    def calcular_juros_mora(self, valor, data_inicio, data_fim, taxa_mensal=1.0):
        """
        Calcula juros de mora (1% ao mês)
        """
        valor_decimal = Decimal(str(valor))
        taxa = Decimal(str(taxa_mensal)) / Decimal('100')
        
        data_inicial = datetime.strptime(data_inicio, '%Y-%m-%d')
        data_final = datetime.strptime(data_fim, '%Y-%m-%d')
        
        meses = relativedelta(data_final, data_inicial).months + \
                (relativedelta(data_final, data_inicial).years * 12)
        
        dias_extras = (data_final - (data_inicial + relativedelta(months=meses))).days
        taxa_dias = (taxa / Decimal('30')) * Decimal(str(dias_extras))
        
        juros_total = valor_decimal * (taxa * Decimal(str(meses)) + taxa_dias)
        
        return {
            'meses': meses,
            'dias': dias_extras,
            'taxa_mensal': float(taxa * 100),
            'valor_juros': float(juros_total.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'valor_total': float((valor_decimal + juros_total).quantize(Decimal('0.01'), ROUND_HALF_UP))
        }
    
    def calcular_honorarios(self, valor, percentual=10.0):
        """
        Calcula honorários advocatícios
        """
        valor_decimal = Decimal(str(valor))
        taxa = Decimal(str(percentual)) / Decimal('100')
        honorarios = valor_decimal * taxa
        
        return {
            'percentual': float(percentual),
            'valor_honorarios': float(honorarios.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'valor_liquido': float((valor_decimal - honorarios).quantize(Decimal('0.01'), ROUND_HALF_UP))
        }
    
    def calculo_completo(self, valor_original, data_inicio, data_fim, 
                        indice='IPCA-E', incluir_juros_mora=True, 
                        taxa_juros=1.0, percentual_honorarios=0):
        """
        Realiza cálculo completo: correção monetária + juros + honorários
        """
        # 1. Correção Monetária
        valor_corrigido, detalhamento_correcao = self.calcular_correcao_monetaria(
            valor_original, data_inicio, data_fim, indice
        )
        
        # 2. Juros de Mora (sobre valor corrigido)
        resultado_juros = None
        valor_com_juros = valor_corrigido
        
        if incluir_juros_mora:
            resultado_juros = self.calcular_juros_mora(
                valor_corrigido, data_inicio, data_fim, taxa_juros
            )
            valor_com_juros = resultado_juros['valor_total']
        
        # 3. Honorários (sobre valor corrigido + juros)
        resultado_honorarios = None
        if percentual_honorarios > 0:
            resultado_honorarios = self.calcular_honorarios(
                valor_com_juros, percentual_honorarios
            )
        
        # Resultado Final
        return {
            'valor_original': float(Decimal(str(valor_original)).quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'indice_utilizado': indice,
            'correcao_monetaria': {
                'valor_corrigido': valor_corrigido,
                'valor_correcao': valor_corrigido - float(valor_original),
                'percentual_total': ((valor_corrigido / float(valor_original)) - 1) * 100,
                'detalhamento': detalhamento_correcao
            },
            'juros_mora': resultado_juros,
            'honorarios': resultado_honorarios,
            'valor_final': resultado_honorarios['valor_liquido'] if resultado_honorarios else valor_com_juros,
            'resumo': {
                'valor_original': float(valor_original),
                'valor_corrigido': valor_corrigido,
                'valor_juros': resultado_juros['valor_juros'] if resultado_juros else 0,
                'valor_honorarios': resultado_honorarios['valor_honorarios'] if resultado_honorarios else 0,
                'valor_liquido': resultado_honorarios['valor_liquido'] if resultado_honorarios else valor_com_juros
            }
        }

# Instância global
calculadora = CalculadoraPrecatorio()
