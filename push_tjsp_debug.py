"""
PUSH TJSP - VERSÃO DEBUG COM SCREENSHOT AUTOMÁTICO
Gera screenshot e HTML para análise
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class PushTJSPDebug:
    
    def __init__(self):
        self.driver = None
        self.url_push = "https://esaj.tjsp.jus.br/push/index.do"
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def acessar_e_analisar(self):
        print(f"\n🔐 Acessando PUSH TJSP...")
        print(f"   URL: {self.url_push}")
        
        self.driver.get(self.url_push)
        print("   ⏳ Aguardando 5 segundos...")
        time.sleep(5)
        
        print("\n" + "="*70)
        print("📸 CAPTURANDO INTERFACE...")
        print("="*70)
        
        # SCREENSHOT
        screenshot_path = "tjsp_push_interface.png"
        self.driver.save_screenshot(screenshot_path)
        print(f"   ✅ Screenshot: {screenshot_path}")
        
        # HTML
        html_path = "tjsp_push_html.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"   ✅ HTML: {html_path}")
        
        # ANÁLISE DOS CAMPOS
        print("\n" + "="*70)
        print("🔍 ANALISANDO CAMPOS...")
        print("="*70)
        
        # Buscar todos os inputs
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        print(f"\n📝 Total de inputs encontrados: {len(inputs)}")
        
        for idx, inp in enumerate(inputs, 1):
            tipo = inp.get_attribute("type")
            nome = inp.get_attribute("name")
            id_campo = inp.get_attribute("id")
            placeholder = inp.get_attribute("placeholder")
            classe = inp.get_attribute("class")
            visivel = inp.is_displayed()
            
            if visivel:
                print(f"\n   Input {idx}:")
                print(f"      Tipo: {tipo}")
                print(f"      Name: {nome}")
                print(f"      ID: {id_campo}")
                print(f"      Placeholder: {placeholder}")
                print(f"      Class: {classe}")
        
        # Buscar todos os botões
        botoes = self.driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 Total de botões encontrados: {len(botoes)}")
        
        for idx, btn in enumerate(botoes, 1):
            texto = btn.text
            tipo = btn.get_attribute("type")
            nome = btn.get_attribute("name")
            id_btn = btn.get_attribute("id")
            classe = btn.get_attribute("class")
            visivel = btn.is_displayed()
            
            if visivel:
                print(f"\n   Botão {idx}:")
                print(f"      Texto: {texto}")
                print(f"      Tipo: {tipo}")
                print(f"      Name: {nome}")
                print(f"      ID: {id_btn}")
                print(f"      Class: {classe}")
        
        # Buscar inputs tipo submit
        submits = self.driver.find_elements(By.XPATH, "//input[@type='submit']")
        if submits:
            print(f"\n✅ Inputs tipo submit encontrados: {len(submits)}")
            for idx, sub in enumerate(submits, 1):
                value = sub.get_attribute("value")
                nome = sub.get_attribute("name")
                id_sub = sub.get_attribute("id")
                print(f"\n   Submit {idx}:")
                print(f"      Value: {value}")
                print(f"      Name: {nome}")
                print(f"      ID: {id_sub}")
        
        print("\n" + "="*70)
        print("✅ ANÁLISE COMPLETA!")
        print("="*70)
        print("\n📁 ARQUIVOS GERADOS:")
        print(f"   📸 {screenshot_path}")
        print(f"   📄 {html_path}")
        print("\n💡 Envie esses arquivos para análise!")
        print("="*70)
        
        input("\n>>> ENTER para fechar &lt;&lt;&lt;\n")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔍 PUSH TJSP - MODO DEBUG")
    print("="*70)
    print("\n🎯 Este script vai:")
    print("   1. Acessar o PUSH do TJSP")
    print("   2. Tirar screenshot automático")
    print("   3. Salvar HTML da página")
    print("   4. Listar TODOS os campos e botões")
    print("\n📁 Arquivos gerados:")
    print("   - tjsp_push_interface.png")
    print("   - tjsp_push_html.html")
    
    debug = PushTJSPDebug()
    
    try:
        input("\nENTER para começar...\n")
        
        debug.iniciar()
        debug.acessar_e_analisar()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        debug.fechar()
    
    print("\n✅ CONCLUÍDO!")
    print("\n📧 Envie os arquivos gerados:")
    print("   - tjsp_push_interface.png")
    print("   - tjsp_push_html.html")
