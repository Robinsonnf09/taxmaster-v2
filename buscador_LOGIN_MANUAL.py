"""
BUSCADOR COM LOGIN MANUAL ASSISTIDO
Você faz login manualmente, depois o script automatiza o resto
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import openpyxl
from datetime import datetime
import shutil
import glob

try:
    import pikepdf
    PIKEPDF = True
except:
    PIKEPDF = False

class BuscadorTJSP_LoginManual:
    
    def __init__(self):
        self.driver = None
        
        self.pasta_oficios = "oficios_LOGIN_MANUAL"
        self.planilha = "processos_TESTE_3.xlsx"
        
        if os.path.exists(self.pasta_oficios):
            shutil.rmtree(self.pasta_oficios)
        os.makedirs(self.pasta_oficios)
        
        self.pasta_downloads = "downloads_temp_manual"
        if os.path.exists(self.pasta_downloads):
            shutil.rmtree(self.pasta_downloads)
        os.makedirs(self.pasta_downloads)
        
        self.janela_principal = None
        self.total_pdfs = 0
    
    def validar_pdf(self, caminho):
        try:
            with open(caminho, 'rb') as f:
                primeiros = f.read(10)
                tamanho = os.path.getsize(caminho)
            
            if not primeiros.startswith(b'%PDF') or tamanho < 1024:
                return False, "Inválido"
            
            if PIKEPDF:
                with pikepdf.open(caminho) as pdf:
                    num = len(pdf.pages)
                    return True, f"{num} pág, {tamanho//1024} KB"
            
            return True, f"{tamanho//1024} KB"
        
        except:
            return False, "Erro"
    
    def iniciar_edge(self):
        print("\n🔷 Iniciando Edge...")
        
        options = Options()
        options.add_argument('--start-maximized')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_downloads),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Edge(options=options)
        self.janela_principal = self.driver.current_window_handle
        
        print("✅ Edge iniciado!")
    
    def login_manual_assistido(self):
        """Usuário faz login manualmente"""
        print(f"\n🔐 LOGIN MANUAL ASSISTIDO")
        print(f"{'='*70}")
        
        print(f"\n📍 Acessando e-SAJ...")
        self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        print(f"\n{'='*70}")
        print(f"👤 FAÇA LOGIN MANUALMENTE NO NAVEGADOR")
        print(f"{'='*70}")
        print(f"\nOpções de login:")
        print(f"   1. 🔐 Certificado Digital (se aparecer popup)")
        print(f"   2. 👤 Usuário e Senha (se tiver credenciais)")
        print(f"   3. 🏛️  Login institucional (se tiver acesso)")
        print(f"\n⏳ Aguarde até estar LOGADO no sistema...")
        print(f"   (Você verá a página inicial do e-SAJ)")
        
        print(f"\n{'='*70}")
        input(">>> Após fazer LOGIN com SUCESSO, pressione ENTER aqui <<<\n")
        
        # Verificar se está logado
        url_atual = self.driver.current_url
        
        print(f"\n✅ URL atual: {url_atual}")
        
        if "login" in url_atual.lower():
            print(f"⚠️  Ainda parece estar na tela de login")
            confirma = input("\n>>> Você conseguiu fazer login? (s/n): ").lower()
            
            if confirma != 's':
                print(f"\n❌ Login não realizado. Encerrando.")
                return False
        
        print(f"\n✅ Login confirmado! Iniciando automação...")
        return True
    
    def aguardar_download(self, timeout=15):
        tempo_inicio = time.time()
        
        while time.time() - tempo_inicio < timeout:
            temp = glob.glob(os.path.join(self.pasta_downloads, "*.crdownload"))
            pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
            
            if len(temp) == 0 and len(pdfs) > 0:
                time.sleep(1)
                return True
            
            time.sleep(0.5)
        
        return False
    
    def limpar_downloads(self):
        for arq in os.listdir(self.pasta_downloads):
            try:
                os.remove(os.path.join(self.pasta_downloads, arq))
            except:
                pass
    
    def buscar_oficios(self, numero, idx, total):
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero}")
            print(f"{'='*70}")
            
            # Buscar processo
            print(f"   🔍 Buscando...", end=" ", flush=True)
            
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(2)
            
            try:
                radio = self.driver.find_element(By.ID, "radioNumeroAntigo")
                radio.click()
                time.sleep(0.5)
            except:
                pass
            
            campo = self.driver.find_element(By.ID, "nuProcessoAntigoFormatado")
            campo.clear()
            campo.send_keys(numero)
            campo.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            url = self.driver.current_url
            
            if "processo.codigo=" not in url:
                print(f"❌ Não encontrado")
                return False
            
            codigo = url.split("processo.codigo=")[1].split("&")[0]
            print(f"✅ {codigo}")
            
            # Acessar requisitórios
            foro = numero.split(".")[-1].lstrip('0') or "0"
            
            url_req = (
                f"https://esaj.tjsp.jus.br/cpopg/show.do?"
                f"processo.codigo={codigo}&"
                f"processo.foro={foro}&"
                f"processo.numero={numero}&"
                f"consultaDeRequisitorios=true"
            )
            
            print(f"   🎯 Acessando requisitórios...", end=" ", flush=True)
            self.driver.get(url_req)
            time.sleep(3)
            print(f"✅")
            
            # Buscar docs
            print(f"   🔍 Localizando docs...", end=" ", flush=True)
            
            docs = self.driver.execute_script("""
                let d = [];
                document.querySelectorAll('a.linkMovVincProc').forEach((a, i) => {
                    let t = a.textContent.trim();
                    if (t.includes('DEPRE') || t.includes('Ofício') || t.includes('OR ')) {
                        a.setAttribute('data-d', i);
                        d.push({id: i, texto: t});
                    }
                });
                return d;
            """)
            
            if not docs:
                print(f"⚠️  Nenhum")
                return False
            
            print(f"✅ {len(docs)}")
            
            # Testar PRIMEIRO
            doc = docs[0]
            
            print(f"\n   📥 Testando: {doc['texto'][:45]}...")
            
            self.limpar_downloads()
            
            elem = self.driver.find_element(By.CSS_SELECTOR, f"a[data-d='{doc['id']}']")
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
            time.sleep(1)
            
            jan_antes = len(self.driver.window_handles)
            
            print(f"      👆 Clicando...", end=" ", flush=True)
            ActionChains(self.driver).move_to_element(elem).click().perform()
            print(f"✅")
            
            time.sleep(3)
            
            jan_depois = len(self.driver.window_handles)
            
            if jan_depois > jan_antes:
                print(f"      ✅ Aba aberta")
                
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                print(f"      ⏳ Aguardando download...", end=" ", flush=True)
                
                if self.aguardar_download(timeout=15):
                    print(f"✅")
                    
                    pdfs = glob.glob(os.path.join(self.pasta_downloads, "*.pdf"))
                    
                    if pdfs:
                        arq = pdfs[0]
                        
                        valido, info = self.validar_pdf(arq)
                        
                        if valido:
                            dest = os.path.join(self.pasta_oficios, f"teste_{idx}.pdf")
                            shutil.move(arq, dest)
                            
                            print(f"      ✅ PDF VÁLIDO! {info}")
                            self.total_pdfs += 1
                        else:
                            print(f"      ❌ Inválido: {info}")
                else:
                    print(f"❌")
                
                self.driver.close()
                self.driver.switch_to.window(self.janela_principal)
            
            else:
                print(f"      ❌ Sem aba")
            
            return False
            
        except Exception as e:
            print(f"      ❌ Erro: {type(e).__name__}")
            return False
    
    def carregar_processos(self):
        caminho = os.path.join(os.getcwd(), self.planilha)
        if not os.path.exists(caminho):
            return []
        
        wb = openpyxl.load_workbook(caminho)
        ws = wb.active
        
        procs = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    procs.append(num)
        
        wb.close()
        return procs
    
    def executar(self):
        print("\n" + "="*70)
        print("🔍 BUSCADOR COM LOGIN MANUAL ASSISTIDO")
        print("="*70)
        
        procs = self.carregar_processos()
        
        if not procs:
            return
        
        print(f"\n📋 {len(procs)} processos")
        
        confirma = input(f"\n>>> Iniciar? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        self.iniciar_edge()
        
        if not self.login_manual_assistido():
            self.fechar()
            return
        
        # Testar primeiro processo
        self.buscar_oficios(procs[0], 1, 1)
        
        print(f"\n{'='*70}")
        print(f"✅ TESTE CONCLUÍDO")
        print(f"📄 PDFs válidos: {self.total_pdfs}")
        print(f"📁 Pasta: {os.path.abspath(self.pasta_oficios)}")
        print(f"{'='*70}")
        
        input("\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    buscador = BuscadorTJSP_LoginManual()
    
    try:
        buscador.executar()
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
    finally:
        buscador.fechar()
    
    print("\n✅ ENCERRADO\n")
