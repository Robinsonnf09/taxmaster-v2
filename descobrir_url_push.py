"""
Descobre a URL correta do serviço PUSH navegando pelo menu
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    print("✅ Chrome iniciado!")
    
    # Login
    driver.get("https://pje1g.trf1.jus.br/pje/login.seam")
    input("\n>>> Faça login com certificado e pressione ENTER <<<\n")
    
    print("\n📋 AGORA NAVEGUE MANUALMENTE ATÉ O SERVIÇO PUSH:")
    print("   1. Procure no menu principal")
    print("   2. Pode estar em: Configurações, Preferências, Serviços, etc.")
    print("   3. Procure por 'Push', 'Notificações', 'Acompanhamento'")
    print("   4. QUANDO ESTIVER NA PÁGINA DO PUSH, volte aqui!")
    
    input("\n>>> Pressione ENTER quando estiver na página do PUSH <<<\n")
    
    # Capturar URL correta
    url_correta = driver.current_url
    
    print("\n" + "="*70)
    print("✅ URL CORRETA DO PUSH ENCONTRADA!")
    print("="*70)
    print(f"\n📍 URL: {url_correta}")
    print("\n" + "="*70)
    
    # Salvar screenshot da página CORRETA
    driver.save_screenshot("push_correto.png")
    print("\n📸 Screenshot salvo: push_correto.png")
    
    # Salvar HTML
    with open("push_correto.html", 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("📄 HTML salvo: push_correto.html")
    
    # Salvar URL em arquivo
    with open("url_push_correta.txt", 'w') as f:
        f.write(url_correta)
    print("📝 URL salva em: url_push_correta.txt")
    
    input("\nPressione ENTER para fechar...")
    
except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    if driver:
        driver.quit()
