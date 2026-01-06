from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    
    print("Acessando TJRJ...")
    page.goto("http://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProc.do")
    time.sleep(5)
    
    print("\nInspecionando campos de input...")
    inputs = page.locator("input").all()
    
    for i, inp in enumerate(inputs):
        try:
            name = inp.get_attribute("name") or "sem-name"
            id_attr = inp.get_attribute("id") or "sem-id"
            type_attr = inp.get_attribute("type") or "sem-type"
            placeholder = inp.get_attribute("placeholder") or "sem-placeholder"
            
            print(f"\nInput {i}:")
            print(f"  name: {name}")
            print(f"  id: {id_attr}")
            print(f"  type: {type_attr}")
            print(f"  placeholder: {placeholder}")
        except:
            pass
    
    print("\n\nInspecionando botões...")
    buttons = page.locator("button, input[type='submit'], input[type='button']").all()
    
    for i, btn in enumerate(buttons):
        try:
            value = btn.get_attribute("value") or btn.inner_text() or "sem-texto"
            print(f"\nBotão {i}: {value}")
        except:
            pass
    
    print("\n\nPressione ENTER para fechar...")
    input()
    browser.close()
