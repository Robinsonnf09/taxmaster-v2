from playwright.sync_api import sync_playwright
import time
import re
from pathlib import Path
import sys
sys.path.append("src")
from database import SessionLocal, Processo

# Conectar ao banco e pegar um processo real do TJSP
db = SessionLocal()
processo_tjsp = db.query(Processo).filter(Processo.tribunal == "TJSP").first()

if not processo_tjsp:
    print("❌ Nenhum processo do TJSP encontrado no banco de dados")
    exit()

numero_processo = processo_tjsp.numero_processo
print(f"\n{'='*60}")
print(f"USANDO PROCESSO REAL DO BANCO DE DADOS")
print(f"Número: {numero_processo}")
print(f"Credor: {processo_tjsp.credor_nome}")
print(f"Valor: R$ {processo_tjsp.valor_atualizado:,.2f}")
print('='*60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    
    try:
        # 1. Acessar portal
        print("\n1️⃣ Acessando portal do TJSP...")
        page.goto("https://esaj.tjsp.jus.br/cpopg/open.do", wait_until="domcontentloaded")
        time.sleep(3)
        print(f"   ✅ Portal carregado")
        
        # 2. Preencher número do processo
        print("\n2️⃣ Preenchendo número do processo...")
        
        # Verificar formato do número
        if "." in numero_processo and "-" in numero_processo:
            partes = numero_processo.split('.')
            if len(partes) >= 5:
                parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
                parte2 = partes[4]
            else:
                print("   ⚠️  Formato do número não reconhecido")
                parte1 = numero_processo
                parte2 = ""
        else:
            print("   ⚠️  Número sem formatação padrão")
            parte1 = numero_processo
            parte2 = ""
        
        print(f"   Parte 1: {parte1}")
        print(f"   Parte 2: {parte2}")
        
        # Preencher campos
        page.fill("#numeroDigitoAnoUnificado", parte1)
        print(f"   ✅ Campo 1 preenchido")
        
        if parte2:
            page.fill("#foroNumeroUnificado", parte2)
            print(f"   ✅ Campo 2 preenchido")
        
        time.sleep(2)
        page.screenshot(path="data/oficios/tjsp_busca_real_preenchido.png")
        
        # 3. Clicar em pesquisar
        print("\n3️⃣ Clicando em pesquisar...")
        page.click("#botaoConsultarProcessos")
        time.sleep(5)
        
        page.screenshot(path="data/oficios/tjsp_busca_real_resultado.png")
        print(f"   📸 Screenshot salvo")
        
        # 4. Verificar resultado
        conteudo = page.content().lower()
        
        if "não encontrado" in conteudo or "não foi possível" in conteudo or "não existem" in conteudo:
            print("\n   ❌ Processo não encontrado no TJSP")
            print(f"   💡 O número {numero_processo} pode não existir no portal do TJSP")
            print(f"   💡 Ou o processo pode ser de outro tribunal")
        else:
            print("\n   ✅ PROCESSO ENCONTRADO!")
            
            # Buscar ofício
            print("\n4️⃣ Buscando ofício requisitório...")
            
            links = page.locator("a").all()
            print(f"   Total de links: {len(links)}")
            
            # Listar todos os links para debug
            print("\n   📋 Links encontrados:")
            for i, link in enumerate(links[:20]):  # Mostrar apenas os 20 primeiros
                try:
                    texto = link.inner_text().strip()
                    if texto:
                        print(f"   {i+1}. {texto[:50]}")
                except:
                    pass
            
            oficio_encontrado = False
            for link in links:
                try:
                    texto = link.inner_text().lower()
                    if "ofício" in texto or "requisitório" in texto or "requisitorio" in texto or "oficio" in texto:
                        print(f"\n   🎉 OFÍCIO ENCONTRADO!")
                        print(f"   Texto: {link.inner_text()}")
                        oficio_encontrado = True
                        
                        # Tentar baixar
                        try:
                            with page.expect_download(timeout=10000) as download_info:
                                link.click()
                            
                            download = download_info.value
                            filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                            filepath = Path("data/oficios") / filename
                            download.save_as(filepath)
                            
                            print(f"   ✅ OFÍCIO BAIXADO: {filepath}")
                            break
                        except:
                            print(f"   ⚠️  Link não iniciou download")
                except:
                    pass
            
            if not oficio_encontrado:
                print("\n   ⚠️  Ofício não encontrado na página")
                print("   💡 O processo existe, mas o ofício pode não estar disponível online")
        
        # Salvar HTML
        with open("data/oficios/tjsp_busca_real.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"\n   💾 HTML salvo: tjsp_busca_real.html")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Pressione ENTER para fechar...")
    input()
    browser.close()

db.close()
