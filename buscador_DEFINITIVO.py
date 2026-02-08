"""
VERSÃO DEFINITIVA - CLIQUE DIRETO NOS LINKS
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

class BuscadorTJSP_CliqueLinks:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_requisitorios_tjsp")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Pasta de downloads temporários
        self.pasta_temp = os.path.join(os.getcwd(), "downloads_temp_final")
        if os.path.exists(self.pasta_temp):
            shutil.rmtree(self.pasta_temp)
        os.makedirs(self.pasta_temp)
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
    
    def iniciar_edge(self):
        """Inicia Edge com downloads automáticos"""
        print("\n🔷 Iniciando Edge...")
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        
        # Configurar pasta de download
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_temp),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        self.driver = webdriver.Edge(options=options)
        
        print("✅ Edge iniciado!")
        print(f"📁 Pasta temporária: {self.pasta_temp}")
        print(f"📁 Destino final: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login_certificado(self):
        """Login com certificado"""
        print(f"\n🔐 Login com Certificado...")
        
        try:
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
                
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")
            return False
    
    def aguardar_download(self, timeout=20):
        """Aguarda download completar"""
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            # Procurar arquivos temporários de download
            arquivos_temp = glob.glob(os.path.join(self.pasta_temp, "*.crdownload"))
            arquivos_temp += glob.glob(os.path.join(self.pasta_temp, "*.tmp"))
            
            # Se não há arquivos temporários
            if len(arquivos_temp) == 0:
                # Verificar se há PDF
                pdfs = glob.glob(os.path.join(self.pasta_temp, "*.pdf"))
                if len(pdfs) > 0:
                    time.sleep(0.5)  # Garantir gravação completa
                    return True
            
            time.sleep(0.3)
        
        return False
    
    def limpar_pasta_temp(self):
        """Limpa pasta temporária"""
        for arquivo in os.listdir(self.pasta_temp):
            try:
                os.remove(os.path.join(self.pasta_temp, arquivo))
            except:
                pass
    
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
            
            print(f"   🔍 Localizando links...", end=" ", flush=True)
            
            # Buscar ELEMENTOS (não apenas URLs)
            script_busca = """
            let links = [];
            let elementos = document.querySelectorAll('a');
            elementos.forEach((a, index) => {
                let texto = a.textContent.toLowerCase();
                let href = a.href;
                
                if ((texto.includes('ofício') || texto.includes('requisitório') || 
                     texto.includes('or') || texto.includes('depre')) 
                    && href && href.length > 0 && !href.includes('javascript')) {
                    
                    // Marcar elemento com ID único
                    a.setAttribute('data-oficio-id', 'oficio_' + index);
                    
                    links.push({
                        id: 'oficio_' + index,
                        texto: a.textContent.trim()
                    });
                }
            });
            return links;
            """
            
            oficios_info = self.driver.execute_script(script_busca)
            
            if not oficios_info or len(oficios_info) == 0:
                print(f"⚠️  Nenhum ofício")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(oficios_info)} ofício(s)")
            
            baixados = 0
            
            for idx_of, info in enumerate(oficios_info, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_final = f"{nome_limpo}_oficio_{idx_of}.pdf"
                
                print(f"   📥 Baixando {idx_of}/{len(oficios_info)}...", end=" ", flush=True)
                
                try:
                    # Limpar pasta temp
                    self.limpar_pasta_temp()
                    
                    # Localizar e clicar no link
                    link_id = info['id']
                    link_elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-oficio-id='{link_id}']")
                    
                    # Clicar
                    link_elemento.click()
                    
                    # Aguardar download
                    if self.aguardar_download(timeout=15):
                        # Pegar arquivo baixado
                        pdfs = glob.glob(os.path.join(self.pasta_temp, "*.pdf"))
                        
                        if len(pdfs) > 0:
                            arquivo_temp = pdfs[0]
                            tamanho = os.path.getsize(arquivo_temp)
                            
                            # Validar PDF
                            with open(arquivo_temp, 'rb') as f:
                                primeiros_bytes = f.read(10)
                            
                            if primeiros_bytes.startswith(b'%PDF'):
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
                        print(f"❌ Sem download")
                    
                    # Voltar para página de requisitórios
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
            print(f"❌ Não encontrada")
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
        """Relatório final"""
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
        print(f"   📄 PDFs: {self.total_pdfs}")
        
        if total > 0:
            taxa = (len(self.sucessos) / total) * 100
            print(f"   📈 Taxa: {taxa:.1f}%")
        
        mins = int(duracao.total_seconds() / 60)
        segs = int(duracao.total_seconds() % 60)
        print(f"\n   ⏱️  Tempo: {mins}min {segs}s")
        
        pdfs_validos = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"\n📁 Destino: {os.path.abspath(self.pasta_oficios)}")
        print(f"📄 Arquivos: {len(pdfs_validos)} PDFs")
        
        # Limpar temp
        try:
            shutil.rmtree(self.pasta_temp)
        except:
            pass
        
        print("="*70)
    
    def executar(self):
        """Execução"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR - VERSÃO DEFINITIVA (CLIQUE NOS LINKS)")
        print("="*70)
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            print("\n❌ Nenhum processo!")
            return
        
        print(f"\n📋 Total: {len(processos)}")
        print(f"📁 Destino: {os.path.abspath(self.pasta_oficios)}")
        
        confirma = input(f"\n>>> Processar {len(processos)} processos? (s/n): ").lower()
        
        if confirma != 's':
            print("\n⚠️  Cancelado")
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            print("\n❌ Erro login")
            self.fechar()
            return
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficios_processo(numero, idx, len(processos))
            time.sleep(self.intervalo)
        
        self.gerar_relatorio(inicio)
        
        input("\n\n>>> ENTER para fechar &lt;&lt;&lt;\n")
    
    def fechar(self):
        """Fecha navegador"""
        if self.driver:
            self.driver.quit()
            print("\n✅ Fechado")

if __name__ == "__main__":
    buscador = BuscadorTJSP_CliqueLinks()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERROMPIDO")
    
    except Exception as e:
        print(f"\n\n❌ ERRO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
