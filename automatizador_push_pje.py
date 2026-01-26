"""
Automação para Cadastro de Processos no Serviço PUSH do PJe
Cadastra múltiplos processos automaticamente para receber notificações
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

class AutomatizadorPushPJe:
    """Cadastra processos no serviço push automaticamente"""
    
    def __init__(self):
        self.driver = None
        self.processos_cadastrados = []
        self.processos_falha = []
    
    def iniciar_navegador(self):
        """Inicia Chrome/Edge"""
        
        print("\n🌐 Iniciando navegador...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Navegador iniciado!")
        return self.driver
    
    def fazer_login_pje(self, url_pje):
        """Login no PJe com certificado A3"""
        
        if not self.driver:
            self.iniciar_navegador()
        
        print(f"\n🔐 Acessando PJe: {url_pje}")
        self.driver.get(url_pje)
        
        print("\n⚠️  FAÇA LOGIN COM SEU CERTIFICADO:")
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token")
        print("   4. Aguarde o login")
        
        input("\n>>> Pressione ENTER após completar o login <<<")
        
        # Verificar login
        if "login" not in self.driver.current_url.lower():
            print("✅ Login realizado com sucesso!")
            return True
        else:
            print("❌ Login não realizado")
            return False
    
    def acessar_servico_push(self):
        """Acessa a área de configuração do serviço push"""
        
        try:
            print("\n🔔 Acessando serviço PUSH...")
            
            wait = WebDriverWait(self.driver, 15)
            
            # MÉTODO 1: Via menu (mais comum)
            try:
                # Clicar em "Configurações" ou "Preferências"
                menu_config = wait.until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Configurações"))
                )
                menu_config.click()
                time.sleep(2)
                
                # Procurar "Serviço Push"
                link_push = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Serviço Push")
                link_push.click()
                time.sleep(2)
                
                print("✅ Serviço Push acessado via menu!")
                return True
                
            except:
                pass
            
            # MÉTODO 2: Via URL direta (mais rápido)
            try:
                # URL típica do serviço push no PJe
                base_url = self.driver.current_url.split("/pje/")[0]
                url_push = f"{base_url}/pje/Processo/CadastroPush/listView.seam"
                
                print(f"   Tentando URL direta: {url_push}")
                self.driver.get(url_push)
                time.sleep(3)
                
                # Verificar se chegou na página certa
                if "push" in self.driver.current_url.lower():
                    print("✅ Serviço Push acessado via URL direta!")
                    return True
                
            except:
                pass
            
            # MÉTODO 3: Navegação manual assistida
            print("\n⚠️  Não consegui acessar automaticamente")
            print("\n📋 ACESSE MANUALMENTE:")
            print("   1. No menu do PJe, vá em 'Configurações'")
            print("   2. Clique em 'Serviço Push' ou 'Notificações'")
            print("   3. Volte aqui quando estiver na página do Push")
            
            input("\n>>> Pressione ENTER quando estiver na página do Push <<<")
            
            return True
        
        except Exception as e:
            print(f"❌ Erro ao acessar Push: {str(e)}")
            return False
    
    def cadastrar_processo_push(self, numero_processo):
        """Cadastra um processo no serviço push"""
        
        try:
            print(f"\n📝 Cadastrando: {numero_processo}")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Botão "Novo" ou "Adicionar Processo"
            try:
                btn_novo = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Novo')] | //a[contains(text(), 'Adicionar')]"))
                )
                btn_novo.click()
                time.sleep(2)
            except:
                # Tentar input direto
                pass
            
            # Campo de número do processo
            campo_numero = wait.until(
                EC.presence_of_element_located((By.ID, "numeroProcesso"))
            )
            campo_numero.clear()
            campo_numero.send_keys(numero_processo)
            
            # Botão Salvar/Cadastrar
            btn_salvar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Salvar')] | //button[contains(text(), 'Cadastrar')]")
            btn_salvar.click()
            
            time.sleep(2)
            
            # Verificar se cadastrou
            if "sucesso" in self.driver.page_source.lower() or "cadastrado" in self.driver.page_source.lower():
                print(f"   ✅ {numero_processo} cadastrado!")
                self.processos_cadastrados.append(numero_processo)
                return True
            else:
                print(f"   ⚠️  {numero_processo} pode não ter sido cadastrado")
                self.processos_falha.append(numero_processo)
                return False
        
        except Exception as e:
            print(f"   ❌ Erro ao cadastrar {numero_processo}: {str(e)}")
            self.processos_falha.append(numero_processo)
            return False
    
    def cadastrar_em_lote(self, arquivo_excel):
        """Cadastra múltiplos processos de uma planilha"""
        
        print(f"\n📊 Processando planilha: {arquivo_excel}")
        
        if not os.path.exists(arquivo_excel):
            print(f"❌ Arquivo não encontrado: {arquivo_excel}")
            return
        
        wb = openpyxl.load_workbook(arquivo_excel)
        ws = wb.active
        
        total = 0
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            numero_processo = row[0]
            
            if numero_processo:
                total += 1
                self.cadastrar_processo_push(numero_processo)
                time.sleep(1)  # Intervalo entre cadastros
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO DO CADASTRO:")
        print(f"   Total processado: {total}")
        print(f"   ✅ Sucesso: {len(self.processos_cadastrados)}")
        print(f"   ❌ Falhas: {len(self.processos_falha)}")
        
        if self.processos_falha:
            print("\n⚠️  Processos com falha:")
            for proc in self.processos_falha:
                print(f"   - {proc}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# TESTE
if __name__ == "__main__":
    print("="*70)
    print("🔔 AUTOMATIZADOR DE CADASTRO NO SERVIÇO PUSH DO PJE")
    print("="*70)
    
    automatizador = AutomatizadorPushPJe()
    
    try:
        print("\n📋 PRÉ-REQUISITOS:")
        print("   ✅ Token A3 conectado")
        print("   ✅ PIN do token em mãos")
        print("   ✅ Planilha Excel com processos")
        
        input("\nPressione ENTER para começar...")
        
        # URL do PJe (adapte conforme seu tribunal)
        url_pje = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        # 1. Fazer login
        if automatizador.fazer_login_pje(url_pje):
            
            # 2. Acessar serviço push
            if automatizador.acessar_servico_push():
                
                # 3. Escolher modo
                print("\n💡 ESCOLHA O MODO:")
                print("   1. Cadastrar processos de planilha (em lote)")
                print("   2. Cadastrar processo individual")
                
                modo = input("\nEscolha (1/2): ")
                
                if modo == "1":
                    arquivo = input("\nCaminho da planilha Excel: ")
                    automatizador.cadastrar_em_lote(arquivo)
                
                elif modo == "2":
                    numero = input("\nNúmero do processo: ")
                    automatizador.cadastrar_processo_push(numero)
        
        input("\n\nPressione ENTER para fechar...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
    
    finally:
        automatizador.fechar()
    
    print("\n✅ CONCLUÍDO!")
