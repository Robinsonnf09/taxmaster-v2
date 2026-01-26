"""
Scraper FINAL - Usando TOKEN A3 Real com Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class ScraperPJeComTokenA3:
    """Scraper para PJe usando certificado A3 em TOKEN USB"""
    
    def __init__(self):
        self.driver = None
        self.token_info = {
            'titular': 'ELIANA DE CAMARGO FIGUEIREDO',
            'cpf': '16111791818',
            'provider': 'SafeSign IC Standard Windows Cryptographic Service Provider',
            'leitor': 'Giesecke & Devrient GmbH StarSign CUT S 0'
        }
    
    def iniciar_navegador_com_certificado(self):
        """Inicia Chrome configurado para usar certificado do token"""
        
        print(f"\n🔐 Configurando Chrome para usar TOKEN A3...")
        print(f"   Titular: {self.token_info['titular']}")
        print(f"   Leitor: {self.token_info['leitor']}")
        
        chrome_options = Options()
        
        # Configurações para certificado digital
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--start-maximized')
        
        # Habilitar certificados de cliente
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Política para sempre pedir PIN
        prefs = {
            'profile.default_content_setting_values.automatic_downloads': 1,
            'download.default_directory': os.path.join(os.getcwd(), 'oficios_baixados'),
            'download.prompt_for_download': False
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # Iniciar Chrome
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome iniciado!")
        return self.driver
    
    def acessar_pje_autenticado(self, url_pje):
        """Acessa área autenticada do PJe com certificado A3"""
        
        if not self.driver:
            self.iniciar_navegador_com_certificado()
        
        print(f"\n🌐 Acessando PJe: {url_pje}")
        self.driver.get(url_pje)
        
        print("\n⚠️  ATENÇÃO:")
        print("   1. Windows vai solicitar o PIN do token")
        print("   2. Digite o PIN na janela que aparecer")
        print("   3. Selecione o certificado de ELIANA DE CAMARGO FIGUEIREDO")
        print("   4. Aguarde o login automático...")
        
        # Aguardar autenticação (30 segundos para usuário digitar PIN)
        time.sleep(30)
        
        return self.driver
    
    def buscar_processo_autenticado(self, numero_processo):
        """Busca processo na área autenticada"""
        
        try:
            print(f"\n🔍 Buscando processo: {numero_processo}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Aguardar login
            print("   Aguardando login...")
            time.sleep(5)
            
            # Aqui você adaptaria para a interface específica do PJe autenticado
            # Exemplo genérico:
            
            # Campo de busca
            try:
                campo_busca = wait.until(
                    EC.presence_of_element_located((By.ID, "numeroProcesso"))
                )
                campo_busca.clear()
                campo_busca.send_keys(numero_processo)
                
                # Botão pesquisar
                btn_pesquisar = self.driver.find_element(By.ID, "btnPesquisar")
                btn_pesquisar.click()
                
                time.sleep(3)
                
                print("✅ Busca realizada!")
                return True
                
            except Exception as e:
                print(f"❌ Erro na busca: {str(e)}")
                return False
        
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("🔒 Navegador fechado")

# TESTE REAL
if __name__ == "__main__":
    print("="*70)
    print("🔐 TESTE REAL - SCRAPER COM TOKEN A3")
    print("="*70)
    
    scraper = ScraperPJeComTokenA3()
    
    try:
        # URL do PJe que requer certificado
        # TRF1: https://pje1g.trf1.jus.br/pje/login.seam
        # TRF2: https://pje.trf2.jus.br/pje/login.seam
        # etc.
        
        url_pje = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        print(f"\n⚠️  PREPARAÇÃO:")
        print(f"   1. Tenha o PIN do token em mãos")
        print(f"   2. Token deve estar conectado")
        print(f"   3. O Chrome vai abrir e solicitar o PIN")
        
        input("\nPressione ENTER para iniciar...")
        
        # Acessar PJe
        scraper.acessar_pje_autenticado(url_pje)
        
        print("\n✅ SE O LOGIN FUNCIONOU:")
        print("   O scraper está pronto para buscar processos!")
        
        # Testar busca (descomente quando estiver logado)
        # scraper.buscar_processo_autenticado("0000001-00.2020.4.01.3800")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        scraper.fechar()
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO!")
    print("="*70)
