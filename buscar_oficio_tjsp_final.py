from playwright.sync_api import sync_playwright
import time
from pathlib import Path

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context()
    page = context.new_page()
    
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
        print(f"   ✅ Página carregada")
        
        # 2. Preencher número do processo
        print("\n2️⃣ Preenchendo número do processo...")
        partes = numero_processo.split('.')
        parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
        parte2 = partes[4]
        
        page.fill("#numeroDigitoAnoUnificado", parte1)
        page.fill("#foroNumeroUnificado", parte2)
        print(f"   ✅ Campos preenchidos: {parte1} / {parte2}")
        
        page.screenshot(path="data/oficios/tjsp_req_preenchido.png")
        
        # 3. Clicar no botão de consulta
        print("\n3️⃣ Clicando no botão de consulta...")
        page.click("#botaoConsultarProcessos")
        time.sleep(5)
        
        page.screenshot(path="data/oficios/tjsp_req_resultado.png")
        print(f"   ✅ Resultado carregado")
        
        # 4. Verificar se encontrou
        conteudo = page.content().lower()
        
        if "não encontrado" in conteudo or "não existem" in conteudo:
            print("\n   ❌ Processo não encontrado")
        else:
            print("\n   ✅ PROCESSO ENCONTRADO!")
            
            # 5. Buscar link "Visualizar" e extrair URL
            print("\n4️⃣ Analisando link de visualização...")
            
            link_visualizar = page.locator("a:has-text('Visualizar')").first
            
            if link_visualizar:
                # Extrair atributos do link
                href = link_visualizar.get_attribute("href")
                onclick = link_visualizar.get_attribute("onclick")
                target = link_visualizar.get_attribute("target")
                
                print(f"   Link encontrado:")
                print(f"   - href: {href}")
                print(f"   - onclick: {onclick}")
                print(f"   - target: {target}")
                
                # Estratégia 1: Se tem onclick, executar o JavaScript
                if onclick:
                    print("\n5️⃣ Executando JavaScript do link...")
                    try:
                        # Capturar nova aba/popup
                        with context.expect_page() as new_page_info:
                            page.evaluate(onclick)
                            time.sleep(2)
                        
                        nova_pagina = new_page_info.value
                        nova_pagina.wait_for_load_state("domcontentloaded")
                        time.sleep(3)
                        
                        print(f"   ✅ Nova página aberta: {nova_pagina.url}")
                        nova_pagina.screenshot(path="data/oficios/tjsp_req_visualizar.png")
                        
                        # Tentar baixar PDF
                        try:
                            with nova_pagina.expect_download(timeout=10000) as download_info:
                                # Procurar botão de download na nova página
                                botoes_download = [
                                    "a:has-text('Download')",
                                    "a:has-text('Baixar')",
                                    "button:has-text('Download')",
                                    "a[href*='.pdf']"
                                ]
                                
                                for seletor in botoes_download:
                                    if nova_pagina.locator(seletor).count() > 0:
                                        print(f"   Clicando em: {seletor}")
                                        nova_pagina.click(seletor)
                                        break
                            
                            download = download_info.value
                            filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                            filepath = Path("data/oficios") / filename
                            download.save_as(filepath)
                            
                            print(f"\n   ✅ OFÍCIO BAIXADO: {filepath}")
                            
                        except:
                            print(f"   ⚠️  Não iniciou download na nova página")
                            
                            # Salvar HTML da nova página
                            with open("data/oficios/tjsp_req_visualizar.html", "w", encoding="utf-8") as f:
                                f.write(nova_pagina.content())
                            print(f"   💾 HTML da página de visualização salvo")
                        
                        nova_pagina.close()
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao executar onclick: {str(e)[:100]}")
                
                # Estratégia 2: Se tem href, navegar diretamente
                elif href and href != "#" and href != "javascript:void(0)":
                    print("\n5️⃣ Navegando para URL do link...")
                    try:
                        if href.startswith("http"):
                            url_completa = href
                        else:
                            url_completa = f"https://esaj.tjsp.jus.br{href}"
                        
                        print(f"   URL: {url_completa}")
                        
                        with context.expect_page() as new_page_info:
                            page.goto(url_completa)
                            time.sleep(3)
                        
                        nova_pagina = new_page_info.value
                        print(f"   ✅ Página aberta: {nova_pagina.url}")
                        nova_pagina.screenshot(path="data/oficios/tjsp_req_visualizar.png")
                        
                    except:
                        print(f"   ⚠️  Não conseguiu navegar")
                
                else:
                    print("\n   ⚠️  Link não tem href ou onclick válido")
            
            # 6. Alternativa: Procurar iframe com PDF
            print("\n6️⃣ Procurando por iframe com PDF...")
            iframes = page.locator("iframe").all()
            print(f"   Iframes encontrados: {len(iframes)}")
            
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src")
                    if src and ".pdf" in src.lower():
                        print(f"\n   🎉 PDF ENCONTRADO NO IFRAME!")
                        print(f"   URL: {src}")
                        
                        # Baixar PDF diretamente
                        if src.startswith("http"):
                            url_pdf = src
                        else:
                            url_pdf = f"https://esaj.tjsp.jus.br{src}"
                        
                        print(f"   Baixando de: {url_pdf}")
                        
                        # Navegar para o PDF
                        pdf_page = context.new_page()
                        pdf_page.goto(url_pdf)
                        time.sleep(3)
                        
                        # Salvar PDF
                        filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                        filepath = Path("data/oficios") / filename
                        
                        # Tentar salvar como PDF
                        pdf_page.pdf(path=str(filepath))
                        print(f"   ✅ PDF SALVO: {filepath}")
                        
                        pdf_page.close()
                        break
                        
                except Exception as e:
                    print(f"   Erro no iframe {i}: {str(e)[:50]}")
            
            print("\n   💡 Se não baixou automaticamente:")
            print("   1. Verifique o screenshot: tjsp_req_resultado.png")
            print("   2. Clique manualmente no link 'Visualizar'")
            print("   3. O navegador ficará aberto...")
            print("\n   Pressione ENTER quando terminar...")
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
