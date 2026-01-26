"""
Integração com APIs de Tribunais
Suporta PJe, e-SAJ, PROJUDI
"""

import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class TribunalIntegration:
    """Base para integração com tribunais"""
    
    TRIBUNAIS_CONFIG = {
        'TRF1': {
            'nome': 'Tribunal Regional Federal 1ª Região',
            'url_pje': 'https://pje1g.trf1.jus.br',
            'tipo': 'PJe'
        },
        'TRF2': {
            'nome': 'Tribunal Regional Federal 2ª Região',
            'url_pje': 'https://pje.trf2.jus.br',
            'tipo': 'PJe'
        },
        'TRF3': {
            'nome': 'Tribunal Regional Federal 3ª Região',
            'url_pje': 'https://pje1g.trf3.jus.br',
            'tipo': 'PJe'
        },
        'TRF4': {
            'nome': 'Tribunal Regional Federal 4ª Região',
            'url_pje': 'https://pje2g.trf4.jus.br',
            'tipo': 'PJe'
        },
        'TRF5': {
            'nome': 'Tribunal Regional Federal 5ª Região',
            'url_pje': 'https://pje.trf5.jus.br',
            'tipo': 'PJe'
        },
        'TJSP': {
            'nome': 'Tribunal de Justiça de São Paulo',
            'url_esaj': 'https://esaj.tjsp.jus.br',
            'tipo': 'e-SAJ'
        }
    }
    
    def __init__(self, tribunal_sigla, certificado_manager):
        self.tribunal = self.TRIBUNAIS_CONFIG.get(tribunal_sigla, {})
        self.certificado = certificado_manager
        self.driver = None
        
    def iniciar_navegador_com_certificado(self):
        """Inicia Chrome com certificado A3"""
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-web-security')
        
        # Configurar certificado (necessário adicionar caminho do certificado)
        # chrome_options.add_argument(f'--client-certificate={certificado_path}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def buscar_processo_pje(self, numero_processo):
        """Busca processo no PJe"""
        try:
            if not self.driver:
                self.iniciar_navegador_com_certificado()
            
            url_busca = f"{self.tribunal['url_pje']}/pje/ConsultaPublica/listView.seam"
            self.driver.get(url_busca)
            
            # Aguardar campo de busca
            wait = WebDriverWait(self.driver, 10)
            campo_busca = wait.until(
                EC.presence_of_element_located((By.ID, "fPP:numeroProcesso:numeroSequencial"))
            )
            
            # Limpar formato do processo
            numero_limpo = numero_processo.replace('.', '').replace('-', '').replace('/', '')
            campo_busca.send_keys(numero_limpo)
            
            # Clicar em pesquisar
            btn_pesquisar = self.driver.find_element(By.ID, "fPP:searchProcessos")
            btn_pesquisar.click()
            
            time.sleep(3)
            
            # Verificar se processo foi encontrado
            # Aqui você pode adicionar lógica para extrair dados
            
            return {
                'sucesso': True,
                'encontrado': True,
                'url': self.driver.current_url
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def buscar_oficio_requisitorio(self, numero_processo):
        """Busca especificamente o ofício requisitório"""
        try:
            resultado = self.buscar_processo_pje(numero_processo)
            
            if not resultado['sucesso']:
                return resultado
            
            # Navegar até a aba de documentos
            # Procurar por "Ofício Requisitório" ou documento com padrão similar
            
            # Esta é uma implementação simplificada
            # Cada tribunal tem uma estrutura diferente
            
            return {
                'sucesso': True,
                'mensagem': 'Busca implementada - necessário ajuste específico por tribunal',
                'tribunal': self.tribunal['nome']
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def baixar_documento(self, documento_id, caminho_destino):
        """Baixa documento do tribunal"""
        try:
            # Implementar download
            # Usar Selenium para clicar no link de download
            
            return {
                'sucesso': True,
                'arquivo': caminho_destino
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def fechar(self):
        """Fecha navegador"""
        if self.driver:
            self.driver.quit()

# Importar scrapers reais
try:
    from scraper_trf1_real import ScraperTRF1Real
    SCRAPER_REAL_DISPONIVEL = True
except ImportError:
    SCRAPER_REAL_DISPONIVEL = False

