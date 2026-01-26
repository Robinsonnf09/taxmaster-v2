"""
Script DEFINITIVO - Cadastro no PUSH com interface REAL identificada
URL correta: /pje/Push/listView.seam
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

class CadastroPushDefinitivo:
    
    def __init__(self):
        self.driver = None
        self.sucessos = []
        self.falhas = []
    
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
        
        url = "https://pje1g.trf1.jus.br/pje/login.seam"
        print(f"\n🔐 Acessando: {url}")
        self.driver.get(url)
        
        input("\n>>> Faça login com certificado e pressione ENTER <<<\n")
        
        if "login" not in self.driver.current_url.lower():
            print("✅ Login OK!")
            return True
        print("❌ Login falhou!")
        return False
    
    def acessar_push(self):
        print("\n🔔 Acessando PJe PUSH...")
        
        # URL CORRETA identificada!
        url_push = "https://pje1g.trf1.jus.br/pje/Push/listView.seam"
        
        self.driver.get(url_push)
        time.sleep(3)
        
        # Verificar se chegou na página correta
        if "push" in self.driver.current_url.lower():
            print("✅ PUSH acessado com sucesso!")
            
            # Verificar se vê o título
            try:
                titulo = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Inclusão de processos')]")
                print(f"✅ Página correta: {titulo.text}")
                return True
            except:
                print("⚠️ Na URL do Push mas título não encontrado")
                return True
        
        print("❌ Não conseguiu acessar Push")
        return False
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Procurar campo de número (tentar várias estratégias)
            campo = None
            
            # Estratégia 1: Por label
            try:
                campo = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[ancestor::*[contains(., 'Número do Processo')]]")
                ))
            except:
                pass
            
            # Estratégia 2: Por placeholder
            if not campo:
                try:
                    campo = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//input[contains(@placeholder, '_______')]")
                    ))
                except:
                    pass
            
            # Estratégia 3: Input type=text primeiro da página
            if not campo:
                try:
                    campos = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                    if campos:
                        campo = campos[0]
                except:
                    pass
            
            if not campo:
                print("❌ Campo de número não encontrado!")
                self.falhas.append(numero)
                return False
            
            # Preencher número
            campo.clear()
            campo.send_keys(numero)
            time.sleep(1)
            
            # Procurar botão INCLUIR
            btn = None
            try:
                btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'INCLUIR')] | //input[@value='INCLUIR']")
            except:
                try:
                    btn = self.driver.find_element(By.XPATH, "//*[contains(text(), 'INCLUIR') and (self::button or self::input)]")
                except:
                    pass
            
            if not btn:
                print("❌ Botão INCLUIR não encontrado!")
                self.falhas.append(numero)
                return False
            
            # Clicar
            btn.click()
            time.sleep(3)
            
            # Verificar sucesso
            page_source = self.driver.page_source.lower()
            
            if "sucesso" in page_source or "incluído" in page_source or "cadastrado" in page_source:
                print(f"   ✅ {numero} cadastrado com sucesso!")
                self.sucessos.append(numero)
                return True
            elif "já cadastrado" in page_source or "já existe" in page_source:
                print(f"   ⚠️  {numero} já estava cadastrado")
                self.sucessos.append(numero)
                return True
            else:
                print(f"   ⚠️  Status desconhecido para {numero}")
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
        
        total = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                total += 1
                numero = str(row[0]).strip()
                self.cadastrar_processo(numero)
                time.sleep(2)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   Total: {total}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        
        if self.sucessos:
            print("\n✅ Cadastrados:")
            for p in self.sucessos:
                print(f"   - {p}")
        
        if self.falhas:
            print("\n❌ Falhas:")
            for p in self.falhas:
                print(f"   - {p}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 CADASTRO NO PUSH - VERSÃO DEFINITIVA")
    print("="*70)
    
    cadastro = CadastroPushDefinitivo()
    
    try:
        input("\n⚠️  Token conectado? ENTER para começar...\n")
        
        if cadastro.login():
            if cadastro.acessar_push():
                
                print("\n💡 MODO:")
                print("   1. Planilha em lote")
                print("   2. Processo individual")
                
                modo = input("\nEscolha: ").strip()
                
                if modo == "1":
                    arq = input("\nArquivo: ").strip().strip('"').strip("'")
                    cadastro.processar_planilha(arq)
                
                elif modo == "2":
                    num = input("\nNúmero: ").strip()
                    cadastro.cadastrar_processo(num)
        
        input("\n\nENTER para fechar...")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        cadastro.fechar()
    
    print("\n✅ FIM!")
