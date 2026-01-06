from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="pt-BR",
        timezone_id="America/Sao_Paulo"
    )
    
    page = context.new_page()
    
    # URLs do TJSP para testar
    urls_tjsp = [
        "https://esaj.tjsp.jus.br/cpopg/open.do",
        "https://esaj.tjsp.jus.br/cpopg/show.do",
        "https://esaj.tjsp.jus.br/cpo/pg/open.do",
        "https://esaj.tjsp.jus.br/"
    ]
    
    for url in urls_tjsp:
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
            
            # Buscar inputs de texto
            inputs = page.locator("input[type='text'], input[type='search']").all()
            print(f"Inputs de texto encontrados: {len(inputs)}")
            
            if len(inputs) > 0:
                print("\n🎉 ENCONTRAMOS INPUTS!")
                for i, inp in enumerate(inputs):
                    try:
                        name = inp.get_attribute("name") or "sem-name"
                        id_attr = inp.get_attribute("id") or "sem-id"
                        placeholder = inp.get_attribute("placeholder") or "sem-placeholder"
                        visible = inp.is_visible()
                        
                        print(f"\n  Input {i}:")
                        print(f"    name: {name}")
                        print(f"    id: {id_attr}")
                        print(f"    placeholder: {placeholder}")
                        print(f"    visível: {visible}")
                    except Exception as e:
                        print(f"    Erro: {e}")
                
                # Buscar botões
                print("\n\n🔘 Buscando botões...")
                buttons = page.locator("button, input[type='submit'], input[type='button']").all()
                print(f"Botões encontrados: {len(buttons)}")
                
                for i, btn in enumerate(buttons[:5]):
                    try:
                        texto = btn.inner_text() or btn.get_attribute("value") or "sem-texto"
                        visible = btn.is_visible()
                        print(f"  Botão {i}: {texto} (visível: {visible})")
                    except:
                        pass
                
                # Salvar screenshot
                idx = urls_tjsp.index(url)
                filename = f"data/oficios/tjsp_sucesso_{idx}.png"
                page.screenshot(path=filename)
                print(f"\n📸 Screenshot salvo: {filename}")
                
                # Salvar HTML
                html_filename = f"data/oficios/tjsp_pagina_{idx}.html"
                with open(html_filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"💾 HTML salvo: {html_filename}")
                
                print("\n✅ Esta é a URL correta!")
                print(f"URL: {url}")
                
                # Testar preenchimento
                print("\n\n🧪 TESTANDO PREENCHIMENTO...")
                numero_teste = "1234567-89.2023.8.26.0100"
                
                try:
                    # Tentar preencher o primeiro input visível
                    for inp in inputs:
                        if inp.is_visible():
                            print(f"Tentando preencher input: {inp.get_attribute('id') or inp.get_attribute('name')}")
                            inp.fill(numero_teste)
                            print(f"✅ Preenchido com sucesso: {numero_teste}")
                            
                            time.sleep(2)
                            page.screenshot(path=f"data/oficios/tjsp_preenchido_{idx}.png")
                            print(f"📸 Screenshot do preenchimento salvo")
                            break
                except Exception as e:
                    print(f"❌ Erro ao preencher: {e}")
                
                break
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print("\n\nPressione ENTER para fechar...")
    input()
    browser.close()
