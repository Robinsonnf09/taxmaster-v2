"""
Serviço de busca automática de ofícios requisitórios
"""

import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests

class BuscaOficioService:
    """Serviço de busca de ofícios nos tribunais"""
    
    TRIBUNAIS = {
        'TJ-BA': {
            'nome': 'Tribunal de Justiça da Bahia',
            'url': 'https://esaj.tjba.jus.br/cpopg/open.do',
            'tipo': 'esaj'
        },
        'TRF1': {
            'nome': 'Tribunal Regional Federal 1ª Região',
            'url': 'https://processual.trf1.jus.br/consultaProcessual/processo.php',
            'tipo': 'eproc'
        },
        'TRF5': {
            'nome': 'Tribunal Regional Federal 5ª Região',
            'url': 'https://cp.trf5.jus.br/processo/',
            'tipo': 'eproc'
        },
        'TJBA': {
            'nome': 'Tribunal de Justiça da Bahia',
            'url': 'https://esaj.tjba.jus.br/cpopg/open.do',
            'tipo': 'esaj'
        }
    }
    
    def __init__(self, certificado_path=None, senha=None):
        self.certificado_path = certificado_path
        self.senha = senha
        self.driver = None
    
    def inicializar_driver(self, headless=False):
        """Inicializa o Selenium WebDriver"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Configurar certificado se fornecido
        if self.certificado_path and os.path.exists(self.certificado_path):
            chrome_options.add_argument(f'--client-certificate={self.certificado_path}')
        
        # Download automático
        prefs = {
            "download.default_directory": os.path.abspath("downloads/oficios"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return self.driver
    
    def fechar_driver(self):
        """Fecha o WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def buscar_oficio_esaj(self, numero_processo):
        """Busca ofício no sistema ESAJ (TJ-BA, TJ-SP, etc)"""
        try:
            tribunal_info = self.TRIBUNAIS.get('TJ-BA')
            url = tribunal_info['url']
            
            if not self.driver:
                self.inicializar_driver()
            
            self.driver.get(url)
            time.sleep(2)
            
            # Preencher número do processo
            input_processo = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "numeroDigitoAnoUnificado"))
            )
            
            # Limpar e formatar número
            processo_limpo = numero_processo.replace('.', '').replace('-', '')
            input_processo.send_keys(processo_limpo[:15])  # Primeiros dígitos
            
            # Preencher foro
            input_foro = self.driver.find_element(By.ID, "foroNumeroUnificado")
            input_foro.send_keys(processo_limpo[15:19])  # Foro
            
            # Ano
            input_ano = self.driver.find_element(By.ID, "numeroAnoUnificado")
            input_ano.send_keys(processo_limpo[19:23])  # Ano
            
            # Submeter
            btn_consultar = self.driver.find_element(By.ID, "pbEnviar")
            btn_consultar.click()
            
            time.sleep(3)
            
            # Procurar link de ofício/precatório
            links_documentos = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Ofício")
            
            if links_documentos:
                oficio_url = links_documentos[0].get_attribute('href')
                return {
                    'sucesso': True,
                    'url': oficio_url,
                    'mensagem': 'Ofício encontrado!'
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': 'Ofício não encontrado no processo'
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro na busca: {str(e)}'
            }
    
    def buscar_oficio_eproc(self, numero_processo):
        """Busca ofício no sistema e-Proc (TRF1, TRF5, etc)"""
        try:
            # Implementação específica para e-Proc
            # Similar ao ESAJ mas com seletores diferentes
            
            return {
                'sucesso': False,
                'mensagem': 'Sistema e-Proc em implementação'
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro: {str(e)}'
            }
    
    def download_oficio(self, url, numero_processo):
        """Baixa o ofício requisitório"""
        try:
            # Navegar para URL do ofício
            if not self.driver:
                self.inicializar_driver()
            
            self.driver.get(url)
            time.sleep(3)
            
            # Nome do arquivo
            filename = f"oficio_{numero_processo.replace('.', '_').replace('-', '_')}.pdf"
            filepath = os.path.join("downloads/oficios", filename)
            
            # Aguardar download
            max_wait = 30
            waited = 0
            while waited < max_wait:
                if os.path.exists(filepath):
                    return {
                        'sucesso': True,
                        'path': filepath
                    }
                time.sleep(1)
                waited += 1
            
            return {
                'sucesso': False,
                'mensagem': 'Timeout no download'
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro no download: {str(e)}'
            }
    
    def processar_lote(self, lista_precatorios, callback=None):
        """Processa lote de precatórios"""
        resultados = []
        total = len(lista_precatorios)
        
        for idx, precatorio in enumerate(lista_precatorios, 1):
            numero_processo = precatorio.get('numero_processo')
            tribunal = precatorio.get('tribunal', 'TJ-BA')
            
            # Callback de progresso
            if callback:
                callback(idx, total, numero_processo)
            
            # Buscar ofício
            tribunal_info = self.TRIBUNAIS.get(tribunal, self.TRIBUNAIS['TJ-BA'])
            
            if tribunal_info['tipo'] == 'esaj':
                resultado = self.buscar_oficio_esaj(numero_processo)
            else:
                resultado = self.buscar_oficio_eproc(numero_processo)
            
            # Se encontrou, tentar baixar
            if resultado.get('sucesso') and resultado.get('url'):
                download_result = self.download_oficio(resultado['url'], numero_processo)
                resultado['download'] = download_result
            
            resultado['numero_processo'] = numero_processo
            resultado['tribunal'] = tribunal
            resultados.append(resultado)
            
            # Pequeno delay entre buscas
            time.sleep(2)
        
        return resultados
    
    @staticmethod
    def importar_planilha(filepath):
        """Importa planilha Excel/CSV com lista de precatórios"""
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            # Validar colunas obrigatórias
            required_cols = ['numero_processo']
            missing = [col for col in required_cols if col not in df.columns]
            
            if missing:
                return {
                    'sucesso': False,
                    'erro': f'Colunas obrigatórias faltando: {", ".join(missing)}'
                }
            
            # Converter para lista de dicionários
            precatorios = df.to_dict('records')
            
            return {
                'sucesso': True,
                'precatorios': precatorios,
                'total': len(precatorios)
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao importar: {str(e)}'
            }
