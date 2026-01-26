"""
Scraper DEMO - Gera dados simulados de oportunidades
Versão para testes sem dependência de sites externos
"""

import json
from datetime import datetime, timedelta
import random

class ScraperDemo:
    def __init__(self):
        self.tribunais = ['TRF-1', 'TRF-2', 'TRF-3', 'TRF-4', 'TRF-5', 'TJ-SP', 'TJ-RJ', 'TJ-MG', 'TRT-2', 'TRT-15']
        self.especialidades = [
            'Contábil - Financeira',
            'Trabalhista',
            'Cálculos de Liquidação',
            'Avaliação de Imóveis',
            'Engenharia Civil',
            'Medicina Trabalhista',
            'Informática Forense',
            'Grafotécnica'
        ]
    
    def gerar_processo(self):
        """Gera número de processo válido"""
        ano = random.randint(2023, 2024)
        sequencial = random.randint(1000000, 9999999)
        origem = random.randint(1000, 9999)
        return f"{sequencial:07d}-{random.randint(10,99)}.{ano}.{random.randint(1,9)}.{random.randint(1,26):02d}.{origem:04d}"
    
    def gerar_oportunidades(self, quantidade=20):
        """Gera oportunidades simuladas"""
        print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Gerando {quantidade} oportunidades simuladas...\n')
        
        oportunidades = []
        
        for i in range(quantidade):
            tribunal = random.choice(self.tribunais)
            especialidade = random.choice(self.especialidades)
            valorCausa = random.randint(50000, 1000000)
            complexidade = random.choice([1, 1.5, 2, 2.5, 3])
            horasEstimadas = random.randint(20, 100)
            
            # Calcular honorários
            valorHora = random.randint(300, 800)
            honorarios = int(horasEstimadas * valorHora * complexidade)
            honorarios = max(honorarios, int(valorCausa * 0.01))  # Mínimo 1%
            
            # Score baseado em honorários e complexidade
            score = min(100, int((honorarios / 1000) + (complexidade * 10)))
            
            # Prazo (5 a 30 dias)
            prazo = datetime.now() + timedelta(days=random.randint(5, 30))
            
            oportunidade = {
                'id': i + 1,
                'tribunal': tribunal,
                'processo': self.gerar_processo(),
                'especialidade': especialidade,
                'valorCausa': valorCausa,
                'honorariosEstimados': honorarios,
                'horasEstimadas': horasEstimadas,
                'complexidade': complexidade,
                'prazo': prazo.strftime('%Y-%m-%d'),
                'score': score,
                'status': random.choice(['Nova', 'Pendente', 'Em Análise']),
                'dataDeteccao': datetime.now().isoformat(),
                'urgente': prazo <= datetime.now() + timedelta(days=7)
            }
            
            oportunidades.append(oportunidade)
            
            # Progresso
            if (i + 1) % 5 == 0:
                print(f'[OK] {i + 1}/{quantidade} oportunidades geradas...')
        
        return oportunidades
    
    def salvar_json(self, oportunidades):
        """Salva oportunidades em JSON"""
        filename = f'oportunidades_demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(oportunidades, f, indent=2, ensure_ascii=False)
        
        print(f'\n[OK] Arquivo salvo: {filename}')
        return filename
    
    def exibir_resumo(self, oportunidades):
        """Exibe resumo das oportunidades"""
        total_honorarios = sum(opp['honorariosEstimados'] for opp in oportunidades)
        media_score = sum(opp['score'] for opp in oportunidades) / len(oportunidades)
        urgentes = sum(1 for opp in oportunidades if opp['urgente'])
        
        print(f'\n{"="*60}')
        print(f'RESUMO DAS OPORTUNIDADES DETECTADAS')
        print(f'{"="*60}')
        print(f'Total de Oportunidades: {len(oportunidades)}')
        print(f'Honorários Totais Estimados: R$ {total_honorarios:,.2f}')
        print(f'Média de Score: {media_score:.1f}/100')
        print(f'Oportunidades Urgentes: {urgentes}')
        print(f'{"="*60}\n')
        
        # Top 5
        top5 = sorted(oportunidades, key=lambda x: x['honorariosEstimados'], reverse=True)[:5]
        
        print('TOP 5 MELHORES OPORTUNIDADES:')
        print(f'{"="*60}')
        for i, opp in enumerate(top5, 1):
            print(f'{i}. {opp["tribunal"]} - {opp["processo"]}')
            print(f'   Honorários: R$ {opp["honorariosEstimados"]:,.2f}')
            print(f'   Score: {opp["score"]}/100')
            print(f'   Prazo: {opp["prazo"]}')
            print()

if __name__ == '__main__':
    print('╔═══════════════════════════════════════════════════════════╗')
    print('║        SCRAPER DEMO - GERADOR DE OPORTUNIDADES           ║')
    print('║              Sistema de Perícia Judicial                 ║')
    print('╚═══════════════════════════════════════════════════════════╝')
    
    scraper = ScraperDemo()
    
    # Gerar 20 oportunidades
    oportunidades = scraper.gerar_oportunidades(quantidade=20)
    
    # Salvar em JSON
    arquivo = scraper.salvar_json(oportunidades)
    
    # Exibir resumo
    scraper.exibir_resumo(oportunidades)
    
    print(f'[SUCESSO] Scraper executado com sucesso!')
    print(f'[ARQUIVO] {arquivo}')
