"""
SOLUÇÃO FINAL - CLIQUE REAL NO ELEMENTO (SEM EXECUTAR ONCLICK)
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import openpyxl
from datetime import datetime
from dotenv import load_dotenv
import shutil
import glob
import traceback

class BuscadorTJSP_CliqueReal:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = "oficios_TESTE_FINAL"
        self.planilha = "processos_TESTE_3.xlsx"
        
        # Limpar pastas
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.pasta_downloads = "downloads_TESTE"
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        self.janela_principal = None
        self.total_pdfs = 0
        
        # Log
        self.log_file = open("log_clique_real.txt", "w", encoding="utf-8")
    
    def log(self, msg):
        """Log com timestamp"""
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        linha = f"[{ts}] {msg}"
        self.log_file.write(linha + "\n")
        self.log_file.flush()
    
    def iniciar_edge(self):
        """Inicia Edge"""
        print("\n🔷 Iniciando Edge...")
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_downloads),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        self.driver = webdriver.Edge(options=options)
        self.janela_principal = self.driver.current_window_handle
        
        self.log(f"Edge iniciado - Handle: {self.janela_principal}")
        print("✅ Edge iniciado!")
    
    def fazer_login_certificado(self):
        """Login"""
        print(f"\n🔐 Login com Certificado...")
        self.log("LOGIN - Iniciando")
        
        self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        print(f"\n{'='*70}")
        print(f"🔐 SELECIONE SEU CERTIFICADO")
        print(f"{'='*70}")
        print(f"\n   📜 Serial: 24a59a14555d0e24")
        print(f"   ⏳ Aguardando 15 segundos...")
        
        time.sleep(15)
        
        self.log(f"LOGIN - Concluído: {self.driver.current_url}")
        print(f"\n✅ Continuando...")
        return True
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca processo"""
        try:
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, 10)
            
            try:
                radio = wait.until(EC.element_to_be_clickable((By.ID, "radioNumeroAntigo")))
                radio.click()
                time.sleep(0.5)
            except:
                pass
            
            campo = wait.until(EC.visibility_of_element_located((By.ID, "nuProcessoAntigoFormatado")))
            
            campo.clear()
            campo.send_keys(numero_processo)
            campo.send_keys(Keys.RETURN)
            
            time.sleep(2.5)
            
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                self.log(f"Código encontrado: {codigo}")
                return codigo
            
            return None
            
        except:
            return None
    
    def extrair_foro(self, numero_processo):
        """Extrai foro"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def aguardar_download(self, timeout=20):
        """Aguarda download"""
        self.log(f"Aguardando download (timeout: {timeout}s)")
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            arquivos_temp = glob.glob(os.path.join(self.pasta_downloads, "*.crdownload"))
            arquivos_temp += glob.glob(os.path.join(self.pasta_downloads, "*.tmp"))
            
            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
            
            tempo_decorrido = time.time() - tempo_inicio
            
            if len(arquivos_temp) > 0:
                self.log(f"  [{tempo_decorrido:.1f}s] Download em andamento: {len(arquivos_temp)} temp")
            
            if len(arquivos_temp) == 0 and len(pdfs) > 0:
                self.log(f"  [{tempo_decorrido:.1f}s] DOWNLOAD COMPLETO! PDF: {pdfs[0]}")
                time.sleep(1)
                return True
            
            time.sleep(0.5)
        
        self.log(f"Download - TIMEOUT após {timeout}s")
        return False
    
    def limpar_downloads(self):
        """Limpa pasta"""
        for arquivo in os.listdir(self.pasta_downloads):
            try:
                os.remove(os.path.join(self.pasta_downloads, arquivo))
            except:
                pass
    
    def processar_primeiro_documento(self, numero_processo):
        """Processa APENAS primeiro documento com diagnóstico ultra-detalhado"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ DIAGNÓSTICO: {numero_processo}")
            print(f"{'='*70}")
            
            self.log(f"\n{'='*70}")
            self.log(f"PROCESSO: {numero_processo}")
            self.log(f"{'='*70}")
            
            # 1. Buscar código
            print(f"\n📍 ETAPA 1: Buscar código do processo")
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"   ❌ Não encontrado")
                return False
            
            print(f"   ✅ Código: {codigo}")
            
            # 2. Acessar requisitórios
            foro = self.extrair_foro(numero_processo)
            
            url_requisitorios = (
                f"https://esaj.tjsp.jus.br/cpopg/show.do?"
                f"processo.codigo={codigo}&"
                f"processo.foro={foro}&"
                f"processo.numero={numero_processo}&"
                f"consultaDeRequisitorios=true"
            )
            
            print(f"\n📍 ETAPA 2: Acessar página de requisitórios")
            self.log(f"URL: {url_requisitorios}")
            
            self.driver.get(url_requisitorios)
            time.sleep(3)
            
            print(f"   ✅ Página carregada")
            self.log(f"Página atual: {self.driver.current_url}")
            
            # 3. Buscar documentos
            print(f"\n📍 ETAPA 3: Localizar documentos na página")
            
            script_busca = """
            let docs = [];
            
            document.querySelectorAll('a.linkMovVincProc').forEach((a, idx) => {
                let texto = a.textContent.trim();
                
                if (texto.includes('DEPRE') || texto.includes('Ofício') ||
                    texto.includes('Decisão') || texto.includes('Certidão')) {
                    
                    a.setAttribute('data-doc-id', 'doc_' + idx);
                    
                    docs.push({
                        id: 'doc_' + idx,
                        texto: texto,
                        onclick: a.getAttribute('onclick'),
                        href: a.href,
                        target: a.getAttribute('target')
                    });
                }
            });
            
            return docs;
            """
            
            documentos = self.driver.execute_script(script_busca)
            
            if not documentos:
                print(f"   ❌ Nenhum documento encontrado")
                return False
            
            print(f"   ✅ {len(documentos)} documentos encontrados")
            self.log(f"Documentos encontrados: {len(documentos)}")
            
            # 4. Processar PRIMEIRO documento
            doc = documentos[0]
            
            print(f"\n📍 ETAPA 4: Processar primeiro documento")
            print(f"   📄 Título: {doc['texto'][:50]}")
            print(f"   🔗 URL: {doc['href'][:80]}")
            print(f"   ⚙️  OnClick: {doc['onclick']}")
            
            self.log(f"\nPRIMEIRO DOCUMENTO:")
            self.log(f"  Texto: {doc['texto']}")
            self.log(f"  URL: {doc['href']}")
            self.log(f"  OnClick: {doc['onclick']}")
            
            # Limpar downloads
            self.limpar_downloads()
            self.log("Pasta de downloads limpa")
            
            # Contar janelas
            janelas_antes = len(self.driver.window_handles)
            self.log(f"Janelas ANTES: {janelas_antes}")
            print(f"\n   📊 Janelas abertas: {janelas_antes}")
            
            # 5. CLICAR NO ELEMENTO (NÃO EXECUTAR JAVASCRIPT)
            print(f"\n📍 ETAPA 5: Clicar no documento")
            
            try:
                # Localizar elemento
                print(f"   🔍 Localizando elemento...", end=" ", flush=True)
                elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-doc-id='{doc['id']}']")
                self.log("Elemento localizado")
                print(f"✅")
                
                # MÉTODO 1: Scroll até elemento
                print(f"   📜 Rolando até elemento...", end=" ", flush=True)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                time.sleep(1)
                self.log("Scroll realizado")
                print(f"✅")
                
                # MÉTODO 2: Usar ActionChains para clique real
                print(f"   👆 Simulando clique real do usuário...", end=" ", flush=True)
                
                actions = ActionChains(self.driver)
                actions.move_to_element(elemento).pause(0.5).click().perform()
                
                self.log("Clique real executado via ActionChains")
                print(f"✅")
                
                # 6. Aguardar nova aba
                print(f"\n📍 ETAPA 6: Aguardar nova aba abrir")
                print(f"   ⏳ Aguardando 5 segundos...")
                time.sleep(5)
                
                janelas_depois = len(self.driver.window_handles)
                self.log(f"Janelas DEPOIS: {janelas_depois}")
                
                print(f"   📊 Janelas: antes={janelas_antes}, depois={janelas_depois}")
                
                if janelas_depois > janelas_antes:
                    print(f"   ✅ Nova aba detectada!")
                    self.log("SUCESSO - Nova aba aberta")
                    
                    # Mudar para nova aba
                    nova_aba = self.driver.window_handles[-1]
                    self.driver.switch_to.window(nova_aba)
                    
                    url_aba = self.driver.current_url
                    titulo = self.driver.title
                    
                    print(f"\n   📍 URL da nova aba: {url_aba}")
                    print(f"   📄 Título: {titulo}")
                    
                    self.log(f"Nova aba - URL: {url_aba}")
                    self.log(f"Nova aba - Título: {titulo}")
                    
                    # Screenshot
                    screenshot = "screenshot_nova_aba.png"
                    self.driver.save_screenshot(screenshot)
                    print(f"   📸 Screenshot: {screenshot}")
                    
                    # 7. Verificar tipo de conteúdo
                    print(f"\n📍 ETAPA 7: Analisar conteúdo da aba")
                    
                    script_analise = """
                    return {
                        url: window.location.href,
                        titulo: document.title,
                        temPDF: window.location.href.toLowerCase().includes('.pdf'),
                        temIframe: document.querySelectorAll('iframe').length,
                        temEmbed: document.querySelectorAll('embed[type*="pdf"]').length,
                        bodyText: document.body.textContent.substring(0, 200)
                    };
                    """
                    
                    info = self.driver.execute_script(script_analise)
                    
                    print(f"   📊 Análise:")
                    print(f"      URL contém .pdf: {info['temPDF']}")
                    print(f"      iFrames: {info['temIframe']}")
                    print(f"      Embeds PDF: {info['temEmbed']}")
                    print(f"      Texto inicial: {info['bodyText'][:50]}...")
                    
                    self.log(f"Análise aba: {info}")
                    
                    # 8. Aguardar download
                    print(f"\n📍 ETAPA 8: Aguardar download")
                    print(f"   ⏳ Verificando pasta de downloads por 10 segundos...")
                    
                    if self.aguardar_download(timeout=10):
                        print(f"   ✅ Download detectado!")
                        
                        pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                        
                        if pdfs:
                            arquivo = pdfs[0]
                            tamanho = os.path.getsize(arquivo)
                            
                            with open(arquivo, 'rb') as f:
                                primeiros = f.read(10)
                            
                            print(f"\n   📦 Arquivo baixado:")
                            print(f"      Nome: {os.path.basename(arquivo)}")
                            print(f"      Tamanho: {tamanho:,} bytes ({tamanho//1024} KB)")
                            print(f"      Primeiros bytes: {primeiros}")
                            
                            if primeiros.startswith(b'%PDF'):
                                print(f"      ✅ É UM PDF VÁLIDO!")
                                self.log("PDF VÁLIDO BAIXADO!")
                                self.total_pdfs += 1
                            else:
                                print(f"      ❌ NÃO É PDF (provavelmente HTML)")
                                self.log("Arquivo não é PDF válido")
                    else:
                        print(f"   ❌ Nenhum download após 10 segundos")
                        self.log("Timeout - nenhum download")
                    
                    # Fechar aba
                    print(f"\n   🔄 Fechando aba...")
                    self.driver.close()
                    self.driver.switch_to.window(self.janela_principal)
                    self.log("Aba fechada")
                    
                else:
                    print(f"   ❌ Nenhuma nova aba foi aberta")
                    self.log("ERRO - Nenhuma aba nova")
                    
                    # Verificar se há popup bloqueado
                    try:
                        alert = self.driver.switch_to.alert
                        texto_alert = alert.text
                        print(f"   ⚠️  ALERT detectado: {texto_alert}")
                        self.log(f"Alert: {texto_alert}")
                        alert.accept()
                    except:
                        pass
                
            except Exception as e:
                print(f"\n   ❌ ERRO AO CLICAR:")
                print(f"      Tipo: {type(e).__name__}")
                print(f"      Mensagem: {str(e)}")
                
                self.log(f"ERRO DETALHADO:")
                self.log(traceback.format_exc())
                
                # Voltar para janela principal
                try:
                    self.driver.switch_to.window(self.janela_principal)
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.log(f"ERRO GERAL: {traceback.format_exc()}")
            return False
    
    def carregar_processos(self):
        """Carrega planilha"""
        caminho = os.path.join(os.getcwd(), self.planilha)
        
        if not os.path.exists(caminho):
            return []
        
        wb = openpyxl.load_workbook(caminho)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    processos.append(num)
        
        wb.close()
        return processos
    
    def executar(self):
        """Execução"""
        print("\n" + "="*70)
        print("🔬 DIAGNÓSTICO COM CLIQUE REAL (ActionChains)")
        print("="*70)
        
        processos = self.carregar_processos()
        
        if not processos:
            print("\n❌ Nenhum processo na planilha")
            return
        
        print(f"\n📋 Testará APENAS 1 documento do primeiro processo")
        
        confirma = input(f"\n>>> Iniciar? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            self.fechar()
            return
        
        # Processar
        self.processar_primeiro_documento(processos[0])
        
        print(f"\n{'='*70}")
        print(f"✅ DIAGNÓSTICO CONCLUÍDO!")
        print(f"{'='*70}")
        print(f"\n📄 PDFs válidos baixados: {self.total_pdfs}")
        print(f"\n📁 Arquivos gerados:")
        print(f"   📄 log_clique_real.txt")
        print(f"   📸 screenshot_nova_aba.png (se abriu)")
        print(f"   📦 Pasta: {self.pasta_downloads}")
        
        input("\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        """Fecha"""
        if self.driver:
            self.driver.quit()
        
        if self.log_file:
            self.log_file.close()

if __name__ == "__main__":
    buscador = BuscadorTJSP_CliqueReal()
    
    try:
        buscador.executar()
    
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        traceback.print_exc()
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
