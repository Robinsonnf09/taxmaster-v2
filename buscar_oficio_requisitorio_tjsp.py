from playwright.sync_api import sync_playwright
import time
from pathlib import Path

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    
    numero_processo = "0034565-98.2018.8.26.0053"
    
    print(f"\n{'='*60}")
    print(f"BUSCANDO OFÍCIO REQUISITÓRIO NO TJSP")
    print(f"Número: {numero_processo}")
    print('='*60)
    
    try:
        # 1. Acessar página de consulta de requisitórios
        print("\n1️⃣ Acessando página de Consulta de Requisitórios...")
        page.goto("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do", wait_until="domcontentloaded")
        time.sleep(3)
        
        print(f"   ✅ Página carregada: {page.url}")
        page.screenshot(path="data/oficios/tjsp_req_1_inicial.png")
        print(f"   📸 Screenshot: tjsp_req_1_inicial.png")
        
        # 2. Preencher número do processo
        print("\n2️⃣ Preenchendo número do processo...")
        
        # Verificar campos disponíveis
        inputs = page.locator("input[type='text']").all()
        print(f"   Campos de texto encontrados: {len(inputs)}")
        
        for i, inp in enumerate(inputs):
            try:
                name = inp.get_attribute("name") or "sem-name"
                id_attr = inp.get_attribute("id") or "sem-id"
                placeholder = inp.get_attribute("placeholder") or ""
                visible = inp.is_visible()
                
                print(f"   Campo {i}: name={name}, id={id_attr}, visible={visible}")
                
                if visible and placeholder:
                    print(f"      Placeholder: {placeholder}")
            except:
                pass
        
        # Tentar preencher o campo de busca
        try:
            # Procurar campo que aceita número do processo
            campo_processo = None
            
            # Tentar diferentes seletores
            seletores = [
                "input[name*='processo']",
                "input[name*='Processo']",
                "input[id*='processo']",
                "input[placeholder*='processo']",
                "input[type='text']"
            ]
            
            for seletor in seletores:
                if page.locator(seletor).count() > 0:
                    campo = page.locator(seletor).first
                    if campo.is_visible():
                        print(f"   Usando campo: {seletor}")
                        campo.fill(numero_processo)
                        print(f"   ✅ Número preenchido: {numero_processo}")
                        campo_processo = campo
                        break
            
            if not campo_processo:
                print("   ❌ Campo de busca não encontrado")
                print("\n   💡 Preencha manualmente o número do processo no navegador")
                print("   Depois pressione ENTER aqui...")
                input()
            
            time.sleep(2)
            page.screenshot(path="data/oficios/tjsp_req_2_preenchido.png")
            print(f"   📸 Screenshot: tjsp_req_2_preenchido.png")
            
        except Exception as e:
            print(f"   ⚠️  Erro ao preencher: {e}")
        
        # 3. Clicar no botão de pesquisa
        print("\n3️⃣ Clicando no botão de pesquisa...")
        
        botoes = [
            "input[value*='Pesquisar']",
            "input[value*='Consultar']",
            "button:has-text('Pesquisar')",
            "button:has-text('Consultar')",
            "input[type='submit']",
            "button[type='submit']"
        ]
        
        botao_clicado = False
        for seletor in botoes:
            try:
                if page.locator(seletor).count() > 0:
                    botao = page.locator(seletor).first
                    if botao.is_visible():
                        print(f"   Clicando: {seletor}")
                        botao.click()
                        botao_clicado = True
                        break
            except:
                pass
        
        if not botao_clicado:
            print("   ⚠️  Botão não encontrado")
            print("   💡 Clique manualmente no botão de pesquisa")
            print("   Depois pressione ENTER aqui...")
            input()
        
        time.sleep(5)
        page.screenshot(path="data/oficios/tjsp_req_3_resultado.png")
        print(f"   📸 Screenshot: tjsp_req_3_resultado.png")
        print(f"   ✅ Resultado carregado: {page.url}")
        
        # 4. Buscar ofícios na página de resultado
        print("\n4️⃣ Buscando ofícios na página de resultado...")
        
        # Listar todos os links
        links = page.locator("a").all()
        print(f"   Total de links: {len(links)}")
        
        print("\n   📋 Links encontrados:")
        for i, link in enumerate(links[:50]):
            try:
                texto = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                
                if texto:
                    print(f"   {i+1}. {texto[:70]}")
                    
                    # Marcar possíveis ofícios
                    if any(palavra in texto.lower() for palavra in ["ofício", "requisitório", "download", "visualizar", "pdf"]):
                        print(f"      🎯 POSSÍVEL OFÍCIO! Href: {href[:60]}")
            except:
                pass
        
        # 5. Tentar baixar ofícios
        print("\n5️⃣ Tentando baixar ofícios...")
        
        oficio_baixado = False
        for link in links:
            try:
                texto = link.inner_text().strip().lower()
                href = link.get_attribute("href") or ""
                
                # Procurar por links de visualização/download
                if any(palavra in texto for palavra in ["visualizar", "download", "abrir", "ver"]) or \
                   ".pdf" in href.lower():
                    
                    print(f"\n   🎉 TENTANDO: {link.inner_text()[:50]}")
                    
                    try:
                        # Tentar clicar e capturar download
                        with page.expect_download(timeout=10000) as download_info:
                            link.click()
                            time.sleep(2)
                        
                        download = download_info.value
                        filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{int(time.time())}.pdf"
                        filepath = Path("data/oficios") / filename
                        download.save_as(filepath)
                        
                        print(f"   ✅ OFÍCIO BAIXADO: {filepath}")
                        oficio_baixado = True
                        
                    except:
                        # Se não baixou, pode ter aberto em nova aba
                        print(f"   ⚠️  Não iniciou download direto")
                        
            except:
                pass
        
        if not oficio_baixado:
            print("\n   ⚠️  Nenhum ofício foi baixado automaticamente")
            print("\n   💡 INSTRUÇÕES MANUAIS:")
            print("   1. Verifique o screenshot: tjsp_req_3_resultado.png")
            print("   2. Procure por links de 'Visualizar Ofício' ou 'Download'")
            print("   3. Clique manualmente no navegador")
            print("\n   O navegador permanecerá aberto para você explorar...")
            print("   Pressione ENTER quando terminar...")
            input()
        
        # Salvar HTML
        with open("data/oficios/tjsp_req_final.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"\n   💾 HTML salvo: tjsp_req_final.html")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    browser.close()
