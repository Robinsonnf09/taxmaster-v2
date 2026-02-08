"""
Scraper REAL do TJGO com Selenium - VERSÃO CORRIGIDA
"""
import sys
import json
import time
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_DISPONIVEL = True
except ImportError:
    SELENIUM_DISPONIVEL = False

def buscar_processo_tjgo_real(numero_processo, tribunal):
    """Scraping REAL do TJGO usando Selenium"""
    
    print(f"🔍 Buscando processo {numero_processo} no {tribunal}...")
    print(f"🌐 Acessando site oficial do tribunal...")
    
    if not SELENIUM_DISPONIVEL:
        print("❌ Selenium não disponível")
        return buscar_modo_basico(numero_processo, tribunal)
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Carregar certificado (CORRIGIDO - trata BOM)
    cert_config_path = Path("./dados/certificado_config.json")
    if cert_config_path.exists():
        try:
            with open(cert_config_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig remove BOM
                cert_config = json.load(f)
            subject = cert_config.get('Subject', 'N/A')
            if len(subject) > 50:
                subject = subject[:50] + "..."
            print(f"✅ Certificado: {subject}")
        except Exception as e:
            print(f"⚠️  Certificado: {str(e)[:50]}")
    
    try:
        # Inicializar Chrome
        print(f"🚀 Iniciando navegador...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # URL do TJGO
        url_tjgo = "https://projudi.tjgo.jus.br/BuscaProcesso"
        
        print(f"📡 Conectando ao TJGO...")
        driver.get(url_tjgo)
        time.sleep(3)
        
        # Buscar processo
        try:
            campo_processo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "numProcesso"))
            )
            
            numero_limpo = numero_processo.replace("-", "").replace(".", "")
            campo_processo.clear()
            campo_processo.send_keys(numero_limpo)
            
            print(f"✅ Número preenchido: {numero_processo}")
            
            botao_buscar = driver.find_element(By.ID, "btnConsultar")
            botao_buscar.click()
            
            print(f"⏳ Aguardando resultado...")
            time.sleep(5)
            
            # Extrair dados
            dados_extraidos = {
                "numero": numero_processo,
                "tribunal": tribunal,
                "timestamp": datetime.now().isoformat(),
                "modo": "SCRAPING_REAL_SELENIUM",
                "url_acesso": driver.current_url,
                "dados": {}
            }
            
            # Extrair informações (com tratamento de erro)
            campos = [
                ("classe", "//span[contains(text(), 'Classe:')]/following-sibling::span"),
                ("assunto", "//span[contains(text(), 'Assunto:')]/following-sibling::span"),
                ("valor_causa", "//span[contains(text(), 'Valor:')]/following-sibling::span"),
            ]
            
            for campo_nome, xpath in campos:
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    dados_extraidos["dados"][campo_nome] = element.text
                    print(f"  ✅ {campo_nome.title()}: {element.text[:50]}")
                except:
                    print(f"  ⚠️  {campo_nome.title()}: não encontrado")
            
            # Screenshot
            screenshot_path = f"./resultados/screenshot_{tribunal}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            dados_extraidos["screenshot"] = screenshot_path
            
            print(f"📸 Screenshot: {screenshot_path}")
            
        except Exception as e:
            print(f"⚠️  Erro na extração: {str(e)[:100]}")
            dados_extraidos = {
                "numero": numero_processo,
                "tribunal": tribunal,
                "erro": str(e),
                "modo": "SCRAPING_ERRO"
            }
        
        finally:
            driver.quit()
            print(f"🔒 Navegador fechado")
        
        # Salvar resultado
        json_path = f"./resultados/scraping_{tribunal}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados_extraidos, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Salvo: {json_path}")
        return dados_extraidos
        
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)[:100]}")
        return buscar_modo_basico(numero_processo, tribunal)

def buscar_modo_basico(numero_processo, tribunal):
    """Modo básico"""
    print("⚠️  Modo básico ativado")
    
    resultado = {
        "numero": numero_processo,
        "tribunal": tribunal,
        "modo": "BASICO",
        "timestamp": datetime.now().isoformat()
    }
    
    json_path = f"./resultados/scraping_{tribunal}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    return resultado

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python scraper_tjgo_cert.py <numero_processo> <tribunal>")
        sys.exit(1)
    
    print("═══════════════════════════════════════════")
    print("  SCRAPER TJGO - SELENIUM + CERT A3")
    print("  VERSÃO CORRIGIDA")
    print("═══════════════════════════════════════════")
    print("")
    
    resultado = buscar_processo_tjgo_real(sys.argv[1], sys.argv[2])
    
    print("")
    print("✅ Concluído!")
