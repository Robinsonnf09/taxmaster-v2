"""
Scraper PJe com TOKEN A3 - VERSÃO CORRIGIDA
Usa abordagem diferente para certificado
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class ScraperPJeTokenCorrigido:
    
    def __init__(self):
        self.driver = None
    
    def iniciar_chrome_com_certificado(self):
        """Chrome com configurações SSL corretas"""
        
        print("\n🔐 Configurando Chrome para certificado A3...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        # CRÍTICO: Desabilitar verificações que bloqueiam certificado
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument('--disable-web-security')
        
        # Forçar Chrome a SEMPRE pedir certificado
        chrome_options.add_argument('--auto-select-desktop-capture-source=NONE')
        
        # Usar perfil padrão do Chrome (onde certificado está instalado)
        import os
        user_data = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        chrome_options.add_argument(f'--user-data-dir={user_data}')
        chrome_options.add_argument('--profile-directory=Default')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome iniciado com perfil que tem o certificado!")
        return self.driver
    
    def acessar_pje_metodo_manual(self):
        """Método manual: deixa usuário fazer login"""
        
        if not self.driver:
            self.iniciar_chrome_com_certificado()
        
        url = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        print(f"\n🌐 Abrindo PJe: {url}")
        self.driver.get(url)
        
        print("\n⚠️  FAÇA O LOGIN MANUALMENTE:")
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token")
        print("   4. Aguarde entrar no sistema")
        print("\n   Quando estiver LOGADO, volte aqui e pressione ENTER")
        
        input("\n>>> Pressione ENTER após fazer login <<<")
        
        # Verificar se logou
        if "login" not in self.driver.current_url.lower():
            print("\n✅ LOGIN REALIZADO COM SUCESSO!")
            print(f"   URL atual: {self.driver.current_url}")
            return True
        else:
            print("\n❌ Ainda está na tela de login!")
            return False
    
    def buscar_processo(self, numero):
        """Busca processo após login"""
        print(f"\n🔍 Buscando processo: {numero}")
        # Adaptar conforme interface do PJe após login
        time.sleep(2)
        return True
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# TESTE
if __name__ == "__main__":
    print("="*70)
    print("🔐 SCRAPER PJE COM TOKEN A3 - VERSÃO CORRIGIDA")
    print("="*70)
    
    scraper = ScraperPJeTokenCorrigido()
    
    try:
        input("\n⚠️  Conecte o TOKEN e pressione ENTER...")
        
        # Método manual: usuário faz login
        if scraper.acessar_pje_metodo_manual():
            print("\n✅ Pronto para buscar processos!")
            
            # Aqui você pode automatizar buscas
            # scraper.buscar_processo("0000001-00.2020.4.01.3800")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        scraper.fechar()
    
    print("\n✅ TESTE CONCLUÍDO!")
