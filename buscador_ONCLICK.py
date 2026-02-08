"""
SOLUÇÃO FINAL - EXECUTA ONCLICK JAVASCRIPT DOS DOCUMENTOS
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

class BuscadorTJSP_OnClickJS:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_VALIDOS_FINAL")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Limpar e criar pasta de destino
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.pasta_downloads = os.path.join(os.getcwd(), "downloads_edge_final")
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
        
        self.janela_principal = None
    
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
        
        self.driver = webdriver.Edge(options=options)
        self.janela_principal = self.driver.current_window_handle
        
        print("✅ Edge iniciado!")
    
    def fazer_login_certificado(self):
        """Login"""
        print(f"\n🔐 Login com Certificado...")
        
        self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        print(f"\n{'='*70}")
        print(f"🔐 SELECIONE SEU CERTIFICADO")
        print(f"{'='*70}")
        print(f"\n   📜 Serial: 24a59a14555d0e24")
        print(f"   ⏳ Aguardando 15 segundos...")
        
        time.sleep(15)
        
        print(f"\n✅ Continuando...")
        return True
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca processo"""
        try:
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, self.timeout)
            
            try:
                radio = wait.until(EC.element_to_be_clickable((By.ID, "radioNumeroAntigo")))
                radio.click()
                time.sleep(0.5)
            except:
                pass
            
            try:
                campo = wait.until(EC.visibility_of_element_located((By.ID, "nuProcessoAntigoFormatado")))
            except:
                return None
            
            campo.clear()
            campo.send_keys(numero_processo)
            campo.send_keys(Keys.RETURN)
            
            time.sleep(2.5)
            
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                return codigo
            
            return None
            
        except:
            return None
    
    def extrair_foro(self, numero_processo):
        """Extrai foro"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def aguardar_nova_aba(self, timeout=10):
        """Aguarda nova aba abrir"""
        tempo_inicio = time.time()
        janelas_iniciais = len(self.driver.window_handles)
        
        while time.time() - tempo_inicio < timeout:
            if len(self.driver.window_handles) > janelas_iniciais:
                return True
            time.sleep(0.3)
        
        return False
    
    def aguardar_download(self, timeout=20):
        """Aguarda download"""
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            arquivos_temp = glob.glob(os.path.join(self.pasta_downloads, "*.crdownload"))
            arquivos_temp += glob.glob(os.path.join(self.pasta_downloads, "*.tmp"))
            
            if len(arquivos_temp) == 0:
                pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                if len(pdfs) > 0:
                    time.sleep(1)
                    return True
            
            time.sleep(0.4)
        
        return False
    
    def limpar_downloads(self):
        """Limpa pasta downloads"""
        for arquivo in os.listdir(self.pasta_downloads):
            try:
                os.remove(os.path.join(self.pasta_downloads, arquivo))
            except:
                pass
    
    def buscar_oficios_processo(self, numero_processo, idx, total):
        """Processa processo"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            print(f"   🔍 Buscando código...", end=" ", flush=True)
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"❌")
                self.falhas.append(numero_processo)
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
            
            print(f"   🎯 Acessando requisitórios...", end=" ", flush=True)
            self.driver.get(url_requisitorios)
            time.sleep(2)
            print(f"✅")
            
            print(f"   🔍 Localizando documentos...", end=" ", flush=True)
            
            # Buscar links com classe linkMovVincProc
            script_busca = """
            let docs = [];
            
            document.querySelectorAll('a.linkMovVincProc').forEach((a, idx) => {
                let texto = a.textContent.trim();
                
                // Filtrar apenas documentos relevantes
                if (texto.includes('DEPRE') || texto.includes('Ofício') || 
                    texto.includes('Decisão') || texto.includes('Certidão')) {
                    
                    a.setAttribute('data-doc-idx', idx);
                    
                    docs.push({
                        index: idx,
                        texto: texto,
                        onclick: a.getAttribute('onclick')
                    });
                }
            });
            
            return docs;
            """
            
            documentos = self.driver.execute_script(script_busca)
            
            if not documentos or len(documentos) == 0:
                print(f"⚠️  Nenhum")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(documentos)} doc(s)")
            
            baixados = 0
            
            for idx_doc, doc in enumerate(documentos, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_final = f"{nome_limpo}_doc_{idx_doc}.pdf"
                
                print(f"   📥 [{idx_doc}/{len(documentos)}] {doc['texto'][:35]}...", end=" ", flush=True)
                
                try:
                    # Limpar downloads
                    self.limpar_downloads()
                    
                    # Localizar elemento
                    elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-doc-idx='{doc['index']}']")
                    
                    # EXECUTAR O ONCLICK JAVASCRIPT DIRETAMENTE
                    onclick_code = doc['onclick']
                    
                    if onclick_code and onclick_code.startswith('javascript:'):
                        # Remover 'javascript:' do início
                        js_code = onclick_code.replace('javascript:', '')
                        
                        # Executar o código JavaScript
                        self.driver.execute_script(js_code)
                        
                        # Aguardar nova aba abrir
                        if self.aguardar_nova_aba(timeout=5):
                            # Mudar para nova aba
                            abas = self.driver.window_handles
                            self.driver.switch_to.window(abas[-1])
                            
                            time.sleep(2)
                            
                            # Verificar se é PDF ou se precisa clicar em algo
                            url_aba = self.driver.current_url
                            
                            if '.pdf' in url_aba.lower() or 'pdf' in self.driver.title.lower():
                                # É PDF - aguardar download
                                if self.aguardar_download(timeout=15):
                                    pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                                    
                                    if len(pdfs) > 0:
                                        arquivo_temp = pdfs[0]
                                        tamanho = os.path.getsize(arquivo_temp)
                                        
                                        # Validar
                                        with open(arquivo_temp, 'rb') as f:
                                            primeiros = f.read(10)
                                        
                                        if primeiros.startswith(b'%PDF'):
                                            destino = os.path.join(self.pasta_oficios, nome_final)
                                            shutil.move(arquivo_temp, destino)
                                            
                                            kb = tamanho // 1024
                                            print(f"✅ {kb} KB")
                                            baixados += 1
                                            self.total_pdfs += 1
                                        else:
                                            print(f"❌ HTML")
                                    else:
                                        print(f"❌ Timeout")
                                else:
                                    print(f"❌ Sem DL")
                            else:
                                print(f"❌ Não é PDF")
                            
                            # Fechar aba
                            self.driver.close()
                            self.driver.switch_to.window(self.janela_principal)
                        else:
                            print(f"❌ Sem aba")
                    else:
                        print(f"❌ Sem onClick")
                    
                    # Voltar para página
                    self.driver.get(url_requisitorios)
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Erro")
                    # Garantir que voltou
                    try:
                        self.driver.switch_to.window(self.janela_principal)
                    except:
                        pass
            
            if baixados > 0:
                self.sucessos.append(numero_processo)
                return True
            else:
                self.falhas.append(numero_processo)
                return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            self.falhas.append(numero_processo)
            return False
    
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
    
    def gerar_relatorio(self, inicio):
        """Relatório"""
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("🎉 CONCLUÍDO!")
        print("="*70)
        
        total = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total: {total}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        print(f"   📄 PDFs VÁLIDOS: {self.total_pdfs}")
        
        if total > 0:
            taxa = (len(self.sucessos) / total) * 100
            print(f"   📈 Taxa: {taxa:.1f}%")
        
        mins = int(duracao.total_seconds() / 60)
        segs = int(duracao.total_seconds() % 60)
        print(f"\n   ⏱️  Tempo: {mins}min {segs}s")
        
        pdfs = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"\n📁 Destino: {os.path.abspath(self.pasta_oficios)}")
        print(f"📄 PDFs: {len(pdfs)}")
        
        # Validar PDFs
        pdfs_validos = 0
        for pdf in pdfs:
            caminho = os.path.join(self.pasta_oficios, pdf)
            with open(caminho, 'rb') as f:
                if f.read(10).startswith(b'%PDF'):
                    pdfs_validos += 1
        
        print(f"✅ PDFs válidos: {pdfs_validos}")
        
        print("="*70)
    
    def executar(self):
        """Execução"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR FINAL - ONCLICK JAVASCRIPT")
        print("="*70)
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            return
        
        print(f"\n📋 Total: {len(processos)}")
        
        confirma = input(f"\n>>> Processar {len(processos)} processos? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            self.fechar()
            return
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficios_processo(numero, idx, len(processos))
            time.sleep(self.intervalo)
        
        self.gerar_relatorio(inicio)
        
        input("\n\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        """Fecha navegador"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    buscador = BuscadorTJSP_OnClickJS()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERROMPIDO")
    
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
