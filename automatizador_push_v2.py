"""
Automatizador PUSH - VERSÃO CORRIGIDA
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

class AutomatizadorPushCorrigido:
    
    def __init__(self):
        self.driver = None
        self.processos_ok = []
        self.processos_erro = []
    
    def iniciar(self):
        print("\n🌐 Iniciando navegador...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Navegador iniciado!")
    
    def login_pje(self, url):
        if not self.driver:
            self.iniciar()
        
        print(f"\n🔐 Acessando: {url}")
        self.driver.get(url)
        
        print("\n⚠️  FAÇA LOGIN:")
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione seu certificado")
        print("   3. Digite o PIN")
        
        input("\n>>> ENTER após login <<<")
        
        if "login" not in self.driver.current_url.lower():
            print("✅ Login OK!")
            return True
        return False
    
    def acessar_push(self):
        print("\n🔔 Acessando PUSH...")
        
        base = self.driver.current_url.split("/pje/")[0]
        url_push = f"{base}/pje/Processo/CadastroPush/listView.seam"
        
        self.driver.get(url_push)
        time.sleep(3)
        
        if "push" in self.driver.current_url.lower():
            print("✅ PUSH acessado!")
            return True
        
        print("⚠️  Acesse manualmente o PUSH")
        input(">>> ENTER quando estiver no PUSH <<<")
        return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Procurar campo de número
            campo = wait.until(
                EC.presence_of_element_located((By.ID, "numeroProcesso"))
            )
            campo.clear()
            campo.send_keys(numero)
            
            # Botão cadastrar
            btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cadastrar')] | //button[contains(text(), 'Salvar')]")
            btn.click()
            
            time.sleep(2)
            
            print(f"   ✅ {numero} cadastrado!")
            self.processos_ok.append(numero)
            return True
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            self.processos_erro.append(numero)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Processando: {arquivo}")
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado!")
            return
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            numero = row[0]
            if numero:
                self.cadastrar_processo(str(numero))
                time.sleep(1)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO:")
        print(f"   ✅ Sucesso: {len(self.processos_ok)}")
        print(f"   ❌ Erros: {len(self.processos_erro)}")
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 CADASTRO AUTOMÁTICO NO PUSH DO PJE")
    print("="*70)
    
    auto = AutomatizadorPushCorrigido()
    
    try:
        input("\n⚠️  Token conectado? ENTER para continuar...")
        
        # Login
        url = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        if auto.login_pje(url):
            if auto.acessar_push():
                
                print("\n💡 MODO:")
                print("   1. Planilha em lote")
                print("   2. Processo individual")
                
                modo = input("\nEscolha: ").strip()
                
                if modo == "1":
                    arq = input("\nCaminho da planilha: ").strip()
                    auto.processar_planilha(arq)
                
                elif modo == "2":
                    num = input("\nNúmero do processo: ").strip()
                    auto.cadastrar_processo(num)
                
                else:
                    print("❌ Opção inválida!")
        
        input("\n\nENTER para fechar...")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        auto.fechar()
    
    print("\n✅ FIM!")
