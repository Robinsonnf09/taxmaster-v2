"""
Versão com verificação de login ROBUSTA
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

class CadastroPushFinal:
    
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
        
        print("\n" + "="*70)
        print("INSTRUÇÕES DE LOGIN:")
        print("="*70)
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token")
        print("   4. AGUARDE entrar completamente no sistema")
        print("   5. Você verá a tela inicial do PJe")
        print("="*70)
        
        input("\n>>> Pressione ENTER SOMENTE APÓS VER A TELA INICIAL DO PJE <<<\n")
        
        # Aguardar um pouco
        time.sleep(2)
        
        # Verificar URL atual
        url_atual = self.driver.current_url
        print(f"\n🔍 URL atual: {url_atual}")
        
        # Verificação múltipla (mais robusta)
        login_ok = False
        
        # Teste 1: URL não contém "login"
        if "login" not in url_atual.lower():
            print("✅ Teste 1 OK: Não está mais na página de login")
            login_ok = True
        
        # Teste 2: URL contém alguma página do PJe
        if any(x in url_atual.lower() for x in ['quadroaviso', 'seam', 'painel', 'menu']):
            print("✅ Teste 2 OK: Está em página do PJe")
            login_ok = True
        
        # Teste 3: Verificar se vê o nome do usuário na página
        try:
            if "ELIANA" in self.driver.page_source or "eliana" in self.driver.page_source.lower():
                print("✅ Teste 3 OK: Nome de usuário encontrado na página")
                login_ok = True
        except:
            pass
        
        if login_ok:
            print("\n✅ LOGIN CONFIRMADO!")
            return True
        else:
            print("\n⚠️ Login não pode ser confirmado automaticamente")
            opcao = input("   Deseja continuar mesmo assim? (s/n): ").lower()
            return opcao == 's'
    
    def acessar_push(self):
        print("\n🔔 Acessando PJe PUSH...")
        
        url_push = "https://pje1g.trf1.jus.br/pje/Push/listView.seam"
        print(f"   URL: {url_push}")
        
        self.driver.get(url_push)
        time.sleep(4)
        
        url_atual = self.driver.current_url
        print(f"   URL atual: {url_atual}")
        
        if "push" in url_atual.lower():
            print("✅ PUSH acessado!")
            return True
        
        print("⚠️ Tente acessar manualmente")
        input(">>> Pressione ENTER quando estiver na página do PUSH <<<\n")
        return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # ESTRATÉGIA 1: Procurar por ID específico (mais provável)
            campo = None
            ids_possiveis = [
                'numeroProcesso',
                'formPush:numeroProcesso',
                'form:numeroProcesso',
                'processo',
                'txtNumeroProcesso'
            ]
            
            for id_campo in ids_possiveis:
                try:
                    campo = self.driver.find_element(By.ID, id_campo)
                    print(f"   ✅ Campo encontrado com ID: {id_campo}")
                    break
                except:
                    continue
            
            # ESTRATÉGIA 2: Por placeholder
            if not campo:
                try:
                    campo = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, '_')]")
                    print(f"   ✅ Campo encontrado por placeholder")
                except:
                    pass
            
            # ESTRATÉGIA 3: Primeiro input text
            if not campo:
                try:
                    inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                    if inputs:
                        campo = inputs[0]
                        print(f"   ✅ Usando primeiro input text")
                except:
                    pass
            
            if not campo:
                print("   ❌ Campo não encontrado! Tire um screenshot para debug")
                self.driver.save_screenshot(f"erro_campo_{numero}.png")
                self.falhas.append(numero)
                return False
            
            # Preencher
            campo.clear()
            time.sleep(0.5)
            campo.send_keys(numero)
            time.sleep(1)
            
            print(f"   ✅ Número digitado: {numero}")
            
            # Procurar botão INCLUIR
            btn = None
            xpaths_btn = [
                "//button[text()='INCLUIR']",
                "//input[@value='INCLUIR']",
                "//button[contains(text(), 'INCLUIR')]",
                "//*[contains(text(), 'INCLUIR') and (self::button or self::input)]",
                "//button[@type='submit']",
                "//input[@type='submit']"
            ]
            
            for xpath in xpaths_btn:
                try:
                    btn = self.driver.find_element(By.XPATH, xpath)
                    print(f"   ✅ Botão encontrado")
                    break
                except:
                    continue
            
            if not btn:
                print("   ❌ Botão INCLUIR não encontrado!")
                self.driver.save_screenshot(f"erro_botao_{numero}.png")
                self.falhas.append(numero)
                return False
            
            # Clicar
            btn.click()
            print(f"   ⏳ Aguardando resposta...")
            time.sleep(4)
            
            # Verificar resultado
            page = self.driver.page_source.lower()
            
            if any(x in page for x in ['sucesso', 'incluído', 'cadastrado', 'adicionado']):
                print(f"   ✅ {numero} CADASTRADO COM SUCESSO!")
                self.sucessos.append(numero)
                return True
            elif any(x in page for x in ['já cadastrado', 'já existe', 'duplicado']):
                print(f"   ⚠️  {numero} já estava cadastrado")
                self.sucessos.append(numero)
                return True
            else:
                print(f"   ⚠️  Status desconhecido")
                self.falhas.append(numero)
                return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:150]}")
            self.falhas.append(numero)
            
            # Screenshot para debug
            try:
                self.driver.save_screenshot(f"erro_{numero}.png")
                print(f"   📸 Screenshot salvo: erro_{numero}.png")
            except:
                pass
            
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
            
            # Intervalo entre cadastros
            if idx < total:
                time.sleep(2)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   Total: {total}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        print(f"   📊 Taxa de sucesso: {(len(self.sucessos)/total*100):.1f}%")
        
        if self.sucessos:
            print(f"\n✅ {len(self.sucessos)} PROCESSOS CADASTRADOS:")
            for p in self.sucessos[:10]:  # Mostrar no máximo 10
                print(f"   - {p}")
            if len(self.sucessos) > 10:
                print(f"   ... e mais {len(self.sucessos)-10}")
        
        if self.falhas:
            print(f"\n❌ {len(self.falhas)} FALHAS:")
            for p in self.falhas:
                print(f"   - {p}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 CADASTRO AUTOMÁTICO NO PUSH - VERSÃO FINAL")
    print("="*70)
    
    cadastro = CadastroPushFinal()
    
    try:
        input("\n⚠️  Token A3 conectado? ENTER para começar...\n")
        
        if cadastro.login():
            if cadastro.acessar_push():
                
                print("\n💡 ESCOLHA O MODO:")
                print("   1. Planilha em lote (vários processos)")
                print("   2. Processo individual (teste)")
                
                modo = input("\nDigite 1 ou 2: ").strip()
                
                if modo == "1":
                    print("\n📁 Planilhas disponíveis:")
                    for f in os.listdir('.'):
                        if 'push' in f.lower() and f.endswith('.xlsx'):
                            print(f"   - {f}")
                    
                    arq = input("\n📄 Nome do arquivo: ").strip().strip('"').strip("'")
                    cadastro.processar_planilha(arq)
                
                elif modo == "2":
                    num = input("\n📝 Número do processo: ").strip()
                    cadastro.cadastrar_processo(num)
                
                else:
                    print("❌ Opção inválida!")
        
        input("\n\n>>> Pressione ENTER para fechar o navegador <<<\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cadastro.fechar()
    
    print("\n" + "="*70)
    print("✅ SCRIPT FINALIZADO!")
    print("="*70)
