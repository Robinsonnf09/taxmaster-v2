"""
BUSCAR REQUISITÓRIOS TJSP - SEM POPUP WEB SIGNER
Configurações que evitam o popup
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import os
import openpyxl
from datetime import datetime
import requests

class BuscadorSemPopup:
    
    def __init__(self):
        self.driver = None
        self.session = None
        self.pasta_oficios = "oficios_requisitorios_tjsp"
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome (configuração especial)...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        # Configurações para evitar popup
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-extensions')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            # Desabilitar detecção de certificado
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.session = requests.Session()
        
        print("✅ Chrome iniciado!")
        print(f"📁 PDFs em: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login_unico(self):
        print(f"\n🔐 Login único...")
        self.driver.get("https://esaj.tjsp.jus.br")
        time.sleep(3)
        
        print("\n" + "="*70)
        print("⚠️  INSTRUÇÕES DE LOGIN:")
        print("="*70)
        print("   ❌ SE APARECER POPUP 'WEB SIGNER':")
        print("      → Clique em CANCELAR")
        print("")
        print("   ✅ USE LOGIN E SENHA:")
        print("      → Digite usuário e senha")
        print("      → Faça login normalmente")
        print("")
        print("   💡 NÃO use certificado digital")
        print("="*70)
        
        input("\n>>> ENTER após login <<<\n")
        
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'])
        
        print("✅ Login salvo!")
        return True
    
    def buscar_processo_automatico(self, numero_processo):
        try:
            url_consulta = "https://esaj.tjsp.jus.br/cpopg/open.do"
            self.driver.get(url_consulta)
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, 10)
            
            try:
                radio = wait.until(EC.element_to_be_clickable(
                    (By.ID, "radioNumeroAntigo")
                ))
                radio.click()
                time.sleep(0.5)
            except:
                pass
            
            try:
                campo = wait.until(EC.visibility_of_element_located(
                    (By.ID, "nuProcessoAntigoFormatado")
                ))
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
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def baixar_pdf_automatico(self, url_pdf, nome_arquivo):
        try:
            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://esaj.tjsp.jus.br/'
            }
            
            response = self.session.get(url_pdf, headers=headers, timeout=30)
            
            if response.status_code == 200 and len(response.content) > 1000:
                caminho = os.path.join(self.pasta_oficios, nome_arquivo)
                
                with open(caminho, 'wb') as f:
                    f.write(response.content)
                
                return True, len(response.content)
            
            return False, 0
            
        except:
            return False, 0
    
    def processar_processo_automatico(self, numero_processo, idx, total):
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            print(f"   🔍 Código...", end=" ", flush=True)
            
            codigo = self.buscar_processo_automatico(numero_processo)
            
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
            
            print(f"   🎯 Requisitórios...", end=" ", flush=True)
            self.driver.get(url_requisitorios)
            time.sleep(2)
            print(f"✅")
            
            print(f"   🔍 Ofícios...", end=" ", flush=True)
            
            script = """
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
            
            oficios = self.driver.execute_script(script)
            
            if not oficios or len(oficios) == 0:
                print(f"⚠️")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(oficios)}")
            
            baixados = 0
            
            for idx_of, oficio in enumerate(oficios, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_arquivo = f"{nome_limpo}_of{idx_of}.pdf"
                
                print(f"   📥 {idx_of}/{len(oficios)}...", end=" ", flush=True)
                
                sucesso, tamanho = self.baixar_pdf_automatico(
                    oficio['url'], 
                    nome_arquivo
                )
                
                if sucesso:
                    kb = tamanho // 1024
                    print(f"✅ {kb}KB")
                    baixados += 1
                else:
                    print(f"❌")
            
            if baixados > 0:
                self.sucessos.append(numero_processo)
                return True
            else:
                self.falhas.append(numero_processo)
                return False
            
        except Exception as e:
            print(f"   ❌")
            self.falhas.append(numero_processo)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Carregando...")
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    processos.append(num)
        
        total = len(processos)
        print(f"✅ {total} processos")
        
        confirma = input(f"\n>>> Processar {total}? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.processar_processo_automatico(numero, idx, total)
            
            if idx % 20 == 0:
                print(f"\n{'='*70}")
                print(f"📊 {idx}/{total} ({idx/total*100:.1f}%)")
                print(f"   ✅ {len(self.sucessos)} | ⚠️  {len(self.sem_oficio)} | ❌ {len(self.falhas)}")
                
                decorrido = (datetime.now() - inicio).total_seconds()
                media = decorrido / idx
                restante = (total - idx) * media
                
                print(f"   ⏱️  {int(decorrido/60)}min | ⏳ ~{int(restante/60)}min")
                print(f"{'='*70}\n")
            
            time.sleep(0.8)
        
        self.gerar_relatorio_final(inicio)
    
    def gerar_relatorio_final(self, inicio):
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("🎉 CONCLUÍDO!")
        print("="*70)
        
        total = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n   Total: {total}")
        print(f"   ✅ Com ofício: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        
        if total > 0:
            taxa = (len(self.sucessos) / total) * 100
            print(f"   📊 Taxa: {taxa:.1f}%")
        
        print(f"\n   ⏱️  {int(duracao.total_seconds()/60)} min")
        
        pdfs = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"   📄 {len(pdfs)} PDFs")
        print(f"\n📁 {os.path.abspath(self.pasta_oficios)}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    print("="*70)
    print("⚡ BUSCAR REQUISITÓRIOS - SEM POPUP")
    print("="*70)
    
    buscador = BuscadorSemPopup()
    
    try:
        input("\nENTER...\n")
        
        buscador.iniciar()
        
        if buscador.fazer_login_unico():
            buscador.processar_planilha("processos_push_20260126_185045.xlsx")
        
        input("\n\nENTER para fechar...\n")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido")
    
    except Exception as e:
        print(f"\n❌ {e}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ FIM!")
