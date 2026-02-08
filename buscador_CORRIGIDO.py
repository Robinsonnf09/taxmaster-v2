"""
BUSCADOR CORRIGIDO - DOWNLOAD DIRETO VIA SELENIUM
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

class BuscadorTJSP_DownloadCorreto:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.usar_certificado = os.getenv("USAR_CERTIFICADO", "True").lower() == "true"
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_requisitorios_tjsp")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Criar pasta temporária de downloads
        self.pasta_temp_downloads = os.path.join(os.getcwd(), "downloads_temp")
        if os.path.exists(self.pasta_temp_downloads):
            shutil.rmtree(self.pasta_temp_downloads)
        os.makedirs(self.pasta_temp_downloads)
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
    
    def iniciar_edge(self):
        """Inicia Edge com download automático configurado"""
        print("\n🔷 Iniciando Microsoft Edge com download automático...")
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--ignore-certificate-errors')
        
        # Configurações críticas de download
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_temp_downloads),
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
        print(f"📁 Downloads temporários: {self.pasta_temp_downloads}")
        print(f"📁 Destino final: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login_certificado(self):
        """Login com certificado"""
        print(f"\n🔐 Fazendo login com Certificado Digital...")
        
        try:
            print(f"   🌐 Acessando e-SAJ...")
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(3)
            
            print(f"\n{'='*70}")
            print(f"🔐 SELECIONE SEU CERTIFICADO NO POPUP DO WINDOWS")
            print(f"{'='*70}")
            print(f"\n   📜 Serial: 24a59a14555d0e24")
            print(f"   ⏳ Aguardando 15 segundos...")
            
            time.sleep(15)
            
            url_atual = self.driver.current_url
            
            if "login" in url_atual.lower():
                time.sleep(10)
                url_atual = self.driver.current_url
            
            if "login" not in url_atual.lower():
                print(f"\n🎉 LOGIN REALIZADO!")
                return True
            else:
                print(f"\n⚠️  Login em andamento, continuando...")
                return True
                
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")
            return False
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca processo e extrai código"""
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
            time.sleep(0.2)
            campo.send_keys(numero_processo)
            time.sleep(0.3)
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
        """Extrai foro do processo"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def aguardar_download_completo(self, timeout=30):
        """Aguarda download finalizar"""
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            # Verificar se há arquivos .crdownload (download em andamento)
            arquivos_temp = [f for f in os.listdir(self.pasta_temp_downloads) if f.endswith('.crdownload') or f.endswith('.tmp')]
            
            if len(arquivos_temp) == 0:
                # Verificar se tem PDF novo
                pdfs = [f for f in os.listdir(self.pasta_temp_downloads) if f.endswith('.pdf')]
                if len(pdfs) > 0:
                    time.sleep(0.5)  # Aguardar finalizar gravação
                    return True
            
            time.sleep(0.3)
        
        return False
    
    def baixar_pdf_selenium(self, url_pdf, nome_final):
        """Baixa PDF usando Selenium (clique direto)"""
        try:
            # Limpar pasta temporária
            for arquivo in os.listdir(self.pasta_temp_downloads):
                caminho = os.path.join(self.pasta_temp_downloads, arquivo)
                try:
                    os.remove(caminho)
                except:
                    pass
            
            # Navegar diretamente para URL do PDF
            self.driver.get(url_pdf)
            
            # Aguardar download
            if self.aguardar_download_completo(timeout=15):
                # Pegar arquivo baixado
                pdfs = [f for f in os.listdir(self.pasta_temp_downloads) if f.endswith('.pdf')]
                
                if len(pdfs) > 0:
                    arquivo_temp = os.path.join(self.pasta_temp_downloads, pdfs[0])
                    tamanho = os.path.getsize(arquivo_temp)
                    
                    # Verificar se é PDF válido
                    with open(arquivo_temp, 'rb') as f:
                        primeiros_bytes = f.read(10)
                    
                    if primeiros_bytes.startswith(b'%PDF'):
                        # Mover para pasta final
                        destino = os.path.join(self.pasta_oficios, nome_final)
                        shutil.move(arquivo_temp, destino)
                        return True, tamanho
                    else:
                        # Arquivo não é PDF (pode ser HTML de erro)
                        return False, 0
            
            return False, 0
            
        except Exception as e:
            return False, 0
    
    def buscar_oficios_processo(self, numero_processo, idx, total):
        """Processa processo completo"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            print(f"   🔍 Buscando código...", end=" ", flush=True)
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"❌ Processo não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            print(f"✅ Código: {codigo}")
            
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
            
            print(f"   🔍 Localizando ofícios...", end=" ", flush=True)
            
            script_busca = """
            let links = [];
            document.querySelectorAll('a').forEach(a => {
                let texto = a.textContent.toLowerCase();
                let href = a.href;
                
                if ((texto.includes('ofício') || texto.includes('requisitório') || 
                     texto.includes('or') || texto.includes('depre')) 
                    && href && href.length > 0 && !href.includes('javascript')) {
                    links.push({
                        url: href,
                        texto: a.textContent.trim()
                    });
                }
            });
            return links;
            """
            
            oficios = self.driver.execute_script(script_busca)
            
            if not oficios or len(oficios) == 0:
                print(f"⚠️  Nenhum ofício encontrado")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(oficios)} ofício(s) encontrado(s)")
            
            baixados = 0
            
            for idx_of, oficio in enumerate(oficios, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_arquivo = f"{nome_limpo}_oficio_{idx_of}.pdf"
                
                print(f"   📥 Baixando {idx_of}/{len(oficios)}...", end=" ", flush=True)
                
                sucesso, tamanho = self.baixar_pdf_selenium(oficio['url'], nome_arquivo)
                
                if sucesso:
                    kb = tamanho // 1024
                    print(f"✅ {kb} KB")
                    baixados += 1
                    self.total_pdfs += 1
                else:
                    print(f"❌ Falha")
            
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
        """Carrega processos da planilha"""
        print(f"\n📊 Carregando planilha: {self.planilha}")
        
        caminho_completo = os.path.join(os.getcwd(), self.planilha)
        
        if not os.path.exists(caminho_completo):
            print(f"❌ Planilha não encontrada: {caminho_completo}")
            return []
        
        wb = openpyxl.load_workbook(caminho_completo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    processos.append(num)
        
        wb.close()
        
        print(f"✅ {len(processos)} processos carregados")
        return processos
    
    def gerar_relatorio_final(self, inicio):
        """Gera relatório final"""
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("🎉 EXECUÇÃO CONCLUÍDA!")
        print("="*70)
        
        total = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total processado: {total}")
        print(f"   ✅ Com ofício baixado: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício disponível: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas/Erros: {len(self.falhas)}")
        print(f"   📄 Total de PDFs baixados: {self.total_pdfs}")
        
        if total > 0:
            taxa_sucesso = (len(self.sucessos) / total) * 100
            print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        minutos = int(duracao.total_seconds() / 60)
        segundos = int(duracao.total_seconds() % 60)
        print(f"\n   ⏱️  Tempo total: {minutos}min {segundos}s")
        
        pdfs = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"\n📁 Pasta de destino: {os.path.abspath(self.pasta_oficios)}")
        print(f"📄 Total de arquivos PDF: {len(pdfs)}")
        
        # Limpar pasta temporária
        try:
            shutil.rmtree(self.pasta_temp_downloads)
            print(f"🗑️  Pasta temporária removida")
        except:
            pass
        
        print("="*70)
    
    def executar(self):
        """Execução principal"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print("   🔐 DOWNLOAD CORRIGIDO VIA SELENIUM")
        print("="*70)
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            print("\n❌ Nenhum processo encontrado!")
            return
        
        print(f"\n📋 Total de processos: {len(processos)}")
        print(f"📁 Destino dos PDFs: {os.path.abspath(self.pasta_oficios)}")
        
        confirma = input(f"\n>>> Iniciar busca de {len(processos)} processos? (s/n): ").lower()
        
        if confirma != 's':
            print("\n⚠️  Execução cancelada")
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            print("\n❌ Erro no login")
            self.fechar()
            return
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficios_processo(numero, idx, len(processos))
            time.sleep(self.intervalo)
        
        self.gerar_relatorio_final(inicio)
        
        input("\n\n>>> Pressione ENTER para fechar <<<\n")
    
    def fechar(self):
        """Fecha navegador"""
        if self.driver:
            self.driver.quit()
            print("\n✅ Navegador fechado")

if __name__ == "__main__":
    buscador = BuscadorTJSP_DownloadCorreto()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERROMPIDO")
    
    except Exception as e:
        print(f"\n\n❌ ERRO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
