"""
VERSÃO FINAL - FILTRO PRECISO + JAVASCRIPT CLICK
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os
import openpyxl
from datetime import datetime
from dotenv import load_dotenv
import shutil
import glob

class BuscadorTJSP_FiltroOtimizado:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_VALIDOS")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Pasta de downloads
        self.pasta_downloads = os.path.join(os.getcwd(), "downloads_edge")
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
        
        self.janela_principal = None
    
    def iniciar_edge(self):
        """Inicia Edge com downloads configurados"""
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
        """Limpa pasta de downloads"""
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
                print(f"❌ Não encontrado")
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
            
            print(f"   🔍 Localizando links de documentos...", end=" ", flush=True)
            
            # FILTRO OTIMIZADO - Apenas links que parecem ser documentos
            script_otimizado = """
            let links = [];
            document.querySelectorAll('a').forEach((a, index) => {
                let texto = a.textContent.toLowerCase();
                let href = a.href;
                
                // IGNORAR links de navegação/sistema
                if (texto.includes('colégio') || texto.includes('turma') || 
                    texto.includes('uniformização') || texto.includes('recursal') ||
                    href.includes('cposgcr') || href.includes('cpopg/open.do')) {
                    return; // Pular este link
                }
                
                // ACEITAR apenas se tiver indicadores de documento
                if ((texto.includes('ofício') || texto.includes('requisitório') || 
                     texto.includes('or ') || texto.includes('depre') || 
                     texto.match(/^\d/) || // Começa com número
                     href.includes('downloadDocumento') || href.includes('.pdf') ||
                     href.includes('documento') || href.includes('anexo'))
                    && href && href.length > 0 && !href.includes('javascript')) {
                    
                    a.setAttribute('data-doc-id', 'doc_' + index);
                    
                    links.push({
                        id: 'doc_' + index,
                        texto: a.textContent.trim().substring(0, 50),
                        href: href
                    });
                }
            });
            return links;
            """
            
            documentos = self.driver.execute_script(script_otimizado)
            
            if not documentos or len(documentos) == 0:
                print(f"⚠️  Nenhum documento")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(documentos)} documento(s)")
            
            baixados = 0
            
            for idx_doc, doc in enumerate(documentos, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_final = f"{nome_limpo}_doc_{idx_doc}.pdf"
                
                print(f"   📥 [{idx_doc}/{len(documentos)}] {doc['texto'][:30]}...", end=" ", flush=True)
                
                try:
                    # Limpar downloads
                    self.limpar_downloads()
                    
                    # Localizar elemento
                    elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-doc-id='{doc['id']}']")
                    
                    # FORÇAR CLIQUE VIA JAVASCRIPT
                    self.driver.execute_script("arguments[0].click();", elemento)
                    
                    # Aguardar download
                    if self.aguardar_download(timeout=15):
                        pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                        
                        if len(pdfs) > 0:
                            arquivo_temp = pdfs[0]
                            tamanho = os.path.getsize(arquivo_temp)
                            
                            # Validar PDF
                            with open(arquivo_temp, 'rb') as f:
                                primeiros = f.read(10)
                            
                            if primeiros.startswith(b'%PDF'):
                                # Mover para pasta final
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
                    
                    # Voltar para página
                    self.driver.get(url_requisitorios)
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Erro")
            
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
        
        # Limpar downloads temp
        try:
            shutil.rmtree(self.pasta_downloads)
        except:
            pass
        
        print("="*70)
    
    def executar(self):
        """Execução"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR FINAL - FILTRO OTIMIZADO")
        print("="*70)
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            return
        
        print(f"\n📋 Total: {len(processos)}")
        
        confirma = input(f"\n>>> Processar? (s/n): ").lower()
        
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
    buscador = BuscadorTJSP_FiltroOtimizado()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERROMPIDO")
    
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
