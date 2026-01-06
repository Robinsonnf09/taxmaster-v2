from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    
    # Configurar contexto para evitar detecção de bot
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="pt-BR",
        timezone_id="America/Sao_Paulo"
    )
    
    page = context.new_page()
    
    # Tentar URLs alternativas do TJRJ
    urls_tjrj = [
        "http://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProc.do",
        "http://www4.tjrj.jus.br/consultaProcessoWebV2/",
        "http://www.tjrj.jus.br/",
        "https://www3.tjrj.jus.br/consultaprocessual/"
    ]
    
    for url in urls_tjrj:
        print(f"\n{'='*60}")
        print(f"Testando URL: {url}")
        print('='*60)
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            print(f"✅ Carregou com sucesso")
            print(f"Título: {page.title()}")
            print(f"URL final: {page.url}")
            
            # Verificar conteúdo
            content = page.content()
            print(f"Tamanho do HTML: {len(content)} caracteres")
            
            # Buscar inputs
            inputs = page.locator("input").all()
            print(f"Inputs encontrados: {len(inputs)}")
            
            if len(inputs) > 0:
                print("\n🎉 ENCONTRAMOS INPUTS!")
                for i, inp in enumerate(inputs[:5]):
                    try:
                        name = inp.get_attribute("name") or "sem-name"
                        id_attr = inp.get_attribute("id") or "sem-id"
                        type_attr = inp.get_attribute("type") or "sem-type"
                        print(f"  Input {i}: name={name}, id={id_attr}, type={type_attr}")
                    except:
                        pass
                
                # Salvar screenshot
                filename = f"data/oficios/tjrj_sucesso_{urls_tjrj.index(url)}.png"
                page.screenshot(path=filename)
                print(f"\n📸 Screenshot salvo: {filename}")
                
                print("\n✅ Esta é a URL correta!")
                print(f"URL: {url}")
                break
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print("\n\nPressione ENTER para fechar...")
    input()
    browser.close()
