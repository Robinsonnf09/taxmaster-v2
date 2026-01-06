"""
Calculadora de Juros e Correção Monetária para Precatórios
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math

class CalculadoraPrecatorio:
    """Calculadora avançada de valores de precatórios"""
    
    # Índices de correção (valores exemplo - atualizar com dados reais)
    INDICES_IPCA = {
        2020: 4.52,
        2021: 10.06,
        2022: 5.79,
        2023: 4.62,
        2024: 4.50,
        2025: 4.20,
        2026: 4.00
    }
    
    INDICES_INPC = {
        2020: 5.45,
        2021: 10.16,
        2022: 5.93,
        2023: 3.71,
        2024: 4.30,
        2025: 4.10,
        2026: 3.90
    }
    
    INDICES_TR = {
        2020: 0.00,
        2021: 0.00,
        2022: 0.73,
        2023: 0.85,
        2024: 0.60,
        2025: 0.50,
        2026: 0.40
    }
    
    def __init__(self, valor_principal, data_base, data_final=None, 
                 taxa_juros_mensal=0.5, indice_correcao='IPCA'):
        """
        Inicializa calculadora
        
        Args:
            valor_principal: Valor principal do precatório
            data_base: Data base para cálculo
            data_final: Data final (default: hoje)
            taxa_juros_mensal: Taxa de juros mensal (%)
            indice_correcao: Índice de correção (IPCA, INPC, TR)
        """
        self.valor_principal = float(valor_principal)
        self.data_base = data_base if isinstance(data_base, datetime) else datetime.strptime(data_base, '%Y-%m-%d')
        self.data_final = data_final if data_final else datetime.now()
        if isinstance(self.data_final, str):
            self.data_final = datetime.strptime(self.data_final, '%Y-%m-%d')
        self.taxa_juros_mensal = float(taxa_juros_mensal)
        self.indice_correcao = indice_correcao
    
    def calcular_meses(self):
        """Calcula número de meses entre datas"""
        delta = relativedelta(self.data_final, self.data_base)
        return delta.years * 12 + delta.months + (1 if delta.days > 0 else 0)
    
    def calcular_juros_simples(self):
        """Calcula juros simples"""
        meses = self.calcular_meses()
        juros = self.valor_principal * (self.taxa_juros_mensal / 100) * meses
        return round(juros, 2)
    
    def calcular_juros_compostos(self):
        """Calcula juros compostos"""
        meses = self.calcular_meses()
        taxa_decimal = self.taxa_juros_mensal / 100
        valor_final = self.valor_principal * math.pow(1 + taxa_decimal, meses)
        juros = valor_final - self.valor_principal
        return round(juros, 2)
    
    def calcular_correcao_monetaria(self):
        """Calcula correção monetária"""
        indices = {
            'IPCA': self.INDICES_IPCA,
            'INPC': self.INDICES_INPC,
            'TR': self.INDICES_TR
        }
        
        indice_selecionado = indices.get(self.indice_correcao, self.INDICES_IPCA)
        
        valor_corrigido = self.valor_principal
        ano_inicial = self.data_base.year
        ano_final = self.data_final.year
        
        for ano in range(ano_inicial, ano_final + 1):
            if ano in indice_selecionado:
                taxa = indice_selecionado[ano] / 100
                
                # Proporcional ao período no ano
                if ano == ano_inicial:
                    meses_ano = 12 - self.data_base.month + 1
                    taxa = taxa * (meses_ano / 12)
                elif ano == ano_final:
                    meses_ano = self.data_final.month
                    taxa = taxa * (meses_ano / 12)
                
                valor_corrigido *= (1 + taxa)
        
        correcao = valor_corrigido - self.valor_principal
        return round(correcao, 2)
    
    def calcular_tudo(self, tipo_juros='SIMPLES'):
        """
        Calcula todos os valores
        
        Args:
            tipo_juros: 'SIMPLES' ou 'COMPOSTOS'
        
        Returns:
            dict com todos os valores calculados
        """
        meses = self.calcular_meses()
        
        if tipo_juros == 'SIMPLES':
            juros = self.calcular_juros_simples()
        else:
            juros = self.calcular_juros_compostos()
        
        correcao = self.calcular_correcao_monetaria()
        valor_total = self.valor_principal + juros + correcao
        
        return {
            'valor_principal': round(self.valor_principal, 2),
            'valor_juros': juros,
            'valor_correcao': correcao,
            'valor_total': round(valor_total, 2),
            'meses_calculados': meses,
            'taxa_juros_mensal': self.taxa_juros_mensal,
            'indice_correcao': self.indice_correcao,
            'tipo_juros': tipo_juros,
            'data_base': self.data_base.strftime('%d/%m/%Y'),
            'data_final': self.data_final.strftime('%d/%m/%Y')
        }
    
    def gerar_detalhamento_mensal(self):
        """Gera detalhamento mês a mês"""
        detalhes = []
        valor_acumulado = self.valor_principal
        data_atual = self.data_base
        
        while data_atual < self.data_final:
            # Próximo mês
            data_proxima = data_atual + relativedelta(months=1)
            if data_proxima > self.data_final:
                data_proxima = self.data_final
            
            # Juros do mês
            juros_mes = valor_acumulado * (self.taxa_juros_mensal / 100)
            
            # Correção do mês (simplificado)
            ano = data_atual.year
            indices = {
                'IPCA': self.INDICES_IPCA,
                'INPC': self.INDICES_INPC,
                'TR': self.INDICES_TR
            }
            indice = indices.get(self.indice_correcao, self.INDICES_IPCA)
            taxa_anual = indice.get(ano, 4.0)
            correcao_mes = valor_acumulado * (taxa_anual / 100 / 12)
            
            valor_acumulado += juros_mes + correcao_mes
            
            detalhes.append({
                'mes': data_atual.strftime('%m/%Y'),
                'valor_inicial': round(valor_acumulado - juros_mes - correcao_mes, 2),
                'juros': round(juros_mes, 2),
                'correcao': round(correcao_mes, 2),
                'valor_final': round(valor_acumulado, 2)
            })
            
            data_atual = data_proxima
        
        return detalhes

# Exemplo de uso
if __name__ == "__main__":
    # Teste
    calc = CalculadoraPrecatorio(
        valor_principal=100000.00,
        data_base='2020-01-01',
        data_final='2026-01-05',
        taxa_juros_mensal=0.5,
        indice_correcao='IPCA'
    )
    
    resultado = calc.calcular_tudo()
    
    print("\n" + "="*70)
    print("CALCULADORA DE PRECATÓRIOS - TESTE")
    print("="*70)
    print(f"\nValor Principal: R$ {resultado['valor_principal']:,.2f}")
    print(f"Juros ({resultado['meses_calculados']} meses): R$ {resultado['valor_juros']:,.2f}")
    print(f"Correção ({resultado['indice_correcao']}): R$ {resultado['valor_correcao']:,.2f}")
    print(f"Valor Total: R$ {resultado['valor_total']:,.2f}")
    print(f"\nPeríodo: {resultado['data_base']} a {resultado['data_final']}")
    print("="*70)
