"""
TRF3 com URL CORRETA: pje1g-jus.trf3.jus.br
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
import os

class PushTRF3Final:
    
    def __init__(self):
        self.driver = None
        self.sucessos = []
        self.falhas = []
        # URL CORRETA DO TRF3!
        self.url_base = "https://pje1g-jus.trf3.jus.br"
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def login(self):
        if not self.driver:
            self.iniciar()
        
        url_login = f"{self.url_base}/pje/login.seam"
        print(f"\n🔐 Acessando TRF3: {url_login}")
        self.driver.get(url_login)
        
        print("\n" + "="*70)
        print("⚠️  FAÇA LOGIN NO TRF3:")
        print("="*70)
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN")
        print("   4. Aguarde entrar")
        print("="*70)
        
        input("\n>>> ENTER após login <<<\n")
        
        time.sleep(2)
        url_atual = self.driver.current_url
        
        if "login" not in url_atual.lower():
            print("✅ Login OK!")
            return True
        
        opcao = input("   Continuar? (s/n): ").lower()
        return opcao == 's'
    
    def acessar_push(self):
        print("\n🔔 Acessando PUSH do TRF3...")
        url_push = f"{self.url_base}/pje/Push/listView.seam"
        
        print(f"   URL: {url_push}")
        self.driver.get(url_push)
        time.sleep(4)
        
        if "push" in self.driver.current_url.lower():
            print("✅ PUSH acessado!")
            return True
        
        print("⚠️ Navegue manualmente até o PUSH")
        input(">>> ENTER quando estiver no PUSH <<<\n")
        return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Localizar campo
            campo = None
            try:
                campo = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[contains(@placeholder, '_') or @type='text']")
                ))
                print(f"   ✅ Campo localizado")
            except:
                print(f"   ❌ Campo não encontrado!")
                self.falhas.append(numero)
                return False
            
            # Preencher
            campo.clear()
            time.sleep(0.3)
            campo.send_keys(numero)
            time.sleep(0.5)
            print(f"   ✅ Número digitado")
            
            # Clicar com JavaScript
            print(f"   ⚡ Clicando...")
            js_click = """
            var elementos = document.querySelectorAll('button, input[type=submit], input[type=button]');
            for(var i=0; i<elementos.length; i++) {
                var txt = elementos[i].textContent || elementos[i].value || '';
                if(txt.toUpperCase().includes('INCLUIR') || txt.toUpperCase().includes('CADASTRAR')) {
                    elementos[i].click();
                    return true;
                }
            }
            return false;
            """
            
            resultado = self.driver.execute_script(js_click)
            
            if not resultado:
                print(f"   ❌ Botão não encontrado!")
                self.falhas.append(numero)
                return False
            
            print(f"   ⏳ Aguardando...")
            time.sleep(4)
            
            # Verificar resultado
            page = self.driver.page_source.lower()
            
            if any(x in page for x in ['sucesso', 'incluído', 'cadastrado']):
                print(f"   ✅ {numero} CADASTRADO!")
                self.sucessos.append(numero)
                return True
            
            elif any(x in page for x in ['já cadastrado', 'já existe']):
                print(f"   ⚠️  {numero} já estava cadastrado")
                self.sucessos.append(numero)
                return True
            
            elif any(x in page for x in ['não encontrado', 'inexistente']):
                print(f"   ❌ {numero} NÃO ENCONTRADO!")
                self.falhas.append(numero)
                return False
            
            else:
                print(f"   ⚠️  Status desconhecido")
                self.falhas.append(numero)
                return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            self.falhas.append(numero)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Processando: {arquivo}")
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado!")
            return
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                processos.append(str(row[0]).strip())
        
        total = len(processos)
        print(f"✅ {total} processos\n")
        
        for idx, numero in enumerate(processos, 1):
            print(f"\n{'='*70}")
            print(f"Processo {idx}/{total}")
            print(f"{'='*70}")
            
            self.cadastrar_processo(numero)
            
            if idx < total:
                time.sleep(2)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   🏛️  TRF3")
        print(f"   📋 Total: {total}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        if total > 0:
            print(f"   📊 Taxa: {(len(self.sucessos)/total*100):.1f}%")
        
        if self.falhas:
            print(f"\n❌ FALHAS:")
            for p in self.falhas[:20]:
                print(f"   - {p}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 PUSH TRF3 - URL CORRETA!")
    print("="*70)
    
    cadastro = PushTRF3Final()
    
    try:
        input("\nToken conectado? ENTER...\n")
        
        if cadastro.login():
            if cadastro.acessar_push():
                
                print("\n💡 MODO:")
                print("   1. Planilha (215 processos)")
                print("   2. Teste")
                
                modo = input("\nDigite: ").strip()
                
                if modo == "1":
                    cadastro.processar_planilha("processos_push_20260126_185045.xlsx")
                
                elif modo == "2":
                    num = input("\nNúmero: ").strip()
                    cadastro.cadastrar_processo(num)
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        cadastro.fechar()
    
    print("\n✅ FIM!")
