"""
PUSH TJSP - COM LOGIN MANUAL
Aguarda login, depois acessa formulário de cadastro
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import openpyxl

class PushTJSPComLogin:
    
    def __init__(self):
        self.driver = None
        self.url_push = "https://esaj.tjsp.jus.br/push/index.do"
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def fazer_login(self):
        print(f"\n🔐 Acessando PUSH TJSP...")
        self.driver.get(self.url_push)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("⚠️  FAÇA LOGIN NO SISTEMA:")
        print("="*70)
        print("   1. Use seu certificado digital OU")
        print("   2. Use login/senha")
        print("   3. AGUARDE até estar LOGADO e ver a área interna")
        print("="*70)
        
        input("\n>>> ENTER após fazer login completo &lt;&lt;&lt;\n")
        
        time.sleep(2)
        print("✅ Login confirmado!")
        return True
    
    def acessar_cadastro(self):
        print("\n📋 Navegando para área de cadastro...")
        
        # Tentar acessar diretamente a URL de cadastro
        url_cadastro = "https://esaj.tjsp.jus.br/push/abrirCadastro.do"
        
        print(f"   Tentando: {url_cadastro}")
        self.driver.get(url_cadastro)
        time.sleep(3)
        
        print("\n⚠️  Você está vendo o formulário de cadastro de processos?")
        opcao = input("   (s/n): ").lower()
        
        if opcao == 's':
            print("✅ Formulário acessado!")
            
            # Debug: ver campos disponíveis
            print("\n🔍 Analisando campos do formulário...")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            print(f"\n📝 Campos encontrados:")
            for idx, inp in enumerate(inputs, 1):
                if inp.is_displayed():
                    tipo = inp.get_attribute("type")
                    nome = inp.get_attribute("name")
                    id_campo = inp.get_attribute("id")
                    placeholder = inp.get_attribute("placeholder")
                    
                    print(f"   {idx}. Tipo: {tipo} | Name: {nome} | ID: {id_campo} | Placeholder: {placeholder}")
            
            return True
        else:
            print("\n💡 Navegue manualmente até o formulário de cadastro")
            input("   >>> ENTER quando estiver no formulário &lt;&lt;&lt;\n")
            return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            # Procurar campo de número
            campo = None
            
            # Estratégia 1: Por name/id comum
            seletores = [
                "//input[@name='numeroProcesso']",
                "//input[@id='numeroProcesso']",
                "//input[@name='processo']",
                "//input[@id='processo']",
                "//input[@type='text' and @maxlength='20']",
                "//input[@type='text'][1]"
            ]
            
            for seletor in seletores:
                try:
                    campo = self.driver.find_element(By.XPATH, seletor)
                    if campo.is_displayed():
                        print(f"   ✅ Campo encontrado")
                        break
                except:
                    continue
            
            if not campo:
                print(f"   ⚠️  Campo não encontrado")
                print(f"   💡 Digite manualmente: {numero}")
                input(f"   >>> ENTER após digitar &lt;&lt;&lt;\n")
                return None
            
            # Preencher
            campo.clear()
            campo.send_keys(numero)
            time.sleep(0.5)
            print(f"   ✅ Número digitado")
            
            # Procurar botão incluir
            btn = None
            botoes = [
                "//button[contains(text(), 'Incluir')]",
                "//input[@value='Incluir']",
                "//button[@id='btnIncluir']",
                "//input[@id='btnIncluir']"
            ]
            
            for xpath in botoes:
                try:
                    btn = self.driver.find_element(By.XPATH, xpath)
                    if btn.is_displayed():
                        print(f"   ✅ Botão encontrado")
                        break
                except:
                    continue
            
            if not btn:
                print(f"   ⚠️  Botão não encontrado")
                input(f"   >>> Clique em INCLUIR &lt;&lt;&lt;\n")
            else:
                btn.click()
                time.sleep(3)
            
            # Verificar resultado
            page = self.driver.page_source.lower()
            
            if 'sucesso' in page or 'incluído' in page:
                print(f"   ✅ CADASTRADO!")
                return True
            elif 'já cadastrado' in page:
                print(f"   ⚠️  Já estava cadastrado")
                return True
            else:
                print(f"   ⚠️  Status desconhecido")
                opcao = input(f"   >>> Cadastrou? (s/n): ").lower()
                return opcao == 's'
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Processando: {arquivo}")
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                # Filtrar apenas processos do TJSP (8.26)
                if '.8.26.' in num:
                    processos.append(num)
        
        total = len(processos)
        print(f"✅ {total} processos do TJSP\n")
        
        sucessos = []
        falhas = []
        
        for idx, numero in enumerate(processos, 1):
            print(f"\n{'='*70}")
            print(f"Processo {idx}/{total}")
            print(f"{'='*70}")
            
            resultado = self.cadastrar_processo(numero)
            
            if resultado:
                sucessos.append(numero)
            else:
                falhas.append(numero)
            
            if idx < total:
                time.sleep(2)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   Total: {total}")
        print(f"   ✅ Sucessos: {len(sucessos)}")
        print(f"   ❌ Falhas: {len(falhas)}")
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 PUSH TJSP - COM LOGIN")
    print("="*70)
    
    push = PushTJSPComLogin()
    
    try:
        input("\nENTER para começar...\n")
        
        push.iniciar()
        
        if push.fazer_login():
            if push.acessar_cadastro():
                
                print("\n💡 MODO:")
                print("   1. Teste (1 processo)")
                print("   2. Planilha completa")
                
                modo = input("\nDigite: ").strip()
                
                if modo == "1":
                    num = input("\nNúmero: ").strip()
                    push.cadastrar_processo(num)
                elif modo == "2":
                    push.processar_planilha("processos_push_20260126_185045.xlsx")
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        push.fechar()
    
    print("\n✅ FIM!")
