"""
VERSÃO DIAGNÓSTICO ULTRA-DETALHADO
Mostra cada passo do processo de download
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import openpyxl
from datetime import datetime
from dotenv import load_dotenv
import shutil
import glob
import traceback

class BuscadorTJSP_DiagnosticoCompleto:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = "oficios_DIAGNOSTICO"
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = 10
        self.intervalo = 0.8
        
        # Limpar pastas
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.pasta_downloads = "downloads_DIAGNOSTICO"
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        self.janela_principal = None
        
        # Log detalhado
        self.log_file = open("diagnostico_detalhado.log", "w", encoding="utf-8")
    
    def log(self, mensagem):
        """Registra log no arquivo e console"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        linha = f"[{timestamp}] {mensagem}"
        self.log_file.write(linha + "\n")
        self.log_file.flush()
    
    def iniciar_edge(self):
        """Inicia Edge"""
        print("\n🔷 Iniciando Edge...")
        self.log("INICIAR EDGE - Começando")
        
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
        
        self.driver = webdriver.Edge(options=options)
        self.janela_principal = self.driver.current_window_handle
        
        self.log(f"INICIAR EDGE - Sucesso! Handle: {self.janela_principal}")
        print("✅ Edge iniciado!")
    
    def fazer_login_certificado(self):
        """Login"""
        print(f"\n🔐 Login com Certificado...")
        self.log("LOGIN - Iniciando")
        
        self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        self.log(f"LOGIN - URL acessada: {self.driver.current_url}")
        
        print(f"\n{'='*70}")
        print(f"🔐 SELECIONE SEU CERTIFICADO")
        print(f"{'='*70}")
        print(f"\n   📜 Serial: 24a59a14555d0e24")
        print(f"   ⏳ Aguardando 15 segundos...")
        
        time.sleep(15)
        
        self.log(f"LOGIN - Após espera: {self.driver.current_url}")
        
        print(f"\n✅ Continuando...")
        return True
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca processo"""
        try:
            self.log(f"BUSCAR PROCESSO - {numero_processo}")
            
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, self.timeout)
            
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
                self.log(f"BUSCAR PROCESSO - Código encontrado: {codigo}")
                return codigo
            
            self.log(f"BUSCAR PROCESSO - Não encontrado na URL: {url_atual}")
            return None
            
        except Exception as e:
            self.log(f"BUSCAR PROCESSO - ERRO: {str(e)}")
            return None
    
    def extrair_foro(self, numero_processo):
        """Extrai foro"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def buscar_oficios_processo(self, numero_processo, idx, total):
        """Processa APENAS PRIMEIRO DOCUMENTO com diagnóstico completo"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            self.log(f"\n{'='*70}")
            self.log(f"PROCESSO [{idx}/{total}] - {numero_processo}")
            self.log(f"{'='*70}")
            
            print(f"   🔍 Buscando código...", end=" ", flush=True)
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"❌")
                return False
            
            print(f"✅ {codigo}")
            
            foro = self.extrair_foro(numero_processo)
            
            url_requisitorios = (
                f"https://esaj.tjsp.jus.br/cpopg/show.do?"
                f"processo.codigo={codigo}&"
                f"processo.foro={foro}&"
                f"processo.numero={numero_processo}&"
                f"consultaDeRequisitorios=true"
            )
            
            self.log(f"URL REQUISITÓRIOS: {url_requisitorios}")
            
            print(f"   🎯 Acessando requisitórios...", end=" ", flush=True)
            self.driver.get(url_requisitorios)
            time.sleep(2)
            print(f"✅")
            
            self.log(f"PÁGINA CARREGADA: {self.driver.current_url}")
            
            # Buscar documentos
            print(f"   🔍 Buscando documentos...", end=" ", flush=True)
            
            script_busca = """
            let docs = [];
            
            document.querySelectorAll('a.linkMovVincProc').forEach((a, idx) => {
                let texto = a.textContent.trim();
                
                if (texto.includes('DEPRE') || texto.includes('Ofício') ||
                    texto.includes('Decisão') || texto.includes('Certidão')) {
                    
                    a.setAttribute('data-doc-idx', idx);
                    
                    docs.push({
                        index: idx,
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
            
            if not documentos or len(documentos) == 0:
                print(f"⚠️  Nenhum")
                self.log("DOCUMENTOS - Nenhum encontrado")
                return False
            
            print(f"✅ {len(documentos)}")
            self.log(f"DOCUMENTOS - {len(documentos)} encontrados")
            
            # PROCESSAR APENAS O PRIMEIRO DOCUMENTO COM DIAGNÓSTICO COMPLETO
            print(f"\n   🔬 DIAGNÓSTICO DETALHADO DO PRIMEIRO DOCUMENTO:")
            
            doc = documentos[0]
            
            print(f"      📄 Texto: {doc['texto']}")
            print(f"      🔗 URL: {doc['href']}")
            print(f"      🎯 Target: {doc['target']}")
            print(f"      ⚙️  OnClick: {doc['onclick']}")
            
            self.log(f"\n--- DOCUMENTO 1 ---")
            self.log(f"Texto: {doc['texto']}")
            self.log(f"URL: {doc['href']}")
            self.log(f"Target: {doc['target']}")
            self.log(f"OnClick: {doc['onclick']}")
            
            try:
                # Limpar downloads
                self.limpar_downloads()
                self.log("Downloads limpos")
                
                # Contar janelas antes
                janelas_antes = len(self.driver.window_handles)
                self.log(f"Janelas ANTES do clique: {janelas_antes}")
                
                # Localizar elemento
                print(f"\n      🔍 Localizando elemento...", end=" ", flush=True)
                elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-doc-idx='{doc['index']}']")
                self.log("Elemento localizado")
                print(f"✅")
                
                # Verificar onclick
                onclick_code = doc['onclick']
                
                if onclick_code:
                    print(f"      ⚙️  Executando JavaScript onClick...")
                    self.log(f"Executando onClick: {onclick_code}")
                    
                    # Remover 'javascript:' se existir
                    if onclick_code.startswith('javascript:'):
                        js_code = onclick_code.replace('javascript:', '')
                    else:
                        js_code = onclick_code
                    
                    # Executar JavaScript
                    resultado_js = self.driver.execute_script(js_code)
                    self.log(f"Resultado JavaScript: {resultado_js}")
                    
                    print(f"      ✅ JavaScript executado")
                    print(f"      ⏳ Aguardando 5 segundos...")
                    time.sleep(5)
                    
                    # Contar janelas depois
                    janelas_depois = len(self.driver.window_handles)
                    self.log(f"Janelas APÓS JavaScript: {janelas_depois}")
                    
                    print(f"      📊 Janelas antes: {janelas_antes}, depois: {janelas_depois}")
                    
                    if janelas_depois > janelas_antes:
                        print(f"      ✅ Nova aba aberta!")
                        self.log("Nova aba detectada")
                        
                        # Mudar para nova aba
                        nova_aba = self.driver.window_handles[-1]
                        self.driver.switch_to.window(nova_aba)
                        
                        url_nova_aba = self.driver.current_url
                        titulo_aba = self.driver.title
                        
                        print(f"      📍 URL da aba: {url_nova_aba[:80]}")
                        print(f"      📄 Título: {titulo_aba}")
                        
                        self.log(f"Nova aba - URL: {url_nova_aba}")
                        self.log(f"Nova aba - Título: {titulo_aba}")
                        
                        # Screenshot da nova aba
                        screenshot = f"aba_documento_1.png"
                        self.driver.save_screenshot(screenshot)
                        print(f"      📸 Screenshot: {screenshot}")
                        self.log(f"Screenshot salvo: {screenshot}")
                        
                        # Verificar conteúdo da página
                        page_source = self.driver.page_source[:500]
                        self.log(f"Conteúdo da página (500 chars): {page_source}")
                        
                        # Procurar por elementos de download
                        print(f"\n      🔍 Procurando elementos de download...")
                        
                        script_elementos = """
                        let info = {
                            temIframe: document.querySelectorAll('iframe').length,
                            temEmbed: document.querySelectorAll('embed').length,
                            temObject: document.querySelectorAll('object').length,
                            temBotaoDownload: document.querySelectorAll('a[download], button[download]').length,
                            urlContemPDF: window.location.href.includes('.pdf'),
                            tituloContemPDF: document.title.toLowerCase().includes('pdf'),
                            linksDownload: []
                        };
                        
                        // Procurar links de download
                        document.querySelectorAll('a').forEach(a => {
                            if (a.textContent.includes('Download') || 
                                a.textContent.includes('Baixar') ||
                                a.href.includes('download') ||
                                a.getAttribute('download')) {
                                info.linksDownload.push({
                                    texto: a.textContent.trim(),
                                    href: a.href
                                });
                            }
                        });
                        
                        return info;
                        """
                        
                        info_pagina = self.driver.execute_script(script_elementos)
                        
                        print(f"      📊 Análise da página:")
                        print(f"         iFrames: {info_pagina['temIframe']}")
                        print(f"         Embeds: {info_pagina['temEmbed']}")
                        print(f"         Objects: {info_pagina['temObject']}")
                        print(f"         Botões Download: {info_pagina['temBotaoDownload']}")
                        print(f"         URL contém PDF: {info_pagina['urlContemPDF']}")
                        print(f"         Título contém PDF: {info_pagina['tituloContemPDF']}")
                        print(f"         Links de download: {len(info_pagina['linksDownload'])}")
                        
                        self.log(f"Análise página: {info_pagina}")
                        
                        # Se encontrou links de download, clicar
                        if len(info_pagina['linksDownload']) > 0:
                            print(f"\n      🎯 Encontrado {len(info_pagina['linksDownload'])} link(s) de download!")
                            
                            for link_info in info_pagina['linksDownload']:
                                print(f"         📥 {link_info['texto']}")
                                self.log(f"Link download: {link_info}")
                        
                        # Aguardar possível download automático
                        print(f"\n      ⏳ Aguardando download automático (10s)...")
                        
                        if self.aguardar_download(timeout=10):
                            print(f"      ✅ Download detectado!")
                            
                            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                            
                            if len(pdfs) > 0:
                                arquivo = pdfs[0]
                                tamanho = os.path.getsize(arquivo)
                                
                                with open(arquivo, 'rb') as f:
                                    primeiros = f.read(10)
                                
                                print(f"      📄 Arquivo: {os.path.basename(arquivo)}")
                                print(f"      📦 Tamanho: {tamanho} bytes")
                                print(f"      🔍 Primeiros bytes: {primeiros}")
                                
                                self.log(f"Arquivo baixado: {arquivo}, tamanho: {tamanho}")
                                self.log(f"Primeiros bytes: {primeiros}")
                                
                                if primeiros.startswith(b'%PDF'):
                                    print(f"      ✅ PDF VÁLIDO!")
                                    self.log("PDF VÁLIDO!")
                                else:
                                    print(f"      ❌ NÃO É PDF!")
                                    self.log("ARQUIVO NÃO É PDF!")
                        else:
                            print(f"      ❌ Nenhum download detectado")
                            self.log("Nenhum download detectado após 10s")
                        
                        # Fechar aba
                        print(f"\n      🔄 Fechando aba...")
                        self.driver.close()
                        self.driver.switch_to.window(self.janela_principal)
                        self.log("Aba fechada, voltou para principal")
                        
                    else:
                        print(f"      ❌ Nenhuma nova aba aberta")
                        self.log("ERRO: Nenhuma aba nova aberta após onClick")
                
                else:
                    print(f"      ❌ Link sem onClick")
                    self.log("ERRO: Link não tem onClick")
                
            except Exception as e:
                print(f"\n      ❌ EXCEÇÃO: {str(e)}")
                self.log(f"EXCEÇÃO COMPLETA: {traceback.format_exc()}")
                
                # Garantir retorno à janela principal
                try:
                    self.driver.switch_to.window(self.janela_principal)
                except:
                    pass
            
            # PARAR APÓS PRIMEIRO PROCESSO
            print(f"\n{'='*70}")
            print(f"📋 DIAGNÓSTICO DO PRIMEIRO PROCESSO CONCLUÍDO")
            print(f"{'='*70}")
            print(f"\n💡 Verifique o arquivo: diagnostico_detalhado.log")
            
            input("\n>>> ENTER para continuar com próximo processo <<<\n")
            
            return False
            
        except Exception as e:
            self.log(f"ERRO GERAL: {traceback.format_exc()}")
            return False
    
    def aguardar_download(self, timeout=20):
        """Aguarda download"""
        self.log(f"AGUARDAR DOWNLOAD - Timeout: {timeout}s")
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            arquivos_temp = glob.glob(os.path.join(self.pasta_downloads, "*.crdownload"))
            arquivos_temp += glob.glob(os.path.join(self.pasta_downloads, "*.tmp"))
            
            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
            
            if len(arquivos_temp) == 0 and len(pdfs) > 0:
                self.log(f"DOWNLOAD COMPLETO - PDF encontrado: {pdfs[0]}")
                time.sleep(1)
                return True
            
            time.sleep(0.4)
        
        self.log("DOWNLOAD - Timeout atingido")
        return False
    
    def limpar_downloads(self):
        """Limpa pasta"""
        for arquivo in os.listdir(self.pasta_downloads):
            try:
                os.remove(os.path.join(self.pasta_downloads, arquivo))
            except:
                pass
    
    def carregar_processos_planilha(self):
        """Carrega planilha"""
        print(f"\n📊 Carregando: {self.planilha}")
        
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
        
        print(f"✅ {len(processos)} processos")
        return processos
    
    def executar(self):
        """Execução"""
        print("\n" + "="*70)
        print("🔬 MODO DIAGNÓSTICO ULTRA-DETALHADO")
        print("="*70)
        
        self.log("="*70)
        self.log("INÍCIO DA EXECUÇÃO")
        self.log("="*70)
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            return
        
        print(f"\n📋 Processará apenas PRIMEIRO processo com diagnóstico completo")
        
        confirma = input(f"\n>>> Iniciar? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            self.fechar()
            return
        
        # Processar apenas primeiro
        self.buscar_oficios_processo(processos[0], 1, 1)
        
        print(f"\n{'='*70}")
        print(f"✅ DIAGNÓSTICO COMPLETO!")
        print(f"{'='*70}")
        print(f"\nArquivos gerados:")
        print(f"   📄 diagnostico_detalhado.log")
        print(f"   📸 aba_documento_1.png (se conseguiu abrir)")
        
        input("\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        """Fecha navegador e arquivo de log"""
        if self.driver:
            self.driver.quit()
        
        if self.log_file:
            self.log_file.close()
        
        print("\n📄 Log salvo: diagnostico_detalhado.log")

if __name__ == "__main__":
    buscador = BuscadorTJSP_DiagnosticoCompleto()
    
    try:
        buscador.executar()
    
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print(f"\n🔍 Traceback completo:")
        traceback.print_exc()
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
