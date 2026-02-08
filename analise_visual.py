"""
ANÁLISE VISUAL DETALHADA - CAPTURA INFORMAÇÕES DA PÁGINA
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

load_dotenv()

print("\n🔍 ANÁLISE VISUAL DA PÁGINA DE REQUISITÓRIOS")
print("="*70)

# Iniciar Edge
options = Options()
options.add_argument('--start-maximized')
driver = webdriver.Edge(options=options)

# Login
driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
time.sleep(3)

print("\n🔐 Selecione certificado...")
time.sleep(15)

# Buscar processo
numero = "0051675-54.2023.8.26.0500"

driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
time.sleep(2)

try:
    radio = driver.find_element(By.ID, "radioNumeroAntigo")
    radio.click()
    time.sleep(0.5)
except:
    pass

campo = driver.find_element(By.ID, "nuProcessoAntigoFormatado")
campo.clear()
campo.send_keys(numero)
campo.send_keys(Keys.RETURN)

time.sleep(3)

url_atual = driver.current_url
codigo = url_atual.split("processo.codigo=")[1].split("&")[0]

print(f"\n✅ Processo encontrado: {codigo}")

# Acessar requisitórios
url_req = f"https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo={codigo}&processo.foro=500&processo.numero={numero}&consultaDeRequisitorios=true"
driver.get(url_req)
time.sleep(3)

# Tirar screenshot
driver.save_screenshot("ANALISE_PAGINA_COMPLETA.png")
print(f"📸 Screenshot completo: ANALISE_PAGINA_COMPLETA.png")

# Extrair TODAS as informações sobre os links
script_analise = """
let analise = {
    totalLinks: 0,
    linksOficio: [],
    estrutura: ''
};

// Contar todos os links
analise.totalLinks = document.querySelectorAll('a').length;

// Analisar links de ofício detalhadamente
document.querySelectorAll('a').forEach((a, idx) => {
    let texto = a.textContent.toLowerCase();
    
    if (texto.includes('ofício') || texto.includes('requisitório') || 
        texto.includes('depre') || texto.includes('or ')) {
        
        let styles = window.getComputedStyle(a);
        
        analise.linksOficio.push({
            index: idx,
            texto: a.textContent.trim(),
            href: a.href,
            target: a.getAttribute('target'),
            onclick: a.getAttribute('onclick'),
            class: a.className,
            id: a.id,
            visivel: (styles.display !== 'none' && styles.visibility !== 'hidden'),
            posicao: {
                x: a.offsetLeft,
                y: a.offsetTop,
                width: a.offsetWidth,
                height: a.offsetHeight
            }
        });
    }
});

// Capturar estrutura HTML da seção de requisitórios
let secaoReq = document.querySelector('#requisitorios') || 
               document.querySelector('.requisitorios') ||
               document.querySelector('[id*="requisitorio"]') ||
               document.querySelector('[class*="requisitorio"]');

if (secaoReq) {
    analise.estrutura = secaoReq.innerHTML.substring(0, 2000);
}

return analise;
"""

resultado = driver.execute_script(script_analise)

print(f"\n📊 ANÁLISE COMPLETA:")
print(f"   Total de links na página: {resultado['totalLinks']}")
print(f"   Links de ofício encontrados: {len(resultado['linksOficio'])}")

print(f"\n📋 PRIMEIROS 5 LINKS DE OFÍCIO:")
for i, link in enumerate(resultado['linksOficio'][:5], 1):
    print(f"\n   [{i}] {link['texto'][:60]}")
    print(f"       URL: {link['href'][:80]}")
    print(f"       OnClick: {link['onclick']}")
    print(f"       Target: {link['target']}")
    print(f"       Visível: {link['visivel']}")
    print(f"       Posição: x={link['posicao']['x']}, y={link['posicao']['y']}")
    print(f"       Tamanho: {link['posicao']['width']}x{link['posicao']['height']}")

# Salvar estrutura HTML
if resultado['estrutura']:
    with open("ESTRUTURA_HTML_REQUISITORIOS.html", "w", encoding="utf-8") as f:
        f.write(resultado['estrutura'])
    print(f"\n📄 Estrutura HTML salva: ESTRUTURA_HTML_REQUISITORIOS.html")

# Salvar análise completa
with open("ANALISE_LINKS_COMPLETA.txt", "w", encoding="utf-8") as f:
    f.write("ANÁLISE COMPLETA DOS LINKS\n")
    f.write("="*70 + "\n\n")
    
    for i, link in enumerate(resultado['linksOficio'], 1):
        f.write(f"[{i}] {link['texto']}\n")
        f.write(f"    URL: {link['href']}\n")
        f.write(f"    OnClick: {link['onclick']}\n")
        f.write(f"    Target: {link['target']}\n")
        f.write(f"    Class: {link['class']}\n")
        f.write(f"    ID: {link['id']}\n")
        f.write(f"    Visível: {link['visivel']}\n")
        f.write(f"    Posição: x={link['posicao']['x']}, y={link['posicao']['y']}\n")
        f.write("\n")

print(f"📄 Análise salva: ANALISE_LINKS_COMPLETA.txt")

print(f"\n{'='*70}")
print(f"✅ ANÁLISE CONCLUÍDA!")
print(f"{'='*70}")
print(f"\nArquivos gerados:")
print(f"   📸 ANALISE_PAGINA_COMPLETA.png")
print(f"   📄 ESTRUTURA_HTML_REQUISITORIOS.html")
print(f"   📄 ANALISE_LINKS_COMPLETA.txt")
print(f"\n💡 Abra os arquivos para entender a estrutura real da página")

input("\n\n>>> ENTER para fechar <<<\n")
driver.quit()
