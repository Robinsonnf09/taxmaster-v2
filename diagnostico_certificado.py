"""
DIAGNÓSTICO DO LOGIN COM CERTIFICADO DIGITAL
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time

print("\n" + "="*70)
print("🔐 DIAGNÓSTICO DE AUTENTICAÇÃO COM CERTIFICADO DIGITAL")
print("="*70)

# Iniciar Edge
print("\n🔷 Iniciando Edge...")

options = Options()
options.add_argument('--start-maximized')
options.add_argument('--disable-popup-blocking')

# CRÍTICO: Habilitar certificados cliente
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-insecure-localhost')

# Configurações experimentais
prefs = {
    "profile.default_content_setting_values.automatic_downloads": 1
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Edge(options=options)

print("✅ Edge aberto!\n")

# Acessar e-SAJ
print("📍 ETAPA 1: Acessando e-SAJ...")
print(f"   URL: https://esaj.tjsp.jus.br/cpopg/open.do")

driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")

print(f"   ⏳ Aguardando 5 segundos...")
time.sleep(5)

url_atual = driver.current_url
print(f"\n✅ Página carregada!")
print(f"   URL atual: {url_atual}")
print(f"   Título: {driver.title}")

# Verificar se exige autenticação
print(f"\n📍 ETAPA 2: Verificando tipo de autenticação...")

# Procurar indicadores na página
script_verificacao = """
return {
    url: window.location.href,
    titulo: document.title,
    temLoginForm: document.querySelector('form[name*="login"]') !== null,
    temCertificadoBtn: document.querySelector('button, a').length > 0,
    bodyText: document.body.textContent.substring(0, 300)
};
"""

info = driver.execute_script(script_verificacao)

print(f"   URL: {info['url']}")
print(f"   Título: {info['titulo']}")
print(f"   Tem form de login: {info['temLoginForm']}")
print(f"   Texto da página (300 chars): {info['bodyText'][:100]}...")

# Screenshot
screenshot_nome = "diagnostico_login.png"
driver.save_screenshot(screenshot_nome)
print(f"\n📸 Screenshot salvo: {screenshot_nome}")

print(f"\n{'='*70}")
print(f"❓ VERIFICAÇÃO MANUAL NECESSÁRIA:")
print(f"{'='*70}")
print(f"\n1. O POPUP de certificado digital APARECEU?")
print(f"   ✅ SIM - Selecione o certificado agora")
print(f"   ❌ NÃO - O site pode não estar solicitando certificado")

print(f"\n2. Após selecionar o certificado:")
print(f"   • Você foi redirecionado para a página inicial do e-SAJ?")
print(f"   • Apareceu alguma mensagem de erro?")

print(f"\n⏳ Aguarde 30 segundos para selecionar o certificado...")
print(f"   (ou feche o Edge se não aparecer popup)")

time.sleep(30)

# Verificar URL após espera
url_final = driver.current_url
print(f"\n📍 URL após 30 segundos: {url_final}")

if "login" in url_final.lower():
    print(f"⚠️  AINDA NA PÁGINA DE LOGIN - Certificado não autenticou")
elif "cpopg" in url_final:
    print(f"✅ AUTENTICADO COM SUCESSO!")
else:
    print(f"❓ URL inesperada - verifique manualmente")

# Screenshot final
driver.save_screenshot("diagnostico_login_APOS.png")
print(f"📸 Screenshot após espera: diagnostico_login_APOS.png")

input("\n\n>>> Pressione ENTER para fechar <<<\n")
driver.quit()

print("\n✅ DIAGNÓSTICO CONCLUÍDO")
print(f"\nArquivos gerados:")
print(f"   📸 diagnostico_login.png")
print(f"   📸 diagnostico_login_APOS.png")
print(f"\n💡 Abra as imagens e me informe:")
print(f"   1. O popup de certificado apareceu?")
print(f"   2. Qual mensagem/tela aparece após selecionar?")
print(f"   3. A autenticação funcionou?")
