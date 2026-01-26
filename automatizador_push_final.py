"""
Automatizador PUSH - VERSÃO MELHORADA COM DEBUG
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

class AutomatizadorPushMelhorado:
    
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
        
        print("\n" + "="*70)
        print("⚠️  INSTRUÇÕES DE LOGIN:")
        print("="*70)
        print("   1. Na página do PJe, clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token")
        print("   4. AGUARDE até entrar no sistema (pode demorar)")
        print("   5. Você verá a tela inicial do PJe logado")
        print("="*70)
        
        input("\n>>> Pressione ENTER SOMENTE APÓS VER A TELA INICIAL DO PJE <<<\n")
        
        # Verificar URL atual
        url_atual = self.driver.current_url
        print(f"\n🔍 URL atual: {url_atual}")
        
        # Verificação mais robusta
        if "login" in url_atual.lower():
            print("\n❌ ATENÇÃO: Ainda está na tela de login!")
            print("   A URL contém 'login'")
            
            opcao = input("\n   Deseja tentar continuar mesmo assim? (s/n): ").lower()
            if opcao == 's':
                print("   ⚠️ Continuando mesmo sem confirmar login...")
                return True
            else:
                print("   ❌ Faça o login e execute o script novamente")
                return False
        else:
            print("✅ Login parece OK! (não está mais na página de login)")
            return True
    
    def acessar_push(self):
        print("\n🔔 Acessando serviço PUSH...")
        
        base = self.driver.current_url.split("/pje/")[0]
        url_push = f"{base}/pje/Processo/CadastroPush/listView.seam"
        
        print(f"   URL do PUSH: {url_push}")
        
        self.driver.get(url_push)
        time.sleep(5)
        
        url_atual = self.driver.current_url
        print(f"   URL atual: {url_atual}")
        
        if "push" in url_atual.lower() or "cadastropush" in url_atual.lower():
            print("✅ PUSH acessado com sucesso!")
            return True
        else:
            print("\n⚠️ Não consegui acessar automaticamente")
            print("   Navegue manualmente até o serviço PUSH:")
            print("   Menu > Configurações > Serviço Push")
            
            input("\n>>> Pressione ENTER quando estiver na página do PUSH <<<\n")
            return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Cadastrando: {numero}")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Procurar campo de número
            try:
                campo = wait.until(
                    EC.presence_of_element_located((By.ID, "numeroProcesso"))
                )
                campo.clear()
                campo.send_keys(numero)
                
                # Botão cadastrar
                btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cadastrar')] | //button[contains(text(), 'Salvar')] | //input[@value='Cadastrar']")
                btn.click()
                
                time.sleep(3)
                
                print(f"   ✅ {numero} cadastrado!")
                self.processos_ok.append(numero)
                return True
                
            except Exception as e:
                print(f"   ⚠️ Erro ao cadastrar: {str(e)}")
                print(f"   Pode já estar cadastrado ou houve problema")
                self.processos_erro.append(numero)
                return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            self.processos_erro.append(numero)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Processando planilha: {arquivo}")
        
        # Verificar se arquivo existe
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado: {arquivo}")
            print(f"\n📁 Arquivos disponíveis na pasta atual:")
            
            for f in os.listdir('.'):
                if f.endswith('.xlsx'):
                    print(f"   - {f}")
            
            return
        
        print(f"✅ Arquivo encontrado! Abrindo...")
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        print(f"\n📋 Lendo processos da planilha...")
        
        total = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            numero = row[0]
            if numero:
                total += 1
                print(f"\n--- Processo {total} ---")
                self.cadastrar_processo(str(numero).strip())
                time.sleep(2)  # Intervalo entre cadastros
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   Total na planilha: {total}")
        print(f"   ✅ Cadastrados com sucesso: {len(self.processos_ok)}")
        print(f"   ❌ Erros/Já cadastrados: {len(self.processos_erro)}")
        
        if self.processos_ok:
            print("\n✅ Processos cadastrados:")
            for proc in self.processos_ok:
                print(f"   - {proc}")
        
        if self.processos_erro:
            print("\n⚠️ Processos com erro:")
            for proc in self.processos_erro:
                print(f"   - {proc}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 CADASTRO AUTOMÁTICO NO PUSH DO PJE - VERSÃO MELHORADA")
    print("="*70)
    
    auto = AutomatizadorPushMelhorado()
    
    try:
        print("\n📋 PRÉ-REQUISITOS:")
        print("   ✅ Token A3 conectado na USB")
        print("   ✅ PIN do token em mãos")
        print("   ✅ Planilha Excel editada com processos REAIS")
        
        input("\n>>> Pressione ENTER para começar <<<\n")
        
        # Login
        url = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        if auto.login_pje(url):
            print("\n✅ Prosseguindo para o PUSH...")
            
            if auto.acessar_push():
                print("\n✅ Pronto para cadastrar processos!")
                
                print("\n💡 MODO DE CADASTRO:")
                print("   1. Planilha em lote (vários processos)")
                print("   2. Processo individual")
                
                modo = input("\nEscolha (1 ou 2): ").strip()
                
                if modo == "1":
                    print("\n📁 Arquivos Excel disponíveis:")
                    for f in os.listdir('.'):
                        if f.endswith('.xlsx'):
                            print(f"   - {f}")
                    
                    arq = input("\n📄 Digite o nome do arquivo (copie e cole): ").strip()
                    
                    # Remover aspas se o usuário colou com aspas
                    arq = arq.strip('"').strip("'")
                    
                    print(f"\n📂 Tentando abrir: {arq}")
                    auto.processar_planilha(arq)
                
                elif modo == "2":
                    num = input("\n📝 Digite o número do processo: ").strip()
                    auto.cadastrar_processo(num)
                
                else:
                    print("❌ Opção inválida!")
            else:
                print("❌ Não conseguiu acessar o PUSH")
        else:
            print("❌ Login não foi completado")
        
        input("\n\n>>> Pressione ENTER para fechar o navegador <<<\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        auto.fechar()
    
    print("\n" + "="*70)
    print("✅ SCRIPT FINALIZADO!")
    print("="*70)
