"""
Scraper REAL para TRF1 - COM WEBDRIVER-MANAGER
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

class ScraperTRF1Real:
    def __init__(self):
        self.base_url = "https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam"
        self.driver = None
    
    def iniciar_navegador(self):
        """Inicia Chrome com ChromeDriver automático"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Download automático
        pasta_download = os.path.join(os.getcwd(), "oficios_baixados")
        os.makedirs(pasta_download, exist_ok=True)
        
        prefs = {
            "download.default_directory": pasta_download,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Usar webdriver-manager para instalar ChromeDriver automaticamente
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome iniciado com sucesso!")
        return self.driver
    
    def buscar_processo_real(self, numero_processo):
        """Busca REAL no PJe"""
        try:
            if not self.driver:
                self.iniciar_navegador()
            
            print(f"\n🔍 Buscando processo: {numero_processo}")
            
            # Acessar consulta pública
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Limpar número do processo
            numero_limpo = numero_processo.replace('.', '').replace('-', '').replace('/', '')
            
            if len(numero_limpo) != 20:
                return {
                    'sucesso': False,
                    'erro': f'Número de processo inválido. Esperado 20 dígitos, recebido {len(numero_limpo)}'
                }
            
            # Preencher campo de busca
            wait = WebDriverWait(self.driver, 15)
            
            print("📝 Preenchendo campos...")
            
            # Número sequencial (7 dígitos)
            campo_numero = wait.until(
                EC.presence_of_element_located((By.ID, "fPP:numeroProcesso:numeroSequencial"))
            )
            campo_numero.clear()
            campo_numero.send_keys(numero_limpo[0:7])
            
            # Dígito verificador (2 dígitos)
            campo_digito = self.driver.find_element(By.ID, "fPP:numeroProcesso:digitoVerificador")
            campo_digito.clear()
            campo_digito.send_keys(numero_limpo[7:9])
            
            # Ano (4 dígitos)
            campo_ano = self.driver.find_element(By.ID, "fPP:numeroProcesso:ano")
            campo_ano.clear()
            campo_ano.send_keys(numero_limpo[9:13])
            
            # Segmento (1 dígito)
            campo_segmento = self.driver.find_element(By.ID, "fPP:numeroProcesso:segmento")
            campo_segmento.clear()
            campo_segmento.send_keys(numero_limpo[13:14])
            
            # Tribunal (4 dígitos)
            campo_tribunal = self.driver.find_element(By.ID, "fPP:numeroProcesso:tribunal")
            campo_tribunal.clear()
            campo_tribunal.send_keys(numero_limpo[14:18])
            
            # Origem (4 dígitos)
            campo_origem = self.driver.find_element(By.ID, "fPP:numeroProcesso:origem")
            campo_origem.clear()
            campo_origem.send_keys(numero_limpo[18:22])
            
            print("✅ Campos preenchidos")
            
            # Clicar em Pesquisar
            btn_pesquisar = self.driver.find_element(By.ID, "fPP:searchProcessos")
            btn_pesquisar.click()
            
            print("⏳ Aguardando resultado...")
            time.sleep(4)
            
            # Verificar se encontrou
            try:
                resultado = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rich-table-row"))
                )
                print("✅ Processo encontrado!")
                
                # Clicar no processo
                resultado.click()
                time.sleep(2)
                
                return {
                    'sucesso': True,
                    'encontrado': True,
                    'mensagem': 'Processo encontrado no PJe'
                }
                
            except Exception as e:
                print(f"❌ Processo não encontrado: {str(e)}")
                return {
                    'sucesso': False,
                    'encontrado': False,
                    'mensagem': 'Processo não encontrado no PJe'
                }
        
        except Exception as e:
            print(f"❌ Erro na busca: {str(e)}")
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("🔒 Navegador fechado")

# Teste
if __name__ == "__main__":
    print("🚀 TESTE DO SCRAPER TRF1")
    print("="*60)
    
    scraper = ScraperTRF1Real()
    
    # IMPORTANTE: Use um processo REAL e PÚBLICO do TRF1
    # Formato: 0000000-00.0000.4.01.0000
    numero = "0000000-00.0000.4.01.0000"  # ⚠️ SUBSTITUA!
    
    print(f"⚠️  ATENÇÃO: Usando número fictício: {numero}")
    print("⚠️  Para testar de verdade, substitua por processo REAL!")
    print("="*60)
    
    try:
        resultado = scraper.buscar_processo_real(numero)
        print(f"\n📊 RESULTADO:")
        print(f"   Sucesso: {resultado.get('sucesso')}")
        print(f"   Encontrado: {resultado.get('encontrado', 'N/A')}")
        print(f"   Mensagem: {resultado.get('mensagem', resultado.get('erro', 'N/A'))}")
    finally:
        scraper.fechar()
