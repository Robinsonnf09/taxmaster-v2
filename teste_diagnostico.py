"""
SOLUÇÃO FINAL - MÚLTIPLAS ABORDAGENS DE DOWNLOAD
Testa diferentes métodos até encontrar um que funcione
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import openpyxl
from datetime import datetime
from dotenv import load_dotenv
import shutil
import glob
import base64

class BuscadorTJSP_MultiplasAbordagens:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_requisitorios_tjsp_VALIDOS")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Limpar pasta de destino
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
        
        # Janela principal
        self.janela_principal = None
    
    def iniciar_edge(self):
        """Inicia Edge"""
        print("\n🔷 Iniciando Edge...")
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        
        self.driver = webdriver.Edge(options=options)
        self.janela_principal = self.driver.current_window_handle
        
        print("✅ Edge iniciado!")
    
    def fazer_login_certificado(self):
        """Login com certificado"""
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
    
    def baixar_pdf_metodo_multiplo(self, link_elemento, nome_arquivo, idx_oficio):
        """Tenta múltiplos métodos para baixar o PDF"""
        
        try:
            # MÉTODO 1: Clicar com botão direito + Salvar como
            print(f"M1...", end="", flush=True)
            
            actions = ActionChains(self.driver)
            actions.context_click(link_elemento).perform()
            time.sleep(1)
            
            # Tentar encontrar "Salvar como" no menu de contexto
            # (Não funciona via Selenium - pular para método 2)
            
        except:
            pass
        
        try:
            # MÉTODO 2: Abrir em nova aba e capturar conteúdo
            print(f"M2...", end="", flush=True)
            
            # Pegar URL do link
            url_pdf = link_elemento.get_attribute('href')
            
            if not url_pdf or 'javascript' in url_pdf:
                return False, 0
            
            # Abrir em nova aba
            self.driver.execute_script("window.open(arguments[0], '_blank');", url_pdf)
            time.sleep(2)
            
            # Mudar para nova aba
            abas = self.driver.window_handles
            if len(abas) > 1:
                self.driver.switch_to.window(abas[-1])
                time.sleep(2)
                
                # Tentar capturar PDF via JavaScript
                try:
                    script_captura = """
                    async function capturarPDF() {
                        // Verificar se é iframe com PDF
                        let iframe = document.querySelector('iframe');
                        if (iframe) {
                            return {tipo: 'iframe', src: iframe.src};
                        }
                        
                        // Verificar se tem embed
                        let embed = document.querySelector('embed[type="application/pdf"]');
                        if (embed) {
                            return {tipo: 'embed', src: embed.src};
                        }
                        
                        // Verificar se é visualizador do Chrome
                        let url = window.location.href;
                        if (url.includes('.pdf')) {
                            return {tipo: 'direct', src: url};
                        }
                        
                        return {tipo: 'desconhecido'};
                    }
                    return await capturarPDF();
                    """
                    
                    resultado = self.driver.execute_script(script_captura)
                    
                    if resultado and resultado.get('src'):
                        # Tentar trigger download via JavaScript
                        script_download = f"""
                        let link = document.createElement('a');
                        link.href = '{resultado["src"]}';
                        link.download = '{nome_arquivo}';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        """
                        
                        self.driver.execute_script(script_download)
                        time.sleep(3)
                    
                except Exception as e:
                    pass
                
                # Fechar aba
                self.driver.close()
                self.driver.switch_to.window(self.janela_principal)
                
                return False, 0
            
        except Exception as e:
            # Garantir que voltou para janela principal
            try:
                self.driver.switch_to.window(self.janela_principal)
            except:
                pass
            
            return False, 0
        
        return False, 0
    
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
        """Processa processo - TESTE APENAS PRIMEIRO OFÍCIO"""
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
            
            # Tirar screenshot da página para análise
            screenshot_nome = f"pagina_requisitorios_{numero_processo.replace('-','').replace('.','')}.png"
            self.driver.save_screenshot(screenshot_nome)
            print(f"   📸 Screenshot: {screenshot_nome}")
            
            print(f"   🔍 Localizando links...", end=" ", flush=True)
            
            # Buscar links e mostrar informações detalhadas
            script_detalhado = """
            let links = [];
            document.querySelectorAll('a').forEach((a, index) => {
                let texto = a.textContent.toLowerCase();
                let href = a.href;
                
                if ((texto.includes('ofício') || texto.includes('requisitório') || 
                     texto.includes('or') || texto.includes('depre')) 
                    && href && href.length > 0 && !href.includes('javascript')) {
                    
                    a.setAttribute('data-oficio-idx', index);
                    
                    links.push({
                        index: index,
                        texto: a.textContent.trim(),
                        href: href,
                        target: a.getAttribute('target'),
                        onclick: a.getAttribute('onclick')
                    });
                }
            });
            return links;
            """
            
            oficios = self.driver.execute_script(script_detalhado)
            
            if not oficios or len(oficios) == 0:
                print(f"⚠️  Nenhum")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(oficios)}")
            
            # TESTAR APENAS O PRIMEIRO OFÍCIO
            if len(oficios) > 0:
                print(f"\n   🔍 TESTANDO PRIMEIRO OFÍCIO:")
                oficio = oficios[0]
                
                print(f"      Texto: {oficio['texto']}")
                print(f"      URL: {oficio['href'][:80]}...")
                print(f"      Target: {oficio['target']}")
                print(f"      onClick: {oficio['onclick']}")
                
                # Tentar clicar
                try:
                    link_elem = self.driver.find_element(By.CSS_SELECTOR, f"a[data-oficio-idx='{oficio['index']}']")
                    
                    print(f"\n      💡 Clicando no link...")
                    link_elem.click()
                    time.sleep(5)
                    
                    # Verificar se abriu nova aba
                    abas = self.driver.window_handles
                    print(f"      📊 Total de abas: {len(abas)}")
                    
                    if len(abas) > 1:
                        print(f"      ✅ Nova aba detectada!")
                        self.driver.switch_to.window(abas[-1])
                        
                        url_nova_aba = self.driver.current_url
                        print(f"      📍 URL da nova aba: {url_nova_aba[:80]}...")
                        
                        # Screenshot da nova aba
                        screenshot_aba = f"aba_oficio_{numero_processo.replace('-','').replace('.','')}_1.png"
                        self.driver.save_screenshot(screenshot_aba)
                        print(f"      📸 Screenshot da aba: {screenshot_aba}")
                        
                        # Fechar aba
                        self.driver.close()
                        self.driver.switch_to.window(self.janela_principal)
                    else:
                        print(f"      ⚠️  Mesma aba - link pode ter falhado")
                    
                except Exception as e:
                    print(f"      ❌ Erro ao clicar: {str(e)}")
            
            # Parar após primeiro processo para análise
            input("\n\n>>> ENTER para continuar com próximo processo <<<\n")
            
            return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
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
    
    def executar(self):
        """Execução"""
        print("\n" + "="*70)
        print("🔍 MODO DIAGNÓSTICO - TESTE DE MÉTODOS DE DOWNLOAD")
        print("="*70)
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            return
        
        print(f"\n📋 Vamos testar com 1 processo primeiro")
        
        confirma = input(f"\n>>> Iniciar teste? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            self.fechar()
            return
        
        # Processar APENAS o primeiro
        self.buscar_oficios_processo(processos[0], 1, 1)
        
        input("\n\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        """Fecha navegador"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    buscador = BuscadorTJSP_MultiplasAbordagens()
    
    try:
        buscador.executar()
    
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
