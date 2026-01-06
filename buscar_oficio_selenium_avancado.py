from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path
import requests

def buscar_oficio_tjsp_avancado(numero_processo):
    """Busca ofício requisitório no TJSP com tratamento avançado"""
    
    downloads_dir = Path("data/oficios")
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"BUSCA AVANÇADA DE OFÍCIO REQUISITÓRIO - TJSP")
    print(f"Processo: {numero_processo}")
    print('='*60)
    
    # Configurar Chrome
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
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # 1. Acessar consulta de requisitórios
        print("\n1️⃣ Acessando consulta de requisitórios...")
        driver.get("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do")
        time.sleep(3)
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
        time.sleep(5)
        
        driver.save_screenshot(str(downloads_dir / "2_resultado.png"))
        print("   ✅ Resultado carregado")
        
        # 4. Procurar link de visualização
        print("\n4️⃣ Procurando link de visualização...")
        
        # Tentar encontrar link "Visualizar"
        try:
            link_visualizar = wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Visualizar"))
            )
            print("   ✅ Link 'Visualizar' encontrado!")
            
            # Obter URL do link
            href = link_visualizar.get_attribute("href")
            onclick = link_visualizar.get_attribute("onclick")
            
            print(f"   href: {href}")
            print(f"   onclick: {onclick}")
            
            # 5. Estratégia: Capturar requisição ao clicar
            print("\n5️⃣ Clicando no link e capturando download...")
            
            # Guardar janelas atuais
            janelas_antes = driver.window_handles
            
            # Clicar no link
            link_visualizar.click()
            time.sleep(3)
            
            # Verificar se abriu nova janela/aba
            janelas_depois = driver.window_handles
            
            if len(janelas_depois) > len(janelas_antes):
                print("   ✅ Nova janela aberta!")
                nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                driver.switch_to.window(nova_janela)
                time.sleep(3)
                
                driver.save_screenshot(str(downloads_dir / "3_nova_janela.png"))
                print(f"   URL da nova janela: {driver.current_url}")
                
                # Verificar se é PDF
                if ".pdf" in driver.current_url.lower() or "download" in driver.current_url.lower():
                    print("   🎉 URL de PDF encontrada!")
                    
                    # Baixar PDF diretamente
                    try:
                        response = requests.get(driver.current_url, stream=True)
                        filename = downloads_dir / f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                        
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"   ✅ OFÍCIO BAIXADO: {filename}")
                        return {"sucesso": True, "caminho": str(filename)}
                    
                    except Exception as e:
                        print(f"   ❌ Erro ao baixar: {e}")
                
                driver.close()
                driver.switch_to.window(janelas_antes[0])
            
            # Verificar se arquivo foi baixado automaticamente
            time.sleep(5)
            arquivos_pdf = list(downloads_dir.glob("*.pdf"))
            
            if arquivos_pdf:
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                print(f"   ✅ OFÍCIO BAIXADO: {arquivo_mais_recente}")
                return {"sucesso": True, "caminho": str(arquivo_mais_recente)}
            
            print("   ⚠️  Nenhum arquivo baixado automaticamente")
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
        
        # 6. Alternativa: Procurar iframe com PDF
        print("\n6️⃣ Procurando iframe com PDF...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   Iframes encontrados: {len(iframes)}")
        
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and ".pdf" in src.lower():
                print(f"   🎉 PDF no iframe: {src}")
                
                # Baixar PDF
                try:
                    response = requests.get(src, stream=True)
                    filename = downloads_dir / f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"   ✅ OFÍCIO BAIXADO: {filename}")
                    return {"sucesso": True, "caminho": str(filename)}
                
                except Exception as e:
                    print(f"   ❌ Erro ao baixar: {e}")
        
        print("\n   ⚠️  Não foi possível baixar o ofício automaticamente")
        print("   💡 O processo existe, mas o ofício pode não estar disponível")
        
        return {"sucesso": False, "erro": "oficio_nao_disponivel"}
        
    except Exception as e:
        print(f"\n❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"sucesso": False, "erro": str(e)}
    
    finally:
        print("\n   Pressione ENTER para fechar...")
        input()
        driver.quit()

# Executar
resultado = buscar_oficio_tjsp_avancado("0034565-98.2018.8.26.0053")
print(f"\n{'='*60}")
print(f"RESULTADO FINAL: {resultado}")
print('='*60)
