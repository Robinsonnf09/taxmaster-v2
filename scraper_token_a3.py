"""
Scraper com suporte a TOKEN A3
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from token_a3 import TokenA3Manager
import time

class ScraperComToken:
    def __init__(self):
        self.token_manager = TokenA3Manager()
        self.driver = None
    
    def iniciar_com_token(self):
        """Inicia navegador configurado para usar token A3"""
        
        print("\n🔐 Configurando token A3...")
        
        # Detectar e validar token
        if not self.token_manager.detectar_middleware():
            raise Exception("Middleware do token não encontrado!")
        
        if not self.token_manager.validar_token_conectado():
            raise Exception("Token A3 não está conectado!")
        
        # Configurar Chrome
        chrome_options = self.token_manager.configurar_chrome_para_token()
        
        if not chrome_options:
            chrome_options = Options()
        
        # Configurações adicionais
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Iniciar Chrome
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Navegador iniciado com token A3!")
        
        return self.driver
    
    def acessar_pje_com_certificado(self, url):
        """Acessa PJe usando certificado do token"""
        
        if not self.driver:
            self.iniciar_com_token()
        
        print(f"\n🌐 Acessando: {url}")
        self.driver.get(url)
        
        # Aguardar seleção de certificado (popup do Windows)
        print("\n⚠️  ATENÇÃO: Selecione o certificado no popup!")
        print("   Digite o PIN do token quando solicitado")
        
        time.sleep(10)  # Tempo para usuário selecionar certificado
        
        return self.driver

# Teste
if __name__ == "__main__":
    scraper = ScraperComToken()
    
    try:
        # Iniciar com token
        scraper.iniciar_com_token()
        
        # Acessar área autenticada do PJe
        scraper.acessar_pje_com_certificado(
            "https://pje1g.trf1.jus.br/pje/login.seam"
        )
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        if scraper.driver:
            scraper.driver.quit()
