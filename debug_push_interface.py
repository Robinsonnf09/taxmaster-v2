"""
Versão DEBUG - Tira screenshots para identificar problema
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

driver = None

try:
    print("🌐 Iniciando Chrome...")
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("✅ Chrome iniciado!")
    
    # Login
    driver.get("https://pje1g.trf1.jus.br/pje/login.seam")
    input(">>> Faça login e pressione ENTER <<<")
    
    # Acessar PUSH
    base = driver.current_url.split("/pje/")[0]
    url_push = f"{base}/pje/Processo/CadastroPush/listView.seam"
    driver.get(url_push)
    time.sleep(3)
    
    # TIRAR SCREENSHOT DA PÁGINA DO PUSH
    screenshot_path = "push_page_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"\n📸 Screenshot salvo: {screenshot_path}")
    
    # SALVAR HTML DA PÁGINA
    html_path = "push_page_source.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"📄 HTML salvo: {html_path}")
    
    print("\n✅ Arquivos salvos com sucesso!")
    print("\n📋 PRÓXIMO PASSO:")
    print("   1. Abra: push_page_screenshot.png")
    print("   2. Veja a interface do PUSH")
    print("   3. Me envie a imagem")
    print("   4. Vou adaptar o script para a interface correta!")
    
    input("\nPressione ENTER para fechar...")
    
except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    if driver:
        driver.quit()
