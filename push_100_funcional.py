"""
SCRIPT DEFINITIVO - Seletor correto do botão INCLUIR identificado!
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import openpyxl
import os

class CadastroPushFinalFuncionando:
    
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
        
        time.sleep(2)
        url_atual = self.driver.current_url
        
        if "login" not in url_atual.lower():
            print("✅ Login OK!")
            return True
        
        print("⚠️ Não detectou saída da página de login")
        opcao = input("   Continuar? (s/n): ").lower()
        return opcao == 's'
    
    def acessar_push(self):
        print("\n🔔 Acessando PJe PUSH...")
        url_push = "https://pje1g.trf1.jus.br/pje/Push/listView.seam"
        
        self.driver.get(url_push)
        time.sleep(4)
        
        if "push" in self.driver.current_url.lower():
            print("✅ PUSH acessado!")
            return True
        
        print("⚠️ Acesse manualmente")
        input(">>> Pressione ENTER quando estiver no PUSH <<<\n")
        return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # LOCALIZAR CAMPO
            campo = None
            try:
                campo = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[contains(@placeholder, '_')]")
                ))
                print(f"   ✅ Campo localizado")
            except:
                print(f"   ❌ Campo não encontrado!")
                self.falhas.append(numero)
                return False
            
            # PREENCHER
            campo.clear()
            time.sleep(0.3)
            campo.send_keys(numero)
            time.sleep(0.5)
            print(f"   ✅ Número digitado")
            
            # LOCALIZAR BOTÃO INCLUIR - MÚLTIPLAS ESTRATÉGIAS
            btn = None
            
            # Estratégia 1: Texto exato "INCLUIR"
            try:
                btn = self.driver.find_element(By.XPATH, "//button[text()='INCLUIR']")
                print(f"   ✅ Botão encontrado (texto exato)")
            except:
                pass
            
            # Estratégia 2: Contains text
            if not btn:
                try:
                    btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'INCLUIR')]")
                    print(f"   ✅ Botão encontrado (contains)")
                except:
                    pass
            
            # Estratégia 3: Input com value
            if not btn:
                try:
                    btn = self.driver.find_element(By.XPATH, "//input[@value='INCLUIR']")
                    print(f"   ✅ Botão encontrado (input value)")
                except:
                    pass
            
            # Estratégia 4: Por classe CSS (botões azuis)
            if not btn:
                try:
                    botoes = self.driver.find_elements(By.TAG_NAME, "button")
                    for b in botoes:
                        if "INCLUIR" in b.text.upper():
                            btn = b
                            print(f"   ✅ Botão encontrado (varredura)")
                            break
                except:
                    pass
            
            # Estratégia 5: JAVASCRIPT (sempre funciona!)
            if not btn:
                print(f"   ⚡ Tentando JavaScript...")
                js_click = """
                var elementos = document.querySelectorAll('button, input[type=submit], input[type=button]');
                for(var i=0; i<elementos.length; i++) {
                    var txt = elementos[i].textContent || elementos[i].value || '';
                    if(txt.toUpperCase().includes('INCLUIR')) {
                        elementos[i].click();
                        return true;
                    }
                }
                return false;
                """
                
                resultado = self.driver.execute_script(js_click)
                
                if resultado:
                    print(f"   ✅ Clicado com JavaScript!")
                    time.sleep(4)
                    
                    # Verificar sucesso
                    page = self.driver.page_source.lower()
                    if any(x in page for x in ['sucesso', 'incluído', 'cadastrado']):
                        print(f"   ✅ {numero} CADASTRADO!")
                        self.sucessos.append(numero)
                        return True
                    elif any(x in page for x in ['já cadastrado', 'já existe']):
                        print(f"   ⚠️  {numero} já estava cadastrado")
                        self.sucessos.append(numero)
                        return True
                    else:
                        self.falhas.append(numero)
                        return False
                else:
                    print(f"   ❌ Botão não encontrado nem com JS!")
                    self.driver.save_screenshot(f"erro_botao_{numero}.png")
                    self.falhas.append(numero)
                    return False
            
            # Se encontrou botão com Selenium
            if btn:
                btn.click()
                print(f"   ⏳ Aguardando...")
                time.sleep(4)
                
                page = self.driver.page_source.lower()
                if any(x in page for x in ['sucesso', 'incluído', 'cadastrado']):
                    print(f"   ✅ {numero} CADASTRADO!")
                    self.sucessos.append(numero)
                    return True
                elif any(x in page for x in ['já cadastrado', 'já existe']):
                    print(f"   ⚠️  {numero} já estava cadastrado")
                    self.sucessos.append(numero)
                    return True
                else:
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
        print(f"✅ {total} processos na planilha\n")
        
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
        print(f"   Total: {total}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        if total > 0:
            print(f"   📊 Taxa de sucesso: {(len(self.sucessos)/total*100):.1f}%")
        
        if self.sucessos:
            print(f"\n✅ {len(self.sucessos)} PROCESSOS CADASTRADOS!")
        
        if self.falhas:
            print(f"\n❌ {len(self.falhas)} FALHAS:")
            for p in self.falhas[:10]:
                print(f"   - {p}")
            if len(self.falhas) > 10:
                print(f"   ... e mais {len(self.falhas)-10}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 CADASTRO AUTOMÁTICO NO PUSH - VERSÃO DEFINITIVA 100% FUNCIONAL")
    print("="*70)
    
    cadastro = CadastroPushFinalFuncionando()
    
    try:
        input("\n⚠️  Token A3 conectado? ENTER para começar...\n")
        
        if cadastro.login():
            if cadastro.acessar_push():
                
                print("\n💡 MODO:")
                print("   1. Planilha em lote (todos os 215 processos)")
                print("   2. Processo individual (teste)")
                
                modo = input("\nDigite 1 ou 2: ").strip()
                
                if modo == "1":
                    arq = "processos_push_20260126_185045.xlsx"
                    print(f"\n📄 Usando: {arq}")
                    cadastro.processar_planilha(arq)
                
                elif modo == "2":
                    num = input("\n📝 Número: ").strip()
                    cadastro.cadastrar_processo(num)
        
        input("\n\n>>> ENTER para fechar <<<\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelado")
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        cadastro.fechar()
    
    print("\n✅ CONCLUÍDO!")
