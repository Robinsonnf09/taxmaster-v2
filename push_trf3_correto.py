"""
SCRIPT PARA TRF3 - URL CORRETA
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

class CadastroPushTRF3:
    
    def __init__(self):
        self.driver = None
        self.sucessos = []
        self.falhas = []
        self.url_base = "https://pje.trf3.jus.br"  # TRF3!
    
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
        print("   3. Digite o PIN do token")
        print("   4. AGUARDE entrar no sistema")
        print("="*70)
        
        input("\n>>> ENTER após login completo <<<\n")
        
        time.sleep(2)
        url_atual = self.driver.current_url
        print(f"🔍 URL atual: {url_atual}")
        
        if "login" not in url_atual.lower():
            print("✅ Login OK no TRF3!")
            return True
        
        opcao = input("   Continuar? (s/n): ").lower()
        return opcao == 's'
    
    def acessar_push(self):
        print("\n🔔 Acessando PUSH do TRF3...")
        
        # Tentar URLs possíveis do TRF3
        urls_push = [
            f"{self.url_base}/pje/Push/listView.seam",
            f"{self.url_base}/pje/Processo/CadastroPush/listView.seam",
            f"{self.url_base}/primeirograu/Push/listView.seam"
        ]
        
        for url in urls_push:
            print(f"   Tentando: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            if "push" in self.driver.current_url.lower():
                print(f"✅ PUSH acessado: {self.driver.current_url}")
                return True
        
        print("\n⚠️ Não encontrei automaticamente. Navegue manualmente:")
        print("   Menu > Configurações > Serviço Push")
        input("\n>>> ENTER quando estiver no PUSH <<<\n")
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
                self.driver.save_screenshot(f"erro_campo_{numero}.png")
                self.falhas.append(numero)
                return False
            
            # Preencher
            campo.clear()
            time.sleep(0.3)
            campo.send_keys(numero)
            time.sleep(0.5)
            print(f"   ✅ Número digitado")
            
            # Clicar com JavaScript (mais confiável)
            print(f"   ⚡ Clicando no botão...")
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
                self.driver.save_screenshot(f"erro_botao_{numero}.png")
                self.falhas.append(numero)
                return False
            
            print(f"   ⏳ Aguardando resposta...")
            time.sleep(4)
            
            # Verificar resultado
            page = self.driver.page_source.lower()
            
            if any(x in page for x in ['sucesso', 'incluído', 'cadastrado', 'adicionado']):
                print(f"   ✅ {numero} CADASTRADO!")
                self.sucessos.append(numero)
                return True
            
            elif any(x in page for x in ['já cadastrado', 'já existe', 'duplicado']):
                print(f"   ⚠️  {numero} já estava cadastrado")
                self.sucessos.append(numero)
                return True
            
            elif any(x in page for x in ['não encontrado', 'inexistente', 'inválido']):
                print(f"   ❌ {numero} NÃO ENCONTRADO no sistema!")
                self.falhas.append(numero)
                return False
            
            else:
                print(f"   ⚠️  Status desconhecido")
                self.driver.save_screenshot(f"status_{numero}.png")
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
        print(f"✅ {total} processos na planilha")
        print(f"🏛️  Todos do TRF3 (.4.03.)\n")
        
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
        print(f"   🏛️  Tribunal: TRF3")
        print(f"   📋 Total: {total}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        if total > 0:
            print(f"   📊 Taxa: {(len(self.sucessos)/total*100):.1f}%")
        
        if self.sucessos:
            print(f"\n✅ {len(self.sucessos)} CADASTRADOS!")
        
        if self.falhas:
            print(f"\n❌ {len(self.falhas)} FALHAS:")
            for p in self.falhas[:20]:
                print(f"   - {p}")
            if len(self.falhas) > 20:
                print(f"   ... e mais {len(self.falhas)-20}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 CADASTRO NO PUSH - TRF3 (TRIBUNAL CORRETO!)")
    print("="*70)
    
    cadastro = CadastroPushTRF3()
    
    try:
        print("\n⚠️  IMPORTANTE:")
        print("   Seus processos são do TRF3 (.4.03.)")
        print("   O script vai acessar: pje.trf3.jus.br")
        
        input("\nToken A3 conectado? ENTER...\n")
        
        if cadastro.login():
            if cadastro.acessar_push():
                
                print("\n💡 MODO:")
                print("   1. Planilha completa (215 processos)")
                print("   2. Teste individual")
                
                modo = input("\nDigite 1 ou 2: ").strip()
                
                if modo == "1":
                    arq = "processos_push_20260126_185045.xlsx"
                    cadastro.processar_planilha(arq)
                
                elif modo == "2":
                    num = input("\nNúmero: ").strip()
                    cadastro.cadastrar_processo(num)
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        cadastro.fechar()
    
    print("\n✅ FIM!")
