from playwright.sync_api import sync_playwright
import time
from pathlib import Path
import urllib.parse

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    
    # Número do processo de teste
    numero_processo = "0034565-98.2018.8.26.0053"
    
    print(f"\n{'='*60}")
    print(f"BUSCANDO REQUISITÓRIOS NO TJSP")
    print(f"Número: {numero_processo}")
    print('='*60)
    
    try:
        # Construir URL com parâmetro consultaDeRequisitorios=true
        print("\n1️⃣ Construindo URL de busca de requisitórios...")
        
        base_url = "https://esaj.tjsp.jus.br/cpopg/search.do"
        params = {
            "conversationId": "",
            "cbPesquisa": "NUMPROC",
            "numeroDigitoAnoUnificado": "",
            "foroNumeroUnificado": "",
            "dadosConsulta.valorConsultaNuUnificado": "",
            "dadosConsulta.valorConsultaNuUnificado": "UNIFICADO",
            "dadosConsulta.valorConsulta": numero_processo,
            "dadosConsulta.tipoNuProcesso": "SAJ",
            "consultaDeRequisitorios": "true"  # PARÂMETRO CHAVE!
        }
        
        url_completa = f"{base_url}?{urllib.parse.urlencode(params)}"
        print(f"   URL: {url_completa[:100]}...")
        
        # Acessar diretamente a URL de busca de requisitórios
        print("\n2️⃣ Acessando portal com busca de requisitórios...")
        page.goto(url_completa, wait_until="domcontentloaded")
        time.sleep(5)
        
        print(f"   ✅ Página carregada")
        print(f"   URL final: {page.url[:100]}...")
        
        page.screenshot(path="data/oficios/tjsp_requisitorios_resultado.png")
        print(f"   📸 Screenshot: tjsp_requisitorios_resultado.png")
        
        # Verificar conteúdo
        conteudo = page.content().lower()
        
        if "não encontrado" in conteudo or "não existem" in conteudo:
            print("\n   ❌ Processo ou requisitórios não encontrados")
        else:
            print("\n   ✅ PÁGINA DE REQUISITÓRIOS CARREGADA!")
            
            # Buscar ofícios/requisitórios
            print("\n3️⃣ Buscando ofícios requisitórios...")
            
            # Procurar por links de download
            links = page.locator("a").all()
            print(f"   Total de links: {len(links)}")
            
            print("\n   📋 Links encontrados:")
            for i, link in enumerate(links[:30]):
                try:
                    texto = link.inner_text().strip()
                    href = link.get_attribute("href") or ""
                    
                    if texto:
                        print(f"   {i+1}. {texto[:60]}")
                        
                        # Verificar se é ofício/requisitório
                        if any(palavra in texto.lower() for palavra in ["ofício", "requisitório", "requisitorio", "oficio", "download", "pdf"]):
                            print(f"      🎯 POSSÍVEL OFÍCIO!")
                            print(f"      Href: {href[:80]}")
                except:
                    pass
            
            # Tentar baixar ofícios
            print("\n4️⃣ Tentando baixar ofícios...")
            
            oficio_baixado = False
            for link in links:
                try:
                    texto = link.inner_text().lower()
                    href = link.get_attribute("href") or ""
                    
                    # Verificar se é link de ofício/requisitório
                    if any(palavra in texto for palavra in ["ofício", "requisitório", "requisitorio", "oficio"]) or \
                       any(palavra in href.lower() for palavra in ["oficio", "requisitorio", "download", ".pdf"]):
                        
                        print(f"\n   🎉 TENTANDO BAIXAR: {link.inner_text()[:50]}")
                        
                        try:
                            with page.expect_download(timeout=15000) as download_info:
                                link.click()
                                time.sleep(2)
                            
                            download = download_info.value
                            filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{int(time.time())}.pdf"
                            filepath = Path("data/oficios") / filename
                            download.save_as(filepath)
                            
                            print(f"   ✅ OFÍCIO BAIXADO!")
                            print(f"   Arquivo: {filepath}")
                            oficio_baixado = True
                            
                        except Exception as e:
                            print(f"   ⚠️  Não foi possível baixar: {str(e)[:50]}")
                            
                except:
                    pass
            
            if not oficio_baixado:
                print("\n   ⚠️  Nenhum ofício foi baixado")
                print("   💡 Possíveis causas:")
                print("      - Ofício não está disponível para download")
                print("      - Ofício requer autenticação")
                print("      - Processo não possui ofício expedido")
        
        # Salvar HTML
        with open("data/oficios/tjsp_requisitorios.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"\n   💾 HTML salvo: tjsp_requisitorios.html")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Pressione ENTER para fechar...")
    input()
    browser.close()
