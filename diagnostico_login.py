"""
DIAGNÓSTICO DE LOGIN TJSP - Versão Debug
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os

# Carregar .env
load_dotenv()

print("="*70)
print("🔍 DIAGNÓSTICO DE LOGIN TJSP")
print("="*70)

usuario = os.getenv("TJSP_USUARIO")
senha = os.getenv("TJSP_SENHA")

print(f"\n📋 Credenciais do .env:")
print(f"   Usuário: {usuario}")
print(f"   Senha: {'*' * len(senha) if senha else 'NÃO CONFIGURADA'}")

# Iniciar Chrome
print(f"\n🌐 Iniciando Chrome...")
chrome_options = Options()
chrome_options.add_argument('--start-maximized')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("✅ Chrome iniciado!")

# Acessar página de login
print(f"\n🔐 Acessando página de login do TJSP...")
driver.get("https://esaj.tjsp.jus.br/sajcas/login")
time.sleep(4)

print(f"✅ Página carregada!")
print(f"📍 URL atual: {driver.current_url}")

# Tirar screenshot
screenshot = "diagnostico_login_tjsp.png"
driver.save_screenshot(screenshot)
print(f"\n📸 Screenshot salvo: {screenshot}")

# Buscar campos na página
print(f"\n🔍 Procurando elementos de login na página...")

elementos_encontrados = {}

# Testar diferentes IDs possíveis
ids_testar = {
    "Campo Usuário": ["usernameForm", "username", "login", "cpf", "usuario"],
    "Campo Senha": ["passwordForm", "password", "senha", "pwd"],
    "Botão Entrar": ["pbEntrar", "btnEntrar", "submit", "entrar"]
}

for tipo, ids in ids_testar.items():
    for id_elem in ids:
        try:
            elem = driver.find_element(By.ID, id_elem)
            elementos_encontrados[tipo] = id_elem
            print(f"   ✅ {tipo}: ID = '{id_elem}'")
            break
        except:
            continue
    
    if tipo not in elementos_encontrados:
        print(f"   ❌ {tipo}: Nenhum ID encontrado")

# Salvar HTML da página
html = driver.page_source
with open("diagnostico_login_tjsp.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n📄 HTML da página salvo: diagnostico_login_tjsp.html")

# Verificar se todos os elementos foram encontrados
print(f"\n{'='*70}")
if len(elementos_encontrados) == 3:
    print("✅ TODOS OS ELEMENTOS ENCONTRADOS!")
    print(f"\n🎯 Testando login agora...")
    
    try:
        campo_usuario = driver.find_element(By.ID, elementos_encontrados["Campo Usuário"])
        campo_senha = driver.find_element(By.ID, elementos_encontrados["Campo Senha"])
        botao = driver.find_element(By.ID, elementos_encontrados["Botão Entrar"])
        
        # Testar preenchimento
        campo_usuario.clear()
        campo_usuario.send_keys(usuario)
        print(f"   ✅ Usuário preenchido")
        
        campo_senha.clear()
        campo_senha.send_keys(senha)
        print(f"   ✅ Senha preenchida")
        
        print(f"\n⚠️  ATENÇÃO: Vou clicar no botão ENTRAR em 3 segundos...")
        time.sleep(3)
        
        botao.click()
        print(f"   ✅ Botão clicado")
        
        time.sleep(5)
        
        url_depois = driver.current_url
        print(f"\n📍 URL após login: {url_depois}")
        
        if "sajcas/login" not in url_depois:
            print(f"\n🎉 LOGIN BEM-SUCEDIDO!")
        else:
            print(f"\n❌ LOGIN FALHOU - Ainda na página de login")
            print(f"\n💡 Verifique se:")
            print(f"   1. As credenciais estão corretas")
            print(f"   2. Não há captcha na tela")
            print(f"   3. Não há mensagem de erro visível")
        
        # Tirar screenshot após tentativa
        driver.save_screenshot("diagnostico_apos_login.png")
        print(f"\n📸 Screenshot após login: diagnostico_apos_login.png")
        
    except Exception as e:
        print(f"\n❌ Erro ao tentar login: {str(e)}")

else:
    print("❌ ELEMENTOS FALTANDO - Página pode ter mudado")

print(f"\n{'='*70}")
print(f"🔍 DIAGNÓSTICO CONCLUÍDO")
print(f"{'='*70}")
print(f"\nArquivos gerados:")
print(f"   📸 diagnostico_login_tjsp.png")
print(f"   📸 diagnostico_apos_login.png")
print(f"   📄 diagnostico_login_tjsp.html")

input("\n\n>>> Pressione ENTER para fechar o navegador e verificar os arquivos <<<\n")
driver.quit()
print("\n✅ Navegador fechado")
