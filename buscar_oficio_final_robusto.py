from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from pathlib import Path
import requests

def buscar_oficio_tjsp_robusto(numero_processo):
    """Busca ofício requisitório no TJSP - Versão ultra robusta"""
    
    downloads_dir = Path("data/oficios")
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"BUSCA ROBUSTA DE OFÍCIO REQUISITÓRIO - TJSP")
    print(f"Processo: {numero_processo}")
    print('='*60)
    
    # Configurar Chrome com opções avançadas
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": str(downloads_dir.absolute()),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 0
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(10)
    
    try:
        # 1. Acessar consulta de requisitórios
        print("\n1️⃣ Acessando consulta de requisitórios...")
        driver.get("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do")
        time.sleep(5)
        print("   ✅ Página carregada")
        
        # 2. Preencher número do processo
        print("\n2️⃣ Preenchendo número do processo...")
        partes = numero_processo.split('.')
        parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
        parte2 = partes[4]
        
        driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
        driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
        print(f"   ✅ Preenchido: {parte1} / {parte2}")
        
        driver.save_screenshot(str(downloads_dir / "1_preenchido.png"))
        
        # 3. Consultar
        print("\n3️⃣ Consultando...")
        driver.find_element(By.ID, "botaoConsultarProcessos").click()
        time.sleep(8)  # Aguardar mais tempo
        
        driver.save_screenshot(str(downloads_dir / "2_resultado.png"))
        print("   ✅ Resultado carregado")
        
        # 4. Verificar se encontrou o processo
        page_source = driver.page_source.lower()
        
        if "não encontrado" in page_source or "não existem" in page_source:
            print("   ❌ Processo não encontrado")
            return {"sucesso": False, "erro": "processo_nao_encontrado"}
        
        print("   ✅ Processo encontrado!")
        
        # 5. Procurar link de visualização com múltiplas estratégias
        print("\n4️⃣ Procurando link de visualização (múltiplas estratégias)...")
        
        link_visualizar = None
        
        # Estratégia 1: Por texto exato
        try:
            print("   Tentando: Link por texto 'Visualizar'...")
            link_visualizar = driver.find_element(By.LINK_TEXT, "Visualizar")
            print("   ✅ Encontrado por texto!")
        except NoSuchElementException:
            pass
        
        # Estratégia 2: Por partial text
        if not link_visualizar:
            try:
                print("   Tentando: Link por texto parcial...")
                link_visualizar = driver.find_element(By.PARTIAL_LINK_TEXT, "Visual")
                print("   ✅ Encontrado por texto parcial!")
            except NoSuchElementException:
                pass
        
        # Estratégia 3: Por href contendo "download"
        if not link_visualizar:
            try:
                print("   Tentando: Link por href com 'download'...")
                link_visualizar = driver.find_element(By.CSS_SELECTOR, "a[href*='download']")
                print("   ✅ Encontrado por href!")
            except NoSuchElementException:
                pass
        
        # Estratégia 4: Buscar todos os links e filtrar
        if not link_visualizar:
            print("   Tentando: Buscar em todos os links...")
            todos_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"   Total de links: {len(todos_links)}")
            
            for i, link in enumerate(todos_links):
                try:
                    texto = link.text.strip().lower()
                    href = link.get_attribute("href") or ""
                    
                    if i < 20:  # Mostrar primeiros 20
                        print(f"   Link {i+1}: {texto[:40]} | href: {href[:50]}")
                    
                    if "visualizar" in texto or "download" in href.lower():
                        link_visualizar = link
                        print(f"   ✅ Encontrado: {texto} | {href}")
                        break
                except:
                    pass
        
        if not link_visualizar:
            print("   ❌ Link 'Visualizar' não encontrado")
            print("\n   💡 MODO MANUAL:")
            print("   O navegador ficará aberto. Clique manualmente no link 'Visualizar'")
            print("   Pressione ENTER quando terminar...")
            input()
            return {"sucesso": False, "erro": "link_nao_encontrado"}
        
        # 6. Obter informações do link
        print("\n5️⃣ Analisando link encontrado...")
        href = link_visualizar.get_attribute("href")
        onclick = link_visualizar.get_attribute("onclick")
        target = link_visualizar.get_attribute("target")
        
        print(f"   href: {href}")
        print(f"   onclick: {onclick}")
        print(f"   target: {target}")
        
        # 7. Clicar no link e capturar
        print("\n6️⃣ Clicando no link...")
        
        janelas_antes = driver.window_handles
        
        # Scroll até o elemento
        driver.execute_script("arguments[0].scrollIntoView(true);", link_visualizar)
        time.sleep(1)
        
        # Clicar
        link_visualizar.click()
        time.sleep(5)
        
        # Verificar novas janelas
        janelas_depois = driver.window_handles
        
        if len(janelas_depois) > len(janelas_antes):
            print("   ✅ Nova janela/aba aberta!")
            nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
            driver.switch_to.window(nova_janela)
            time.sleep(3)
            
            url_nova = driver.current_url
            print(f"   URL: {url_nova}")
            
            driver.save_screenshot(str(downloads_dir / "3_nova_janela.png"))
            
            # Verificar se é PDF
            if ".pdf" in url_nova.lower() or "download" in url_nova.lower():
                print("   🎉 URL de PDF encontrada!")
                
                # Baixar PDF
                try:
                    print("   Baixando PDF...")
                    response = requests.get(url_nova, stream=True, timeout=30)
                    
                    if response.status_code == 200:
                        filename = downloads_dir / f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                        
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"   ✅ OFÍCIO BAIXADO: {filename}")
                        driver.close()
                        driver.switch_to.window(janelas_antes[0])
                        return {"sucesso": True, "caminho": str(filename)}
                    else:
                        print(f"   ❌ Erro HTTP: {response.status_code}")
                
                except Exception as e:
                    print(f"   ❌ Erro ao baixar: {e}")
            
            driver.close()
            driver.switch_to.window(janelas_antes[0])
        
        # Verificar downloads automáticos
        print("\n7️⃣ Verificando downloads automáticos...")
        time.sleep(5)
        
        arquivos_pdf = list(downloads_dir.glob("*.pdf"))
        if arquivos_pdf:
            arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
            
            # Verificar se foi criado recentemente (últimos 30 segundos)
            if time.time() - arquivo_mais_recente.stat().st_mtime < 30:
                print(f"   ✅ OFÍCIO BAIXADO: {arquivo_mais_recente}")
                return {"sucesso": True, "caminho": str(arquivo_mais_recente)}
        
        print("\n   ⚠️  Ofício não foi baixado automaticamente")
        print("   💡 O processo existe, mas o ofício pode não estar disponível para download")
        print("\n   Navegador ficará aberto para inspeção manual...")
        print("   Pressione ENTER quando terminar...")
        input()
        
        return {"sucesso": False, "erro": "download_nao_realizado"}
        
    except Exception as e:
        print(f"\n❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\n   Navegador ficará aberto para debug...")
        print("   Pressione ENTER para fechar...")
        input()
        
        return {"sucesso": False, "erro": str(e)}
    
    finally:
        driver.quit()

# Executar
if __name__ == "__main__":
    resultado = buscar_oficio_tjsp_robusto("0034565-98.2018.8.26.0053")
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL:")
    print(f"Sucesso: {resultado.get('sucesso')}")
    if resultado.get('sucesso'):
        print(f"Arquivo: {resultado.get('caminho')}")
    else:
        print(f"Erro: {resultado.get('erro')}")
    print('='*60)
