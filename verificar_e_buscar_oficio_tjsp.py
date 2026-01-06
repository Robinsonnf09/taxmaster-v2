from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path

def verificar_e_buscar_oficio_tjsp(numero_processo):
    """Verifica processo e busca ofício - Estratégia completa"""
    
    downloads_dir = Path("data/oficios")
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"VERIFICAÇÃO E BUSCA DE OFÍCIO - TJSP")
    print(f"Processo: {numero_processo}")
    print('='*60)
    
    # Configurar Chrome
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": str(downloads_dir.absolute()),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # ETAPA 1: Verificar se o processo existe na consulta processual normal
        print("\n📋 ETAPA 1: Verificando se o processo existe...")
        print("="*60)
        
        driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        partes = numero_processo.split('.')
        parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
        parte2 = partes[4]
        
        print(f"Preenchendo: {parte1} / {parte2}")
        
        driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
        driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
        
        driver.save_screenshot(str(downloads_dir / "etapa1_consulta_normal.png"))
        
        driver.find_element(By.ID, "botaoConsultarProcessos").click()
        time.sleep(5)
        
        driver.save_screenshot(str(downloads_dir / "etapa1_resultado.png"))
        
        page_source = driver.page_source.lower()
        
        if "não encontrado" in page_source or "não existem" in page_source:
            print("❌ Processo NÃO EXISTE no TJSP")
            print("\n💡 Possíveis causas:")
            print("   1. Número do processo incorreto")
            print("   2. Processo é de outro tribunal")
            print("   3. Processo foi arquivado/excluído")
            
            print("\n🔍 Vamos tentar formatos alternativos...")
            
            # Tentar formato antigo
            print("\nTentando formato SAJ antigo...")
            driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(3)
            
            # Clicar no radio "Processo do Foro"
            try:
                driver.find_element(By.ID, "radioNumeroAntigo").click()
                time.sleep(1)
                
                # Preencher no campo de processo antigo
                driver.find_element(By.ID, "nuProcessoAntigoFormatado").send_keys(numero_processo)
                driver.find_element(By.ID, "botaoConsultarProcessos").click()
                time.sleep(5)
                
                driver.save_screenshot(str(downloads_dir / "etapa1_formato_antigo.png"))
                
                page_source = driver.page_source.lower()
                
                if "não encontrado" not in page_source and "não existem" not in page_source:
                    print("✅ Processo encontrado com formato antigo!")
                else:
                    print("❌ Processo não encontrado nem com formato antigo")
            except:
                print("⚠️  Não foi possível tentar formato antigo")
            
            print("\n📸 Verifique os screenshots:")
            print("   - etapa1_consulta_normal.png")
            print("   - etapa1_resultado.png")
            print("   - etapa1_formato_antigo.png")
            
            print("\n🌐 O navegador ficará aberto para você verificar manualmente...")
            print("Pressione ENTER quando terminar...")
            input()
            
            return {"sucesso": False, "erro": "processo_nao_existe"}
        
        print("✅ Processo EXISTE no TJSP!")
        
        # Extrair informações do processo
        print("\n📊 Informações do processo:")
        try:
            # Tentar extrair dados básicos
            if "assunto" in page_source:
                print("   ✅ Página com dados do processo carregada")
            
            # Procurar por links de documentos
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"\n   Total de links na página: {len(links)}")
            
            print("\n   🔗 Links relevantes:")
            for i, link in enumerate(links[:30]):
                try:
                    texto = link.text.strip()
                    if texto and len(texto) > 3:
                        print(f"   {i+1}. {texto[:60]}")
                        
                        if any(palavra in texto.lower() for palavra in ["documento", "ofício", "requisitório", "visualizar"]):
                            print(f"      🎯 RELEVANTE!")
                except:
                    pass
        except Exception as e:
            print(f"   ⚠️  Erro ao extrair informações: {e}")
        
        # ETAPA 2: Buscar na consulta de requisitórios
        print("\n\n📋 ETAPA 2: Buscando na Consulta de Requisitórios...")
        print("="*60)
        
        driver.get("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do")
        time.sleep(3)
        
        driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
        driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
        
        driver.save_screenshot(str(downloads_dir / "etapa2_requisitorios_preenchido.png"))
        
        driver.find_element(By.ID, "botaoConsultarProcessos").click()
        time.sleep(5)
        
        driver.save_screenshot(str(downloads_dir / "etapa2_requisitorios_resultado.png"))
        
        page_source = driver.page_source.lower()
        
        if "não encontrado" in page_source or "não existem" in page_source:
            print("⚠️  Processo não tem requisitórios cadastrados")
            print("\n💡 Isso significa:")
            print("   - O processo existe no TJSP")
            print("   - MAS não tem ofício requisitório expedido")
            print("   - OU o ofício não está disponível online")
            
            print("\n🌐 O navegador ficará aberto para você verificar...")
            print("Pressione ENTER quando terminar...")
            input()
            
            return {"sucesso": False, "erro": "sem_requisitorios"}
        
        print("✅ Requisitórios encontrados!")
        
        # Procurar link de visualização
        print("\n🔍 Procurando link de visualização...")
        
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   Total de links: {len(links)}")
        
        for i, link in enumerate(links):
            try:
                texto = link.text.strip().lower()
                href = link.get_attribute("href") or ""
                
                if i < 30:
                    print(f"   {i+1}. {texto[:50]} | {href[:50]}")
                
                if "visualizar" in texto or "download" in href.lower():
                    print(f"\n   🎉 LINK ENCONTRADO: {texto}")
                    print(f"   URL: {href}")
                    
                    # Tentar clicar
                    print("\n   Clicando no link...")
                    janelas_antes = driver.window_handles
                    
                    link.click()
                    time.sleep(5)
                    
                    janelas_depois = driver.window_handles
                    
                    if len(janelas_depois) > len(janelas_antes):
                        print("   ✅ Nova janela aberta!")
                        nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                        driver.switch_to.window(nova_janela)
                        
                        print(f"   URL da nova janela: {driver.current_url}")
                        driver.save_screenshot(str(downloads_dir / "etapa2_visualizacao.png"))
                        
                        # Aguardar download
                        time.sleep(5)
                        
                        # Verificar se baixou
                        arquivos = list(downloads_dir.glob("*.pdf"))
                        if arquivos:
                            mais_recente = max(arquivos, key=lambda p: p.stat().st_mtime)
                            if time.time() - mais_recente.stat().st_mtime < 30:
                                print(f"\n   ✅ OFÍCIO BAIXADO: {mais_recente}")
                                return {"sucesso": True, "caminho": str(mais_recente)}
                        
                        driver.close()
                        driver.switch_to.window(janelas_antes[0])
                    
                    break
            except:
                pass
        
        print("\n⚠️  Não foi possível baixar automaticamente")
        print("\n🌐 O navegador ficará aberto para você tentar manualmente...")
        print("Pressione ENTER quando terminar...")
        input()
        
        return {"sucesso": False, "erro": "download_manual_necessario"}
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\n🌐 Navegador ficará aberto para debug...")
        print("Pressione ENTER para fechar...")
        input()
        
        return {"sucesso": False, "erro": str(e)}
    
    finally:
        driver.quit()

# Executar
if __name__ == "__main__":
    # Testar com o processo fornecido
    resultado = verificar_e_buscar_oficio_tjsp("0034565-98.2018.8.26.0053")
    
    print(f"\n{'='*60}")
    print("RESULTADO FINAL:")
    print(f"Sucesso: {resultado['sucesso']}")
    if resultado['sucesso']:
        print(f"Arquivo: {resultado['caminho']}")
    else:
        print(f"Erro: {resultado['erro']}")
    print('='*60)
