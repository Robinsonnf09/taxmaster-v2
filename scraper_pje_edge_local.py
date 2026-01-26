"""
Scraper PJe com Edge usando EdgeDriver LOCAL
Não depende de download automático
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import subprocess

class ScraperPJeEdgeLocal:
    """Scraper usando Edge com driver local"""
    
    def __init__(self):
        self.driver = None
        self.token_info = {
            'titular': 'ELIANA DE CAMARGO FIGUEIREDO',
            'cpf': '16111791818',
            'tipo': 'RFB e-CPF A3'
        }
    
    def detectar_edge_e_driver(self):
        """Detecta Edge e EdgeDriver instalados"""
        
        print("\n🔍 Detectando Microsoft Edge...")
        
        # Caminhos possíveis do Edge
        caminhos_edge = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        
        edge_path = None
        for caminho in caminhos_edge:
            if os.path.exists(caminho):
                edge_path = caminho
                print(f"✅ Edge encontrado: {caminho}")
                break
        
        if not edge_path:
            raise Exception("Edge não encontrado! Instale o Microsoft Edge.")
        
        # EdgeDriver geralmente vem com Edge
        # Vamos usar o msedgedriver que vem com o Edge
        driver_path = os.path.join(
            os.path.dirname(edge_path),
            "msedgedriver.exe"
        )
        
        if not os.path.exists(driver_path):
            print(f"⚠️  EdgeDriver não encontrado em: {driver_path}")
            print("   Tentando caminho alternativo...")
            
            # Caminho alternativo
            driver_path = r"C:\Windows\System32\msedgedriver.exe"
            
            if not os.path.exists(driver_path):
                print("\n❌ EdgeDriver não encontrado!")
                print("\n📥 SOLUÇÃO: Baixe manualmente")
                print("   1. Acesse: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                print("   2. Baixe a versão correspondente ao seu Edge")
                print("   3. Extraia msedgedriver.exe para: C:\Windows\System32\")
                
                # Tentar usar sem especificar driver (Edge usa driver automático)
                print("\n💡 Tentando usar driver automático do Edge...")
                return None
        else:
            print(f"✅ EdgeDriver encontrado: {driver_path}")
        
        return driver_path
    
    def iniciar_edge(self):
        """Inicia Edge com configurações para certificado"""
        
        print(f"\n🌐 Iniciando Microsoft Edge...")
        print(f"   Certificado: {self.token_info['titular']}")
        
        edge_options = Options()
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Download automático
        pasta_oficios = os.path.join(os.getcwd(), 'oficios_baixados')
        os.makedirs(pasta_oficios, exist_ok=True)
        
        prefs = {
            'download.default_directory': pasta_oficios,
            'download.prompt_for_download': False,
            'plugins.always_open_pdf_externally': True
        }
        edge_options.add_experimental_option('prefs', prefs)
        
        # Tentar iniciar Edge
        try:
            # Tentar com driver detectado
            driver_path = self.detectar_edge_e_driver()
            
            if driver_path:
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Edge(service=service, options=edge_options)
            else:
                # Tentar sem especificar driver (Edge automático)
                self.driver = webdriver.Edge(options=edge_options)
            
            print("✅ Edge iniciado com sucesso!")
            return self.driver
            
        except Exception as e:
            print(f"\n❌ Erro ao iniciar Edge: {str(e)}")
            print("\n🔧 SOLUÇÕES:")
            print("   1. Baixe EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            print("   2. Ou use Chrome: python scraper_pje_token_a3_v2.py")
            raise
    
    def acessar_pje(self, url):
        """Acessa PJe"""
        
        if not self.driver:
            self.iniciar_edge()
        
        print(f"\n🌐 Acessando: {url}")
        self.driver.get(url)
        
        print("\n⚠️  FAÇA LOGIN COM CERTIFICADO:")
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token")
        print("   4. Aguarde o login")
        
        input("\n>>> Pressione ENTER após fazer login <<<")
        
        url_atual = self.driver.current_url
        
        if "login" not in url_atual.lower():
            print("✅ LOGIN REALIZADO!")
            return True
        else:
            print("⚠️  Ainda na tela de login")
            return False
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("🔒 Edge fechado")

# TESTE
if __name__ == "__main__":
    print("="*70)
    print("🌐 SCRAPER PJE COM EDGE (DRIVER LOCAL)")
    print("="*70)
    
    scraper = ScraperPJeEdgeLocal()
    
    try:
        print("\n📋 PRÉ-REQUISITOS:")
        print("   ✅ Token A3 conectado")
        print("   ✅ PIN em mãos")
        print("   ✅ Microsoft Edge instalado")
        
        input("\nPressione ENTER para iniciar...")
        
        url_pje = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        if scraper.acessar_pje(url_pje):
            print("\n✅ Sistema pronto para usar!")
            
            # Aqui você pode adicionar lógica de busca
            
        input("\nPressione ENTER para fechar...")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
    
    finally:
        scraper.fechar()
    
    print("\n✅ CONCLUÍDO!")
