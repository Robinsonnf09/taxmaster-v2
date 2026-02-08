"""
Teste com URL específica fornecida pelo usuário
"""
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL específica do usuário
URL_EXEMPLO = "https://esaj.tjsp.jus.br/cpopg/search.do?conversationId=&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado=&foroNumeroUnificado=&dadosConsulta.valorConsultaNuUnificado=&dadosConsulta.valorConsultaNuUnificado=UNIFICADO&dadosConsulta.valorConsulta=0000001-77.2024.8.26.0053&dadosConsulta.tipoNuProcesso=SAJ&consultaDeRequisitorios=true"

print("═"*70)
print("  TESTE COM URL ESPECÍFICA")
print("═"*70)
print()

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument('--start-maximized')

print("🚀 Iniciando Chrome...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print(f"🌐 Acessando URL específica...")
    print(f"   {URL_EXEMPLO[:100]}...\n")
    
    driver.get(URL_EXEMPLO)
    time.sleep(5)
    
    # Screenshot
    driver.save_screenshot("./debug_screenshots/teste_url_especifica.png")
    print("📸 Screenshot: teste_url_especifica.png")
    
    # HTML
    with open("./debug_screenshots/teste_url_especifica.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("💾 HTML: teste_url_especifica.html")
    
    # Analisar página
    print("\n🔍 Analisando elementos da página...\n")
    
    # Procurar TODOS os links
    todos_links = driver.find_elements(By.TAG_NAME, "a")
    print(f"📊 Total de links na página: {len(todos_links)}\n")
    
    # Mostrar primeiros 20 links
    print("🔗 Primeiros 20 links encontrados:\n")
    for idx, link in enumerate(todos_links[:20], 1):
        try:
            texto = link.text.strip()[:50] if link.text else "[Vazio]"
            href = link.get_attribute('href')
            href_resumido = href[:60] if href else "[Sem href]"
            
            print(f"  [{idx}] {texto}")
            print(f"      {href_resumido}")
            
            # Destacar se tiver "oficio" ou "requisitorio"
            if href and ('oficio' in href.lower() or 'requisit' in href.lower()):
                print(f"      ⭐ POSSÍVEL OFÍCIO!")
            if texto and ('ofício' in texto.lower() or 'requisit' in texto.lower()):
                print(f"      ⭐ TEXTO COM 'OFÍCIO'!")
            
            print()
            
        except Exception as e:
            print(f"  [{idx}] Erro: {str(e)[:40]}\n")
    
    # Procurar tabelas
    tabelas = driver.find_elements(By.TAG_NAME, "table")
    print(f"\n📊 Total de tabelas: {len(tabelas)}")
    
    for idx, tabela in enumerate(tabelas, 1):
        table_id = tabela.get_attribute('id') or f"[Sem ID {idx}]"
        print(f"  Tabela {idx}: {table_id}")
    
    print("\n✅ Análise concluída!")
    print("\nAbra os arquivos para análise:")
    print("  • debug_screenshots/teste_url_especifica.png")
    print("  • debug_screenshots/teste_url_especifica.html")
    
finally:
    print("\n⏳ Aguardando 10 segundos para você ver a página...")
    time.sleep(10)
    driver.quit()
    print("🔒 Navegador fechado")
