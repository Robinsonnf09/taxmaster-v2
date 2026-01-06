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
        
        print(f"   ✅ Página carregada")
        page.screenshot(path="data/oficios/tjsp_req_1_inicial.png")
        
        # 2. Preencher número do processo CORRETAMENTE
        print("\n2️⃣ Preenchendo número do processo...")
        
        # Separar número: NNNNNNN-DD.AAAA.J.TR.OOOO
        partes = numero_processo.split('.')
        parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"  # 0034565-98.2018.8.26
        parte2 = partes[4]  # 0053
        
        print(f"   Parte 1: {parte1}")
        print(f"   Parte 2: {parte2}")
        
        # Preencher campo 1 (numeroDigitoAnoUnificado)
        page.fill("#numeroDigitoAnoUnificado", parte1)
        print(f"   ✅ Campo 1 preenchido")
        
        # Preencher campo 2 (foroNumeroUnificado)
        page.fill("#foroNumeroUnificado", parte2)
        print(f"   ✅ Campo 2 preenchido")
        
        time.sleep(2)
        page.screenshot(path="data/oficios/tjsp_req_2_preenchido.png")
        print(f"   📸 Screenshot: tjsp_req_2_preenchido.png")
        
        # 3. Clicar no botão de consulta
        print("\n3️⃣ Clicando no botão de consulta...")
        page.click("#botaoConsultarProcessos")
        time.sleep(5)
        
        page.screenshot(path="data/oficios/tjsp_req_3_resultado.png")
        print(f"   📸 Screenshot: tjsp_req_3_resultado.png")
        print(f"   ✅ Resultado carregado")
        
        # 4. Verificar se encontrou o processo
        conteudo = page.content().lower()
        
        if "não encontrado" in conteudo or "não existem" in conteudo:
            print("\n   ❌ Processo não encontrado")
        else:
            print("\n   ✅ PROCESSO ENCONTRADO!")
            
            # 5. Buscar tabela de requisitórios
            print("\n4️⃣ Buscando tabela de requisitórios...")
            
            # Procurar por tabelas
            tabelas = page.locator("table").all()
            print(f"   Tabelas encontradas: {len(tabelas)}")
            
            # Procurar por links dentro das tabelas
            links_tabela = []
            for tabela in tabelas:
                try:
                    links = tabela.locator("a").all()
                    for link in links:
                        try:
                            texto = link.inner_text().strip()
                            href = link.get_attribute("href") or ""
                            if texto:
                                links_tabela.append({"texto": texto, "href": href, "element": link})
                        except:
                            pass
                except:
                    pass
            
            print(f"   Links em tabelas: {len(links_tabela)}")
            
            if links_tabela:
                print("\n   📋 Links encontrados nas tabelas:")
                for i, link_info in enumerate(links_tabela[:20]):
                    print(f"   {i+1}. {link_info['texto'][:60]}")
                    if any(palavra in link_info['texto'].lower() for palavra in ["visualizar", "download", "ofício", "pdf"]):
                        print(f"      🎯 POSSÍVEL OFÍCIO! Href: {link_info['href'][:60]}")
            
            # 6. Procurar especificamente por "Visualizar" ou ícones de documento
            print("\n5️⃣ Procurando links de visualização/download...")
            
            # Procurar por links com texto "Visualizar"
            links_visualizar = page.locator("a:has-text('Visualizar')").all()
            print(f"   Links 'Visualizar': {len(links_visualizar)}")
            
            # Procurar por ícones/imagens de documento
            links_com_img = page.locator("a:has(img)").all()
            print(f"   Links com imagens: {len(links_com_img)}")
            
            # Tentar baixar ofícios
            print("\n6️⃣ Tentando baixar ofícios...")
            
            oficio_baixado = False
            
            # Tentar links "Visualizar"
            for i, link in enumerate(links_visualizar):
                try:
                    print(f"\n   🎉 TENTANDO: Visualizar {i+1}")
                    
                    with page.expect_download(timeout=10000) as download_info:
                        link.click()
                        time.sleep(2)
                    
                    download = download_info.value
                    filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{i}.pdf"
                    filepath = Path("data/oficios") / filename
                    download.save_as(filepath)
                    
                    print(f"   ✅ OFÍCIO BAIXADO: {filepath}")
                    oficio_baixado = True
                    
                except Exception as e:
                    print(f"   ⚠️  Não baixou: {str(e)[:50]}")
            
            # Se não baixou, tentar links com imagens
            if not oficio_baixado:
                for i, link in enumerate(links_com_img[:5]):
                    try:
                        texto = link.inner_text().strip()
                        if texto:
                            print(f"\n   🎉 TENTANDO: {texto[:40]}")
                        else:
                            print(f"\n   🎉 TENTANDO: Link com imagem {i+1}")
                        
                        with page.expect_download(timeout=10000) as download_info:
                            link.click()
                            time.sleep(2)
                        
                        download = download_info.value
                        filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{i}.pdf"
                        filepath = Path("data/oficios") / filename
                        download.save_as(filepath)
                        
                        print(f"   ✅ OFÍCIO BAIXADO: {filepath}")
                        oficio_baixado = True
                        break
                        
                    except:
                        pass
            
            if not oficio_baixado:
                print("\n   ⚠️  Nenhum ofício foi baixado automaticamente")
                print("\n   💡 Verifique os screenshots:")
                print("      - tjsp_req_3_resultado.png")
                print("\n   O navegador ficará aberto para você explorar...")
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
