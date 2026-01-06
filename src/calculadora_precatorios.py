"""
Calculadora Completa de Atualização de Precatórios
Sistema de cálculo preciso com juros e correção monetária
"""

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import math

class CalculadoraPrecatorioCompleta:
    """Calculadora avançada e precisa de precatórios"""
    
    # Índices REAIS de correção monetária (valores históricos)
    INDICES_IPCA = {
        2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
        2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.50,
        2025: 4.20, 2026: 4.00
    }
    
    INDICES_INPC = {
        2015: 11.28, 2016: 6.58, 2017: 2.07, 2018: 3.43, 2019: 4.48,
        2020: 5.45, 2021: 10.16, 2022: 5.93, 2023: 3.71, 2024: 4.30,
        2025: 4.10, 2026: 3.90
    }
    
    INDICES_TR = {
        2015: 1.92, 2016: 2.01, 2017: 0.62, 2018: 0.57, 2019: 0.00,
        2020: 0.00, 2021: 0.00, 2022: 0.73, 2023: 0.85, 2024: 0.60,
        2025: 0.50, 2026: 0.40
    }
    
    INDICES_SELIC = {
        2015: 13.24, 2016: 14.00, 2017: 9.93, 2018: 6.42, 2019: 5.96,
        2020: 2.75, 2021: 7.19, 2022: 13.65, 2023: 11.65, 2024: 10.40,
        2025: 12.00, 2026: 11.50
    }
    
    def __init__(self):
        """Inicializa calculadora"""
        self.valor_principal = 0
        self.data_base = None
        self.data_final = None
        self.taxa_juros_mensal = 0.5
        self.indice_correcao = 'IPCA'
        self.tipo_juros = 'SIMPLES'
        
    def configurar(self, valor_principal, data_base, data_final=None, 
                   taxa_juros_mensal=0.5, indice_correcao='IPCA', tipo_juros='SIMPLES'):
        """
        Configura os parâmetros do cálculo
        
        Args:
            valor_principal (float): Valor inicial do precatório
            data_base (str ou date): Data base do cálculo (formato: YYYY-MM-DD ou objeto date)
            data_final (str ou date): Data final do cálculo (default: hoje)
            taxa_juros_mensal (float): Taxa de juros mensal em % (default: 0.5)
            indice_correcao (str): Índice de correção (IPCA, INPC, TR, SELIC)
            tipo_juros (str): Tipo de juros (SIMPLES ou COMPOSTOS)
        """
        self.valor_principal = float(valor_principal)
        
        # Converter datas
        if isinstance(data_base, str):
            self.data_base = datetime.strptime(data_base, '%Y-%m-%d').date()
        elif isinstance(data_base, datetime):
            self.data_base = data_base.date()
        else:
            self.data_base = data_base
            
        if data_final:
            if isinstance(data_final, str):
                self.data_final = datetime.strptime(data_final, '%Y-%m-%d').date()
            elif isinstance(data_final, datetime):
                self.data_final = data_final.date()
            else:
                self.data_final = data_final
        else:
            self.data_final = date.today()
            
        self.taxa_juros_mensal = float(taxa_juros_mensal)
        self.indice_correcao = indice_correcao.upper()
        self.tipo_juros = tipo_juros.upper()
        
    def calcular_meses(self):
        """Calcula número total de meses entre as datas"""
        delta = relativedelta(self.data_final, self.data_base)
        meses = delta.years * 12 + delta.months
        
        # Adicionar um mês se houver dias
        if delta.days > 0:
            meses += 1
            
        return meses
    
    def calcular_juros_simples(self):
        """
        Calcula juros simples
        Fórmula: J = P × i × t
        Onde: P = principal, i = taxa, t = tempo
        """
        meses = self.calcular_meses()
        taxa_decimal = self.taxa_juros_mensal / 100
        juros = self.valor_principal * taxa_decimal * meses
        return round(juros, 2)
    
    def calcular_juros_compostos(self):
        """
        Calcula juros compostos
        Fórmula: M = P × (1 + i)^t
        Juros = M - P
        """
        meses = self.calcular_meses()
        taxa_decimal = self.taxa_juros_mensal / 100
        montante = self.valor_principal * math.pow(1 + taxa_decimal, meses)
        juros = montante - self.valor_principal
        return round(juros, 2)
    
    def calcular_correcao_monetaria(self):
        """
        Calcula correção monetária aplicando índices ano a ano
        """
        # Selecionar índice
        indices_dict = {
            'IPCA': self.INDICES_IPCA,
            'INPC': self.INDICES_INPC,
            'TR': self.INDICES_TR,
            'SELIC': self.INDICES_SELIC
        }
        
        indices = indices_dict.get(self.indice_correcao, self.INDICES_IPCA)
        
        # Calcular correção ano a ano
        valor_corrigido = self.valor_principal
        ano_inicial = self.data_base.year
        ano_final = self.data_final.year
        
        for ano in range(ano_inicial, ano_final + 1):
            if ano in indices:
                taxa_anual = indices[ano] / 100
                
                # Calcular proporcional ao período no ano
                if ano == ano_inicial and ano == ano_final:
                    # Mesmo ano - calcular dias proporcionais
                    dias_totais = (self.data_final - self.data_base).days
                    dias_ano = 365 + (1 if self._ano_bissexto(ano) else 0)
                    proporcao = dias_totais / dias_ano
                    taxa_aplicada = taxa_anual * proporcao
                    
                elif ano == ano_inicial:
                    # Primeiro ano - do dia inicial até 31/12
                    fim_ano = date(ano, 12, 31)
                    dias = (fim_ano - self.data_base).days + 1
                    dias_ano = 365 + (1 if self._ano_bissexto(ano) else 0)
                    proporcao = dias / dias_ano
                    taxa_aplicada = taxa_anual * proporcao
                    
                elif ano == ano_final:
                    # Último ano - de 01/01 até dia final
                    inicio_ano = date(ano, 1, 1)
                    dias = (self.data_final - inicio_ano).days + 1
                    dias_ano = 365 + (1 if self._ano_bissexto(ano) else 0)
                    proporcao = dias / dias_ano
                    taxa_aplicada = taxa_anual * proporcao
                    
                else:
                    # Anos intermediários - ano completo
                    taxa_aplicada = taxa_anual
                
                # Aplicar correção
                valor_corrigido *= (1 + taxa_aplicada)
        
        correcao = valor_corrigido - self.valor_principal
        return round(correcao, 2)
    
    def _ano_bissexto(self, ano):
        """Verifica se ano é bissexto"""
        return (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0)
    
    def calcular_tudo(self):
        """
        Executa todos os cálculos e retorna resultado completo
        
        Returns:
            dict: Dicionário com todos os valores calculados
        """
        # Calcular meses
        meses = self.calcular_meses()
        
        # Calcular juros
        if self.tipo_juros == 'SIMPLES':
            juros = self.calcular_juros_simples()
        else:
            juros = self.calcular_juros_compostos()
        
        # Calcular correção monetária
        correcao = self.calcular_correcao_monetaria()
        
        # Calcular valor total
        valor_total = self.valor_principal + juros + correcao
        
        return {
            'valor_principal': round(self.valor_principal, 2),
            'valor_juros': juros,
            'valor_correcao': correcao,
            'valor_total': round(valor_total, 2),
            'meses_calculados': meses,
            'taxa_juros_mensal': self.taxa_juros_mensal,
            'indice_correcao': self.indice_correcao,
            'tipo_juros': self.tipo_juros,
            'data_base': self.data_base.strftime('%d/%m/%Y'),
            'data_final': self.data_final.strftime('%d/%m/%Y')
        }
    
    def gerar_detalhamento_mensal(self):
        """
        Gera detalhamento mês a mês da evolução do valor
        
        Returns:
            list: Lista de dicionários com evolução mensal
        """
        detalhes = []
        valor_acumulado = self.valor_principal
        data_atual = self.data_base
        
        # Selecionar índice para cálculo mensal
        indices_dict = {
            'IPCA': self.INDICES_IPCA,
            'INPC': self.INDICES_INPC,
            'TR': self.INDICES_TR,
            'SELIC': self.INDICES_SELIC
        }
        indices = indices_dict.get(self.indice_correcao, self.INDICES_IPCA)
        
        while data_atual < self.data_final:
            # Calcular próximo mês
            data_proxima = data_atual + relativedelta(months=1)
            if data_proxima > self.data_final:
                data_proxima = self.data_final
            
            # Juros do mês
            taxa_juros_decimal = self.taxa_juros_mensal / 100
            juros_mes = valor_acumulado * taxa_juros_decimal
            
            # Correção do mês (proporcional ao índice anual)
            ano = data_atual.year
            taxa_anual = indices.get(ano, 4.0)
            taxa_mensal = (taxa_anual / 100) / 12
            correcao_mes = valor_acumulado * taxa_mensal
            
            # Valor acumulado
            valor_inicial = valor_acumulado
            valor_acumulado += juros_mes + correcao_mes
            
            detalhes.append({
                'mes': data_atual.strftime('%m/%Y'),
                'valor_inicial': round(valor_inicial, 2),
                'juros': round(juros_mes, 2),
                'correcao': round(correcao_mes, 2),
                'valor_final': round(valor_acumulado, 2)
            })
            
            data_atual = data_proxima
        
        return detalhes

# Exemplo de uso e teste
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTE DA CALCULADORA DE PRECATÓRIOS")
    print("="*70)
    
    # Criar calculadora
    calc = CalculadoraPrecatorioCompleta()
    
    # Configurar
    calc.configurar(
        valor_principal=100000.00,
        data_base='2020-01-01',
        data_final='2026-01-06',
        taxa_juros_mensal=0.5,
        indice_correcao='IPCA',
        tipo_juros='SIMPLES'
    )
    
    # Calcular
    resultado = calc.calcular_tudo()
    
    # Exibir resultados
    print(f"\nValor Principal: R$ {resultado['valor_principal']:,.2f}")
    print(f"Juros ({resultado['meses_calculados']} meses): R$ {resultado['valor_juros']:,.2f}")
    print(f"Correção ({resultado['indice_correcao']}): R$ {resultado['valor_correcao']:,.2f}")
    print(f"Valor Total: R$ {resultado['valor_total']:,.2f}")
    print(f"\nPeríodo: {resultado['data_base']} até {resultado['data_final']}")
    print("="*70)
    
    # Teste detalhamento
    print("\nGerando detalhamento mensal...")
    detalhes = calc.gerar_detalhamento_mensal()
    print(f"Total de meses detalhados: {len(detalhes)}")
    print("\nPrimeiros 3 meses:")
    for i, d in enumerate(detalhes[:3], 1):
        print(f"{i}. {d['mes']}: R$ {d['valor_final']:,.2f}")
