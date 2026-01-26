"""
Scraper de Diários Oficiais Eletrônicos
Monitora publicações de nomeação de perito
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

class ScraperDiarios:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def buscar_diario_cnj(self):
        """Busca no Diário de Justiça Eletrônico do CNJ"""
        print(f'[{datetime.now()}] Acessando diários oficiais...')
        
        oportunidades = []
        
        # URLs dos diários (exemplos)
        diarios = [
            'https://www.cnj.jus.br/diario-justica-eletronico/',
            'https://dje.tjsp.jus.br/cdje/',
        ]
        
        for url in diarios:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar por padrões de nomeação
                texto = soup.get_text()
                
                # Regex para detectar nomeações
                padrao = r'(nomei[ao]|design[ao]).*?perit[oa].*?(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})'
                
                matches = re.finditer(padrao, texto, re.IGNORECASE)
                
                for match in matches:
                    processo = match.group(2)
                    
                    oportunidades.append({
                        'tribunal': 'Detectado em Diário',
                        'processo': processo,
                        'especialidade': 'A definir',
                        'fonte': url,
                        'dataPublicacao': datetime.now().isoformat(),
                        'status': 'Aguardando análise'
                    })
                
            except Exception as e:
                print(f'[ERRO] {url}: {str(e)}')
        
        print(f'[OK] {len(oportunidades)} publicações detectadas')
        return oportunidades
    
    def salvar_publicacoes(self, oportunidades):
        """Salva publicações detectadas"""
        with open('publicacoes_diarios.json', 'w', encoding='utf-8') as f:
            json.dump(oportunidades, f, indent=2, ensure_ascii=False)
        print(f'[OK] Publicações salvas em publicacoes_diarios.json')

if __name__ == '__main__':
    print('=== SCRAPER DIÁRIOS OFICIAIS - INICIADO ===')
    
    scraper = ScraperDiarios()
    oportunidades = scraper.buscar_diario_cnj()
    scraper.salvar_publicacoes(oportunidades)
    
    print(f'\n=== CONCLUÍDO: {len(oportunidades)} publicações detectadas ===')
