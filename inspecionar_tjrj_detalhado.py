from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    
    print("Acessando TJRJ...")
    page.goto("http://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProc.do", wait_until="networkidle")
    time.sleep(5)
    
    # Salvar HTML completo
    html = page.content()
    with open("data/oficios/tjrj_pagina.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML salvo em: data/oficios/tjrj_pagina.html")
    
    # Verificar se há iframes
    print("\nVerificando iframes...")
    frames = page.frames
    print(f"Total de frames: {len(frames)}")
    
    for i, frame in enumerate(frames):
        print(f"\nFrame {i}: {frame.url}")
        
        # Tentar encontrar inputs em cada frame
        try:
            inputs = frame.locator("input").all()
            print(f"  Inputs encontrados: {len(inputs)}")
            
            for j, inp in enumerate(inputs[:5]):  # Mostrar apenas os 5 primeiros
                try:
                    name = inp.get_attribute("name") or "sem-name"
                    id_attr = inp.get_attribute("id") or "sem-id"
                    type_attr = inp.get_attribute("type") or "sem-type"
                    
                    print(f"    Input {j}: name={name}, id={id_attr}, type={type_attr}")
                except:
                    pass
        except Exception as e:
            print(f"  Erro ao inspecionar frame: {e}")
    
    # Verificar elementos visíveis
    print("\n\nVerificando elementos visíveis na página...")
    print(f"Título da página: {page.title()}")
    print(f"URL atual: {page.url}")
    
    # Tentar encontrar qualquer elemento de formulário
    print("\nBuscando formulários...")
    forms = page.locator("form").all()
    print(f"Formulários encontrados: {len(forms)}")
    
    for i, form in enumerate(forms):
        try:
            action = form.get_attribute("action") or "sem-action"
            method = form.get_attribute("method") or "sem-method"
            print(f"  Form {i}: action={action}, method={method}")
        except:
            pass
    
    # Buscar por texto específico
    print("\nBuscando texto 'processo' na página...")
    if "processo" in page.content().lower():
        print("✅ Texto 'processo' encontrado na página")
    else:
        print("❌ Texto 'processo' NÃO encontrado")
    
    print("\n\nPressione ENTER para fechar...")
    input()
    browser.close()
