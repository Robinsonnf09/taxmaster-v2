"""
BUSCADOR COM TRATAMENTO DE POPUP DE SENHA
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

try:
    import pikepdf
    PIKEPDF_DISPONIVEL = True
except:
    PIKEPDF_DISPONIVEL = False

class BuscadorTJSP_ComSenha:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = "oficios_COM_SENHA"
        self.planilha = "processos_TESTE_3.xlsx"
        
        # SENHA DO PROCESSO (configurar no .env ou deixar vazio)
        self.senha_processo = os.getenv("SENHA_PROCESSO", "")
        
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.pasta_downloads = "downloads_temp"
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        self.janela_principal = None
        self.total_pdfs_validos = 0
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = open(f"execucao_senha_{timestamp}.log", "w", encoding="utf-8")
    
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        linha = f"[{ts}] {msg}"
        self.log_file.write(linha + "\n")
        self.log_file.flush()
    
    def validar_pdf(self, caminho):
        """Validação"""
        try:
            with open(caminho, 'rb') as f:
                primeiros = f.read(10)
                tamanho = os.path.getsize(caminho)
            
            if not primeiros.startswith(b'%PDF'):
                return False, "Não é PDF"
            
            if tamanho < 1024:
                return False, f"Muito pequeno ({tamanho}b)"
            
            if PIKEPDF_DISPONIVEL:
                with pikepdf.open(caminho) as pdf:
                    num_pag = len(pdf.pages)
                    if num_pag == 0:
                        return False, "Sem páginas"
                    return True, f"{num_pag} pág(s), {tamanho//1024} KB"
            else:
                return True, f"{tamanho//1024} KB"
        
        except Exception as e:
            return False, str(e)
    
    def tratar_popup_senha(self, timeout=5):
        """Detecta e trata popup de senha"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            # Procurar pelo modal de senha
            # Título: "SENHA DO PROCESSO"
            try:
                modal_titulo = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'SENHA DO PROCESSO')]"))
                )
                
                print(f"\n      ⚠️  POPUP DE SENHA DETECTADO!")
                self.log("POPUP DE SENHA detectado")
                
                # Verificar se tem senha configurada
                if self.senha_processo and len(self.senha_processo) > 0:
                    print(f"      🔑 Preenchendo senha automática...")
                    self.log(f"Preenchendo senha: {self.senha_processo}")
                    
                    # Localizar campo de senha
                    campo_senha = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[type='text']")
                    campo_senha.clear()
                    campo_senha.send_keys(self.senha_processo)
                    
                    # Clicar em Continuar
                    botao_continuar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continuar')]")
                    botao_continuar.click()
                    
                    time.sleep(2)
                    
                    print(f"      ✅ Senha enviada")
                    self.log("Senha enviada - popup fechado")
                    
                    return True
                
                else:
                    print(f"      ❌ Senha não configurada no .env")
                    self.log("ERRO - Senha necessária mas não configurada")
                    
                    # Clicar em Cancelar
                    botao_cancelar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancelar')]")
                    botao_cancelar.click()
                    
                    return False
            
            except:
                # Não há popup de senha
                return None
        
        except:
            return None
    
    def iniciar_edge(self):
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
        
        print("✅ Edge iniciado!")
    
    def fazer_login_certificado(self):
        print(f"\n🔐 Login com Certificado...")
        
        self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        print(f"\n{'='*70}")
        print(f"🔐 SELECIONE SEU CERTIFICADO")
        print(f"{'='*70}")
        print(f"\n   📜 Serial: 24a59a14555d0e24")
        print(f"   ⏳ Aguardando 15 segundos...")
        
        time.sleep(15)
        
        print(f"\n✅ Login concluído!")
        return True
    
    def extrair_codigo_processo(self, numero_processo):
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
                return codigo
            
            return None
            
        except:
            return None
    
    def extrair_foro(self, numero_processo):
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def aguardar_download(self, timeout=20):
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            arquivos_temp = glob.glob(os.path.join(self.pasta_downloads, "*.crdownload"))
            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
            
            if len(arquivos_temp) == 0 and len(pdfs) > 0:
                time.sleep(1)
                return True
            
            time.sleep(0.5)
        
        return False
    
    def limpar_downloads(self):
        for arquivo in os.listdir(self.pasta_downloads):
            try:
                os.remove(os.path.join(self.pasta_downloads, arquivo))
            except:
                pass
    
    def buscar_oficios_processo(self, numero_processo, idx_proc, total_proc):
        """Processa processo com tratamento de popup de senha"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx_proc}/{total_proc}] {numero_processo}")
            print(f"{'='*70}")
            
            self.log(f"\nPROCESSO [{idx_proc}/{total_proc}]: {numero_processo}")
            
            # Buscar código
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
            
            print(f"   🎯 Acessando requisitórios...", end=" ", flush=True)
            self.driver.get(url_requisitorios)
            time.sleep(3)
            print(f"✅")
            
            # Buscar documentos
            print(f"   🔍 Localizando documentos...", end=" ", flush=True)
            
            script_busca = """
            let docs = [];
            document.querySelectorAll('a.linkMovVincProc').forEach((a, idx) => {
                let texto = a.textContent.trim();
                if (texto.includes('DEPRE') || texto.includes('Ofício') ||
                    texto.includes('Decisão') || texto.includes('Certidão') ||
                    texto.includes('OR ')) {
                    a.setAttribute('data-doc-id', 'doc_' + idx);
                    docs.push({id: 'doc_' + idx, texto: texto});
                }
            });
            return docs;
            """
            
            documentos = self.driver.execute_script(script_busca)
            
            if not documentos:
                print(f"⚠️  Nenhum")
                return False
            
            print(f"✅ {len(documentos)}")
            
            # PROCESSAR APENAS PRIMEIRO DOCUMENTO (TESTE)
            doc = documentos[0]
            
            print(f"\n   📥 Testando: {doc['texto'][:50]}...")
            
            try:
                self.limpar_downloads()
                
                # Localizar e clicar
                elemento = self.driver.find_element(By.CSS_SELECTOR, f"a[data-doc-id='{doc['id']}']")
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                time.sleep(1)
                
                janelas_antes = len(self.driver.window_handles)
                
                # Clique real
                print(f"      👆 Clicando...", end=" ", flush=True)
                actions = ActionChains(self.driver)
                actions.move_to_element(elemento).pause(0.5).click().perform()
                print(f"✅")
                
                time.sleep(3)
                
                # VERIFICAR SE APARECEU POPUP DE SENHA
                resultado_senha = self.tratar_popup_senha(timeout=3)
                
                if resultado_senha == False:
                    # Senha necessária mas não foi fornecida
                    print(f"      ❌ Cancelado (sem senha)")
                    return False
                
                elif resultado_senha == True:
                    # Senha preenchida com sucesso
                    time.sleep(2)
                
                # Verificar se abriu nova aba
                janelas_depois = len(self.driver.window_handles)
                
                if janelas_depois > janelas_antes:
                    print(f"      ✅ Nova aba aberta")
                    
                    nova_aba = self.driver.window_handles[-1]
                    self.driver.switch_to.window(nova_aba)
                    
                    url_aba = self.driver.current_url
                    print(f"      📍 URL: {url_aba[:60]}...")
                    
                    # Screenshot
                    self.driver.save_screenshot("screenshot_aba_doc.png")
                    
                    # Aguardar download
                    print(f"      ⏳ Aguardando download (15s)...", end=" ", flush=True)
                    
                    if self.aguardar_download(timeout=15):
                        print(f"✅")
                        
                        pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                        
                        if pdfs:
                            arquivo = pdfs[0]
                            
                            valido, info = self.validar_pdf(arquivo)
                            
                            if valido:
                                nome_final = f"teste_doc_1.pdf"
                                destino = os.path.join(self.pasta_oficios, nome_final)
                                shutil.move(arquivo, destino)
                                
                                print(f"      ✅ PDF VÁLIDO salvo! {info}")
                                self.total_pdfs_validos += 1
                            else:
                                print(f"      ❌ PDF inválido: {info}")
                    else:
                        print(f"❌")
                    
                    # Fechar aba
                    self.driver.close()
                    self.driver.switch_to.window(self.janela_principal)
                
                else:
                    print(f"      ❌ Nenhuma aba aberta")
            
            except Exception as e:
                print(f"      ❌ Erro: {str(e)}")
                
                try:
                    self.driver.switch_to.window(self.janela_principal)
                except:
                    pass
            
            return False
            
        except Exception as e:
            return False
    
    def carregar_processos(self):
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
        print("\n" + "="*70)
        print("🔍 TESTE COM TRATAMENTO DE POPUP DE SENHA")
        print("="*70)
        
        if self.senha_processo:
            print(f"\n🔑 Senha configurada: {'*' * len(self.senha_processo)}")
        else:
            print(f"\n⚠️  SENHA NÃO CONFIGURADA - popup será cancelado")
        
        processos = self.carregar_processos()
        
        if not processos:
            return
        
        print(f"\n📋 Testará primeiro documento do primeiro processo")
        
        confirma = input(f"\n>>> Iniciar? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            self.fechar()
            return
        
        self.buscar_oficios_processo(processos[0], 1, 1)
        
        print(f"\n{'='*70}")
        print(f"📊 RESULTADO:")
        print(f"   ✅ PDFs válidos: {self.total_pdfs_validos}")
        print(f"📁 Pasta: {os.path.abspath(self.pasta_oficios)}")
        print(f"📄 Log: execucao_senha_*.log")
        print(f"={'='*70}")
        
        input("\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
        if self.log_file:
            self.log_file.close()

if __name__ == "__main__":
    buscador = BuscadorTJSP_ComSenha()
    
    try:
        buscador.executar()
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
