"""
Debug: Tira screenshot após preencher para ver o botão
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = None

try:
    print("🌐 Iniciando Chrome...")
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Login
    driver.get("https://pje1g.trf1.jus.br/pje/login.seam")
    input("\n>>> Faça login e pressione ENTER <<<\n")
    
    # Acessar PUSH
    driver.get("https://pje1g.trf1.jus.br/pje/Push/listView.seam")
    time.sleep(3)
    
    # Preencher campo
    campo = driver.find_element(By.XPATH, "//input[contains(@placeholder, '_')]")
    campo.send_keys("0096864-86.2025.4.03.9900")
    
    print("\n✅ Campo preenchido!")
    print("📸 Tirando screenshot...")
    
    time.sleep(2)
    
    # SCREENSHOT APÓS PREENCHER
    driver.save_screenshot("botao_incluir_screenshot.png")
    
    print("✅ Screenshot salvo: botao_incluir_screenshot.png")
    print("\n📋 PRÓXIMO PASSO:")
    print("   1. Abra: botao_incluir_screenshot.png")
    print("   2. Me envie a imagem")
    print("   3. Vou identificar o botão INCLUIR")
    print("   4. Ajusto o script!")
    
    input("\nPressione ENTER para fechar...")
    
except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    if driver:
        driver.quit()
