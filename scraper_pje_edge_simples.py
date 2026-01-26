"""
Scraper PJe com Edge - VERSÃO CORRIGIDA
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import time
import os

class ScraperPJeEdge:
    
    def __init__(self):
        self.driver = None
    
    def iniciar_edge(self):
        """Inicia Edge com configurações simples"""
        
        print("\n🌐 Iniciando Microsoft Edge...")
        print("   Certificado: ELIANA DE CAMARGO FIGUEIREDO")
        
        edge_options = Options()
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--ignore-certificate-errors')
        
        # Download automático
        pasta_oficios = os.path.join(os.getcwd(), 'oficios_baixados')
        os.makedirs(pasta_oficios, exist_ok=True)
        
        prefs = {
            'download.default_directory': pasta_oficios,
            'download.prompt_for_download': False
        }
        edge_options.add_experimental_option('prefs', prefs)
        
        try:
            # Tentar iniciar Edge (driver automático)
            self.driver = webdriver.Edge(options=edge_options)
            print("✅ Edge iniciado!")
            return self.driver
            
        except Exception as e:
            erro = str(e)
            print(f"\n❌ Erro ao iniciar Edge: {erro}")
            
            if "EdgeDriver" in erro or "msedgedriver" in erro:
                print("\n📥 SOLUÇÃO:")
                print("   1. Baixe EdgeDriver em:")
                print("      https://developer.microsoft.com/edge/tools/webdriver/")
                print("   2. Extraia msedgedriver.exe")
                print(r"   3. Coloque em: C:\Windows\System32\msedgedriver.exe")
                print("\n💡 OU USE CHROME:")
                print("   python scraper_pje_token_a3_v2.py")
            
            raise
    
    def acessar_pje(self, url):
        """Acessa PJe e aguarda login manual"""
        
        if not self.driver:
            self.iniciar_edge()
        
        print(f"\n🌐 Acessando: {url}")
        self.driver.get(url)
        
        print("\n⚠️  INSTRUÇÕES DE LOGIN:")
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token quando solicitado")
        print("   4. Aguarde entrar no sistema")
        print("\n   Após completar o LOGIN, volte aqui!")
        
        input("\n>>> Pressione ENTER após fazer login completo <<<")
        
        # Verificar se logou
        url_atual = self.driver.current_url
        print(f"\n📍 URL atual: {url_atual}")
        
        if "login" not in url_atual.lower():
            print("✅ LOGIN REALIZADO COM SUCESSO!")
            return True
        else:
            print("⚠️  Ainda está na tela de login")
            return False
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("🔒 Edge fechado")

# TESTE
if __name__ == "__main__":
    print("="*70)
    print("🌐 SCRAPER PJE COM MICROSOFT EDGE + TOKEN A3")
    print("="*70)
    
    scraper = ScraperPJeEdge()
    
    try:
        print("\n📋 ANTES DE COMEÇAR:")
        print("   ✅ Token A3 conectado na USB")
        print("   ✅ PIN do token em mãos")
        print("   ✅ Microsoft Edge instalado")
        
        input("\nPressione ENTER para abrir o Edge...")
        
        # URL do PJe TRF1
        url_pje = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        # Acessar e fazer login
        if scraper.acessar_pje(url_pje):
            print("\n✅ SUCESSO! Sistema pronto!")
            print("\n💡 Agora você pode:")
            print("   - Buscar processos")
            print("   - Baixar ofícios")
            print("   - Automatizar consultas")
        else:
            print("\n⚠️  Login não completado")
            print("   Tente novamente ou verifique o certificado")
        
        input("\nPressione ENTER para fechar o Edge...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
    
    finally:
        scraper.fechar()
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO!")
    print("="*70)
