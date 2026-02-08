"""
═══════════════════════════════════════════════════════════════════════
BUSCADOR DE OFÍCIOS REQUISITÓRIOS TJSP - VERSÃO FINAL COMPLETA
═══════════════════════════════════════════════════════════════════════
Características:
✅ Validação robusta com pikepdf (2 camadas)
✅ Clique real via ActionChains (sem erro de JavaScript)
✅ Log detalhado de cada operação
✅ Tratamento de erros específico por tipo
✅ Validação de PDFs antes de salvar
✅ Relatório completo ao final
═══════════════════════════════════════════════════════════════════════
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

# Tentar importar pikepdf
try:
    import pikepdf
    PIKEPDF_DISPONIVEL = True
except ImportError:
    PIKEPDF_DISPONIVEL = False
    print("⚠️  pikepdf não instalado - usando validação básica")

class BuscadorTJSP_Final:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        # Configurações
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_REQUISITORIOS_FINAL")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Criar pastas limpas
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.pasta_downloads = "downloads_temporarios"
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        # Controle
        self.janela_principal = None
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs_validos = 0
        self.total_pdfs_invalidos = 0
        
        # Log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = open(f"execucao_{timestamp}.log", "w", encoding="utf-8")
    
    def log(self, msg, nivel="INFO"):
        """Log com timestamp e nível"""
        ts = datetime.now().strftime("%H:%M:%S")
        linha = f"[{ts}] [{nivel}] {msg}"
        self.log_file.write(linha + "\n")
        self.log_file.flush()
    
    def validar_pdf(self, caminho_arquivo):
        """Valida PDF com pikepdf (se disponível) ou método básico"""
        
        # CAMADA 1: Magic bytes (sempre)
        try:
            with open(caminho_arquivo, 'rb') as f:
                primeiros = f.read(10)
                tamanho = os.path.getsize(caminho_arquivo)
            
            if not primeiros.startswith(b'%PDF'):
                self.log(f"Validação FALHOU - Magic bytes: {primeiros[:20]}", "WARN")
                return False, "Não é PDF (magic bytes incorreto)"
            
            # Se arquivo muito pequeno (< 1KB), provavelmente é HTML
            if tamanho < 1024:
                self.log(f"Validação FALHOU - Arquivo muito pequeno: {tamanho} bytes", "WARN")
                return False, f"Arquivo muito pequeno ({tamanho} bytes)"
        
        except Exception as e:
            return False, f"Erro leitura: {str(e)}"
        
        # CAMADA 2: pikepdf (se disponível)
        if PIKEPDF_DISPONIVEL:
            try:
                with pikepdf.open(caminho_arquivo) as pdf:
                    num_paginas = len(pdf.pages)
                    
                    if num_paginas == 0:
                        return False, "PDF sem páginas"
                    
                    self.log(f"Validação PIKEPDF - OK: {num_paginas} página(s), {tamanho} bytes", "SUCCESS")
                    return True, f"{num_paginas} pág(s), {tamanho//1024} KB"
            
            except pikepdf.PasswordError:
                return False, "PDF protegido por senha"
            
            except pikepdf.PdfError as e:
                self.log(f"Validação PIKEPDF - ERRO: {str(e)}", "ERROR")
                return False, "PDF corrompido"
            
            except Exception as e:
                return False, f"Erro pikepdf: {str(e)}"
        
        else:
            # Validação básica sem pikepdf
            self.log(f"Validação BÁSICA - OK: {tamanho} bytes", "INFO")
            return True, f"{tamanho//1024} KB (validação básica)"
    
    def iniciar_edge(self):
        """Inicia Edge"""
        print("\n🔷 Iniciando Microsoft Edge...")
        self.log("Iniciando Edge", "INFO")
        
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
        
        self.log(f"Edge iniciado - Handle: {self.janela_principal}", "SUCCESS")
        print("✅ Edge iniciado com sucesso!")
        print(f"📁 Pasta de destino: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login_certificado(self):
        """Login com certificado"""
        print(f"\n🔐 Fazendo login com Certificado Digital...")
        self.log("Login - Acessando e-SAJ", "INFO")
        
        self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        self.log(f"Login - URL inicial: {self.driver.current_url}", "INFO")
        
        print(f"\n{'='*70}")
        print(f"🔐 POPUP DE CERTIFICADO DIGITAL")
        print(f"{'='*70}")
        print(f"\n   📜 Selecione o certificado:")
        print(f"      Serial: 24a59a14555d0e24")
        print(f"      e-CPF A3 CERTDATA")
        print(f"\n   ⏳ Aguardando 15 segundos...")
        
        time.sleep(15)
        
        url_final = self.driver.current_url
        self.log(f"Login - URL após certificado: {url_final}", "INFO")
        
        print(f"\n✅ Login concluído!")
        return True
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca processo e extrai código interno"""
        try:
            self.log(f"Buscando processo: {numero_processo}", "INFO")
            
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Clicar em "Número Antigo"
            try:
                radio = wait.until(EC.element_to_be_clickable((By.ID, "radioNumeroAntigo")))
                radio.click()
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Não encontrou rádio 'Número Antigo': {str(e)}", "WARN")
            
            # Digitar número do processo
            try:
                campo = wait.until(EC.visibility_of_element_located((By.ID, "nuProcessoAntigoFormatado")))
            except Exception as e:
                self.log(f"ERRO - Campo de busca não encontrado: {str(e)}", "ERROR")
                return None
            
            campo.clear()
            campo.send_keys(numero_processo)
            campo.send_keys(Keys.RETURN)
            
            time.sleep(2.5)
            
            # Extrair código da URL
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                self.log(f"Código encontrado: {codigo}", "SUCCESS")
                return codigo
            
            self.log(f"Código NÃO encontrado na URL: {url_atual}", "WARN")
            return None
            
        except Exception as e:
            self.log(f"ERRO ao buscar processo: {str(e)}", "ERROR")
            return None
    
    def extrair_foro(self, numero_processo):
        """Extrai código do foro do número do processo"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def aguardar_download(self, timeout=20):
        """Aguarda download completar"""
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            # Verificar arquivos temporários
            arquivos_temp = glob.glob(os.path.join(self.pasta_downloads, "*.crdownload"))
            arquivos_temp += glob.glob(os.path.join(self.pasta_downloads, "*.tmp"))
            
            # Verificar PDFs
            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
            
            # Se não há temporários E há PDFs = download completo
            if len(arquivos_temp) == 0 and len(pdfs) > 0:
                time.sleep(1)  # Aguardar finalização da gravação
                return True
            
            time.sleep(0.5)
        
        return False
    
    def limpar_downloads(self):
        """Limpa pasta de downloads temporários"""
        for arquivo in os.listdir(self.pasta_downloads):
            caminho = os.path.join(self.pasta_downloads, arquivo)
            try:
                os.remove(caminho)
            except:
                pass
    
    def buscar_oficios_processo(self, numero_processo, idx_proc, total_proc):
        """Processa um processo completo"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ PROCESSO [{idx_proc}/{total_proc}] - {numero_processo}")
            print(f"{'='*70}")
            
            self.log(f"\n{'='*70}", "INFO")
            self.log(f"PROCESSO [{idx_proc}/{total_proc}]: {numero_processo}", "INFO")
            self.log(f"{'='*70}", "INFO")
            
            # 1. Buscar código
            print(f"   🔍 Buscando código do processo...", end=" ", flush=True)
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"❌ Não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            print(f"✅ {codigo}")
            
            # 2. Montar URL de requisitórios
            foro = self.extrair_foro(numero_processo)
            
            url_requisitorios = (
                f"https://esaj.tjsp.jus.br/cpopg/show.do?"
                f"processo.codigo={codigo}&"
                f"processo.foro={foro}&"
                f"processo.numero={numero_processo}&"
                f"consultaDeRequisitorios=true"
            )
            
            self.log(f"URL Requisitórios: {url_requisitorios}", "INFO")
            
            # 3. Acessar página de requisitórios
            print(f"   🎯 Acessando página de requisitórios...", end=" ", flush=True)
            self.driver.get(url_requisitorios)
            time.sleep(3)
            print(f"✅")
            
            # 4. Buscar documentos
            print(f"   🔍 Localizando documentos...", end=" ", flush=True)
            
            script_busca = """
            let docs = [];
            
            document.querySelectorAll('a.linkMovVincProc').forEach((a, idx) => {
                let texto = a.textContent.trim();
                
                // Filtrar apenas documentos relevantes
                if (texto.includes('DEPRE') || texto.includes('Ofício') ||
                    texto.includes('Decisão') || texto.includes('Certidão') ||
                    texto.includes('OR ')) {
                    
                    a.setAttribute('data-doc-id', 'doc_' + idx);
                    
                    docs.push({
                        id: 'doc_' + idx,
                        texto: texto,
                        onclick: a.getAttribute('onclick')
                    });
                }
            });
            
            return docs;
            """
            
            documentos = self.driver.execute_script(script_busca)
            
            if not documentos or len(documentos) == 0:
                print(f"⚠️  Nenhum documento encontrado")
                self.log("Nenhum documento encontrado", "WARN")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(documentos)} documento(s)")
            self.log(f"Documentos encontrados: {len(documentos)}", "INFO")
            
            # 5. Processar cada documento
            baixados = 0
            
            for idx_doc, doc in enumerate(documentos, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_final = f"{nome_limpo}_doc_{idx_doc}.pdf"
                
                print(f"   📥 [{idx_doc}/{len(documentos)}] {doc['texto'][:40]}...", end=" ", flush=True)
                self.log(f"Processando doc {idx_doc}: {doc['texto']}", "INFO")
                
                try:
                    # Limpar downloads
                    self.limpar_downloads()
                    
                    # Localizar elemento
                    elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-doc-id='{doc['id']}']")
                    
                    # Scroll até elemento
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                    time.sleep(0.8)
                    
                    # Contar janelas antes
                    janelas_antes = len(self.driver.window_handles)
                    
                    # CLIQUE REAL via ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(elemento).pause(0.5).click().perform()
                    
                    # Aguardar nova aba
                    time.sleep(3)
                    
                    janelas_depois = len(self.driver.window_handles)
                    
                    if janelas_depois > janelas_antes:
                        # Nova aba aberta
                        nova_aba = self.driver.window_handles[-1]
                        self.driver.switch_to.window(nova_aba)
                        
                        url_aba = self.driver.current_url
                        self.log(f"Nova aba aberta: {url_aba}", "INFO")
                        
                        # Aguardar download
                        if self.aguardar_download(timeout=12):
                            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                            
                            if pdfs:
                                arquivo_temp = pdfs[0]
                                
                                # VALIDAÇÃO ROBUSTA
                                valido, info = self.validar_pdf(arquivo_temp)
                                
                                if valido:
                                    # Mover para pasta final
                                    destino = os.path.join(self.pasta_oficios, nome_final)
                                    shutil.move(arquivo_temp, destino)
                                    
                                    print(f"✅ {info}")
                                    self.log(f"PDF válido salvo: {nome_final} - {info}", "SUCCESS")
                                    
                                    baixados += 1
                                    self.total_pdfs_validos += 1
                                else:
                                    print(f"❌ Inválido: {info}")
                                    self.log(f"PDF inválido rejeitado: {info}", "WARN")
                                    self.total_pdfs_invalidos += 1
                            else:
                                print(f"❌ Sem arquivo")
                                self.log("Download OK mas nenhum PDF encontrado", "WARN")
                        else:
                            print(f"❌ Timeout DL")
                            self.log("Timeout aguardando download", "WARN")
                        
                        # Fechar aba
                        self.driver.close()
                        self.driver.switch_to.window(self.janela_principal)
                    
                    else:
                        print(f"❌ Sem aba nova")
                        self.log("Clique não abriu nova aba", "WARN")
                    
                    # Voltar para página de requisitórios
                    self.driver.get(url_requisitorios)
                    time.sleep(1.2)
                
                except Exception as e:
                    print(f"❌ Erro: {type(e).__name__}")
                    self.log(f"ERRO no documento {idx_doc}: {traceback.format_exc()}", "ERROR")
                    
                    # Garantir retorno
                    try:
                        self.driver.switch_to.window(self.janela_principal)
                        self.driver.get(url_requisitorios)
                        time.sleep(1)
                    except:
                        pass
            
            # Classificar resultado
            if baixados > 0:
                self.sucessos.append(numero_processo)
                return True
            else:
                self.falhas.append(numero_processo)
                return False
            
        except Exception as e:
            print(f"\n   ❌ ERRO GERAL: {str(e)}")
            self.log(f"ERRO GERAL no processo: {traceback.format_exc()}", "ERROR")
            self.falhas.append(numero_processo)
            return False
    
    def carregar_processos_planilha(self):
        """Carrega números de processos da planilha"""
        print(f"\n📊 Carregando planilha: {self.planilha}")
        
        caminho = os.path.join(os.getcwd(), self.planilha)
        
        if not os.path.exists(caminho):
            print(f"❌ Planilha não encontrada: {caminho}")
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
        
        print(f"✅ {len(processos)} processos carregados")
        self.log(f"Planilha carregada: {len(processos)} processos", "INFO")
        
        return processos
    
    def gerar_relatorio_final(self, inicio):
        """Gera relatório completo da execução"""
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("🎉 EXECUÇÃO CONCLUÍDA!")
        print("="*70)
        
        total = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   Total de processos: {total}")
        print(f"   ✅ Com ofício baixado: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício disponível: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas/Erros: {len(self.falhas)}")
        
        print(f"\n📄 ESTATÍSTICAS DE PDFs:")
        print(f"   ✅ PDFs VÁLIDOS: {self.total_pdfs_validos}")
        print(f"   ❌ PDFs INVÁLIDOS (rejeitados): {self.total_pdfs_invalidos}")
        
        if total > 0:
            taxa_sucesso = (len(self.sucessos) / total) * 100
            print(f"\n   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        minutos = int(duracao.total_seconds() / 60)
        segundos = int(duracao.total_seconds() % 60)
        print(f"   ⏱️  Tempo total: {minutos}min {segundos}s")
        
        # Verificar arquivos salvos
        arquivos_salvos = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        
        print(f"\n📁 PASTA DE DESTINO:")
        print(f"   {os.path.abspath(self.pasta_oficios)}")
        print(f"   📄 Total de arquivos: {len(arquivos_salvos)}")
        
        # Processos com falha
        if len(self.falhas) > 0:
            print(f"\n❌ PROCESSOS COM FALHA:")
            for proc in self.falhas:
                print(f"   • {proc}")
        
        # Processos sem ofício
        if len(self.sem_oficio) > 0:
            print(f"\n⚠️  PROCESSOS SEM OFÍCIO:")
            for proc in self.sem_oficio:
                print(f"   • {proc}")
        
        # Limpar pasta temporária
        try:
            shutil.rmtree(self.pasta_downloads)
            print(f"\n🗑️  Pasta temporária removida")
        except:
            pass
        
        print("="*70)
        
        self.log(f"\n{'='*70}", "INFO")
        self.log("RELATÓRIO FINAL", "INFO")
        self.log(f"{'='*70}", "INFO")
        self.log(f"Total processos: {total}", "INFO")
        self.log(f"Sucessos: {len(self.sucessos)}", "INFO")
        self.log(f"Sem ofício: {len(self.sem_oficio)}", "INFO")
        self.log(f"Falhas: {len(self.falhas)}", "INFO")
        self.log(f"PDFs válidos: {self.total_pdfs_validos}", "SUCCESS")
        self.log(f"PDFs inválidos: {self.total_pdfs_invalidos}", "WARN")
        self.log(f"Tempo: {minutos}min {segundos}s", "INFO")
    
    def executar(self):
        """Método principal de execução"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print("   🔐 CERTIFICADO DIGITAL A3")
        print("   ✅ VALIDAÇÃO ROBUSTA COM PIKEPDF")
        print("="*70)
        
        self.log("="*70, "INFO")
        self.log("INÍCIO DA EXECUÇÃO", "INFO")
        self.log(f"pikepdf disponível: {PIKEPDF_DISPONIVEL}", "INFO")
        self.log("="*70, "INFO")
        
        # Carregar processos
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            print("\n❌ Nenhum processo encontrado na planilha!")
            return
        
        print(f"\n📋 Total de processos a processar: {len(processos)}")
        print(f"📁 Destino dos PDFs: {os.path.abspath(self.pasta_oficios)}")
        
        # Confirmação
        confirma = input(f"\n>>> Iniciar busca de {len(processos)} processos? (s/n): ").lower()
        
        if confirma != 's':
            print("\n⚠️  Execução cancelada pelo usuário")
            return
        
        # Iniciar Edge
        self.iniciar_edge()
        
        # Login
        if not self.fazer_login_certificado():
            print("\n❌ Erro no login. Encerrando.")
            self.fechar()
            return
        
        # Processar todos os processos
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficios_processo(numero, idx, len(processos))
            time.sleep(self.intervalo)
        
        # Relatório final
        self.gerar_relatorio_final(inicio)
        
        input("\n\n>>> Pressione ENTER para fechar o navegador <<<\n")
    
    def fechar(self):
        """Fecha navegador e arquivos"""
        if self.driver:
            self.driver.quit()
            print("\n✅ Navegador fechado")
        
        if self.log_file:
            self.log_file.close()

# ═══════════════════════════════════════════════════════════════════════
# EXECUÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    buscador = BuscadorTJSP_Final()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  EXECUÇÃO INTERROMPIDA PELO USUÁRIO")
        buscador.log("Execução interrompida (Ctrl+C)", "WARN")
    
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {str(e)}")
        print(f"\n🔍 Traceback completo:")
        traceback.print_exc()
        
        buscador.log(f"ERRO CRÍTICO: {traceback.format_exc()}", "ERROR")
    
    finally:
        buscador.fechar()
    
    print("\n✅ SISTEMA ENCERRADO\n")
