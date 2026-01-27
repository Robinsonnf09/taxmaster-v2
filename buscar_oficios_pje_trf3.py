"""
Script para buscar Ofícios Requisitórios no PJe TRF3
URL: https://pje1g.trf3.jus.br
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

class BuscadorOficiosPJeTRF3:
    
    def __init__(self):
        self.driver = None
        self.sucessos = []
        self.falhas = []
        self.url_base = "https://pje1g.trf3.jus.br"
        
        self.pasta_oficios = "oficios_requisitorios_pje_trf3"
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def login(self):
        print("\n🔐 Acessando PJe TRF3...")
        url_login = f"{self.url_base}/pje/login.seam"
        
        self.driver.get(url_login)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("⚠️  FAÇA LOGIN NO PJe TRF3:")
        print("="*70)
        print("   1. Clique em 'Certificado Digital'")
        print("   2. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   3. Digite o PIN do token")
        print("   4. Aguarde carregar a tela inicial do PJe")
        print("="*70)
        
        input("\n>>> ENTER após fazer login completo <<<\n")
        
        time.sleep(2)
        url_atual = self.driver.current_url
        
        if "login" not in url_atual.lower():
            print("✅ Login OK!")
            return True
        
        opcao = input("   Continuar mesmo assim? (s/n): ").lower()
        return opcao == 's'
    
    def navegar_para_consulta(self):
        print("\n📋 Navegando para consulta de processos...")
        
        print("\n💡 OPÇÕES DE ONDE ESTÁ A CONSULTA:")
        print("   1. Menu > Consulta Processual")
        print("   2. Menu > Processos > Consultar")
        print("   3. Barra de busca rápida")
        print("   4. Área de Precatórios")
        
        print("\n⚠️  NAVEGUE MANUALMENTE até a página onde você:")
        print("   - Digita o número do processo")
        print("   - Vê os documentos/expedientes")
        print("   - Pode baixar o Ofício Requisitório")
        
        input("\n>>> ENTER quando estiver na tela de consulta <<<\n")
        
        url_atual = self.driver.current_url
        print(f"✅ URL atual: {url_atual}")
        
        return True
    
    def buscar_processo(self, numero_processo):
        try:
            print(f"\n📝 Buscando: {numero_processo}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Procurar campo de busca
            campo = None
            
            # Estratégia 1: Campo visível com type=text
            try:
                campos = self.driver.find_elements(By.XPATH, "//input[@type='text' and not(@style='display: none')]")
                if campos:
                    campo = campos[0]
                    print(f"   ✅ Campo encontrado")
            except:
                pass
            
            # Estratégia 2: Por placeholder
            if not campo:
                try:
                    campo = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, 'processo') or contains(@placeholder, 'número')]")
                    print(f"   ✅ Campo encontrado (placeholder)")
                except:
                    pass
            
            # Estratégia 3: Manual
            if not campo:
                print(f"   ⚠️  Campo não encontrado automaticamente")
                print(f"   💡 Digite manualmente: {numero_processo}")
                input(f"   >>> Pressione ENTER após digitar e buscar <<<\n")
            else:
                # Preencher
                campo.clear()
                time.sleep(0.3)
                campo.send_keys(numero_processo)
                time.sleep(0.5)
                print(f"   ✅ Número digitado")
                
                # Tentar clicar em buscar
                try:
                    btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Pesquisar') or contains(text(), 'Buscar') or contains(text(), 'Consultar')] | //input[@type='submit']")
                    btn.click()
                    print(f"   ⏳ Consultando...")
                    time.sleep(5)
                except:
                    print(f"   ⚠️  Clique manualmente em PESQUISAR/CONSULTAR")
                    input(f"   >>> ENTER após clicar <<<\n")
            
            # Verificar se processo foi encontrado
            page = self.driver.page_source.lower()
            
            if "não encontrado" in page or "nenhum resultado" in page:
                print(f"   ❌ Processo não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            # Procurar documentos/expedientes
            print(f"   🔍 Procurando Ofício Requisitório...")
            
            print("\n   💡 ONDE PROCURAR O OFÍCIO:")
            print("   - Aba 'Documentos'")
            print("   - Aba 'Expedientes'")
            print("   - Aba 'Requisições'")
            print("   - Link 'Ofício Requisitório' ou 'OR'")
            
            # Procurar links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            oficios_encontrados = []
            
            for link in links:
                texto = link.text.lower()
                if any(x in texto for x in ['ofício', 'requisitório', 'or', 'requisição', 'precatório']):
                    oficios_encontrados.append(link)
            
            if not oficios_encontrados:
                print(f"   ⚠️  Nenhum ofício encontrado automaticamente")
                print(f"\n   💡 VERIFICAÇÃO MANUAL:")
                print(f"   - Há ofício requisitório neste processo?")
                print(f"   - Consegue ver/baixar?")
                
                opcao = input(f"\n   >>> Há ofício? (s/n): ").lower()
                
                if opcao == 's':
                    input(f"   >>> Baixe manualmente e pressione ENTER <<<\n")
                    self.sucessos.append(numero_processo)
                    return True
                else:
                    print(f"   ⚠️  Processo sem ofício ou não formado ainda")
                    self.falhas.append(numero_processo)
                    return False
            
            # Baixar ofícios encontrados
            print(f"   ✅ {len(oficios_encontrados)} ofício(s) encontrado(s)!")
            
            for idx, link in enumerate(oficios_encontrados, 1):
                try:
                    print(f"   📥 Baixando ofício {idx}...")
                    link.click()
                    time.sleep(4)
                    
                    # Verificar se abriu nova aba
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        time.sleep(2)
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    
                    print(f"   ✅ Ofício {idx} processado!")
                except Exception as e:
                    print(f"   ⚠️  Erro ao baixar ofício {idx}")
            
            self.sucessos.append(numero_processo)
            return True
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            self.falhas.append(numero_processo)
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
        print(f"✅ {total} processos")
        print(f"📁 Salvando em: {os.path.abspath(self.pasta_oficios)}\n")
        
        for idx, numero in enumerate(processos, 1):
            print(f"\n{'='*70}")
            print(f"Processo {idx}/{total}")
            print(f"{'='*70}")
            
            self.buscar_processo(numero)
            
            # Voltar para página de consulta
            if idx < total:
                print("\n   ⏪ Voltando para nova busca...")
                try:
                    # Tentar voltar
                    self.driver.back()
                    time.sleep(2)
                except:
                    print("   ⚠️  Navegue manualmente para nova busca")
                    input("   >>> ENTER quando estiver pronto <<<\n")
                
                time.sleep(2)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   🏛️  Tribunal: PJe TRF3")
        print(f"   📋 Total: {total}")
        print(f"   ✅ Com ofício: {len(self.sucessos)}")
        print(f"   ❌ Sem ofício/erro: {len(self.falhas)}")
        if total > 0:
            print(f"   📊 Taxa: {(len(self.sucessos)/total*100):.1f}%")
        
        print(f"\n📁 Ofícios em: {os.path.abspath(self.pasta_oficios)}")
        
        if self.falhas:
            print(f"\n❌ Processos sem ofício ({len(self.falhas)}):")
            for p in self.falhas[:20]:
                print(f"   - {p}")
            if len(self.falhas) > 20:
                print(f"   ... e mais {len(self.falhas)-20}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 BUSCA DE OFÍCIOS REQUISITÓRIOS - PJe TRF3")
    print("="*70)
    
    buscador = BuscadorOficiosPJeTRF3()
    
    try:
        input("\n⚠️  Token A3 conectado? ENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.login():
            if buscador.navegar_para_consulta():
                
                print("\n💡 MODO:")
                print("   1. Planilha (215 processos)")
                print("   2. Teste individual")
                
                modo = input("\nDigite 1 ou 2: ").strip()
                
                if modo == "1":
                    buscador.processar_planilha("processos_push_20260126_185045.xlsx")
                
                elif modo == "2":
                    num = input("\nNúmero do processo: ").strip()
                    buscador.buscar_processo(num)
        
        input("\n\n>>> ENTER para fechar <<<\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        buscador.fechar()
    
    print("\n✅ CONCLUÍDO!")
