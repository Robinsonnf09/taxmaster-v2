"""
BUSCAR OFÍCIOS REQUISITÓRIOS - PASTA DIGITAL TJSP
Acessa a pasta digital de cada processo e baixa os ofícios
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import openpyxl
import os
from datetime import datetime

class BuscadorOficiosPastaDigitalTJSP:
    
    def __init__(self):
        self.driver = None
        self.url_base = "https://esaj.tjsp.jus.br"
        
        # Pasta para salvar ofícios
        self.pasta_oficios = "oficios_tjsp_pasta_digital"
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
        # Configurar download automático
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def fazer_login(self):
        print(f"\n🔐 Acessando e-SAJ TJSP...")
        self.driver.get(self.url_base)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("👉 FAÇA LOGIN NO e-SAJ:")
        print("="*70)
        print("   1. Use certificado digital OU login/senha")
        print("   2. Se pedir Web Signer, clique CANCELAR e use login/senha")
        print("   3. Aguarde até estar LOGADO na área interna")
        print("="*70)
        
        input("\n>>> ENTER após fazer login completo <<<\n")
        
        print("✅ Login confirmado!")
        return True
    
    def buscar_oficio_processo(self, numero_processo, idx, total):
        """Busca ofício requisitório de um processo específico"""
        try:
            print(f"\n{'='*70}")
            print(f"📝 [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            # Construir URL da consulta processual
            url_consulta = f"{self.url_base}/cpopg/open.do"
            
            print(f"   🔍 Acessando consulta processual...")
            self.driver.get(url_consulta)
            time.sleep(2)
            
            # Buscar o processo
            try:
                # Tentar encontrar campo de busca
                campo = self.driver.find_element(By.ID, "nuProcessoAntigoFormatado")
                campo.clear()
                campo.send_keys(numero_processo)
                time.sleep(0.5)
                
                # Clicar em consultar
                btn = self.driver.find_element(By.ID, "pbConsultar")
                btn.click()
                print(f"   ⏳ Consultando processo...")
                time.sleep(3)
                
            except:
                print(f"   ⚠️  Campo de busca não encontrado")
                print(f"   💡 Busque manualmente: {numero_processo}")
                input(f"   >>> ENTER após buscar <<<\n")
            
            # Verificar se processo foi encontrado
            page_source = self.driver.page_source.lower()
            
            if "não encontrado" in page_source or "nenhum processo" in page_source:
                print(f"   ❌ Processo não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            # Procurar link "Pasta Digital"
            print(f"   📂 Procurando Pasta Digital...")
            
            try:
                # Tentar clicar em "Pasta Digital"
                link_pasta = self.driver.find_element(By.XPATH, 
                    "//a[contains(text(), 'Pasta Digital') or contains(@href, 'pastadigital')]")
                
                print(f"   ✅ Link Pasta Digital encontrado")
                link_pasta.click()
                time.sleep(4)
                
            except:
                print(f"   ⚠️  Link Pasta Digital não encontrado automaticamente")
                print(f"   💡 Clique manualmente em 'Pasta Digital'")
                input(f"   >>> ENTER após clicar <<<\n")
            
            # Agora estamos na Pasta Digital
            print(f"   📄 Procurando Ofício Requisitório...")
            
            # Mudar para iframe se existir
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    self.driver.switch_to.frame(iframes[0])
                    print(f"   ✅ Iframe detectado")
            except:
                pass
            
            # Procurar ofício requisitório
            oficios_encontrados = []
            
            # Estratégia 1: Links com texto
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                texto = link.text.lower()
                href = link.get_attribute("href") or ""
                
                if any(x in texto for x in ['ofício', 'requisitório', 'or', 'requisição']):
                    oficios_encontrados.append({
                        "elemento": link,
                        "texto": link.text,
                        "tipo": "link"
                    })
            
            # Estratégia 2: Ícones de PDF
            pdfs = self.driver.find_elements(By.XPATH, 
                "//img[contains(@src, 'pdf')] | //a[contains(@href, '.pdf')]")
            
            for pdf in pdfs:
                # Verificar se está próximo de texto com "ofício"
                try:
                    parent = pdf.find_element(By.XPATH, "./..")
                    texto_pai = parent.text.lower()
                    
                    if any(x in texto_pai for x in ['ofício', 'requisitório', 'or']):
                        oficios_encontrados.append({
                            "elemento": pdf,
                            "texto": texto_pai,
                            "tipo": "pdf"
                        })
                except:
                    pass
            
            if oficios_encontrados:
                print(f"   ✅ {len(oficios_encontrados)} ofício(s) encontrado(s)!")
                
                for idx_of, oficio in enumerate(oficios_encontrados, 1):
                    try:
                        print(f"   📥 Baixando ofício {idx_of}...")
                        
                        elemento = oficio["elemento"]
                        elemento.click()
                        time.sleep(3)
                        
                        # Se abriu nova aba, fechar
                        if len(self.driver.window_handles) > 1:
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            time.sleep(2)
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        
                        print(f"   ✅ Ofício {idx_of} baixado!")
                        
                    except Exception as e:
                        print(f"   ⚠️  Erro ao baixar ofício {idx_of}: {str(e)[:50]}")
                
                self.sucessos.append(numero_processo)
                return True
                
            else:
                print(f"   ⚠️  Nenhum ofício encontrado automaticamente")
                print(f"   💡 Há ofício visível na página?")
                
                opcao = input(f"   >>> (s/n): ").lower()
                
                if opcao == 's':
                    print(f"   💡 Clique no ofício para baixar")
                    input(f"   >>> ENTER após baixar <<<\n")
                    self.sucessos.append(numero_processo)
                    return True
                else:
                    print(f"   ⚠️  Processo sem ofício requisitório")
                    self.sem_oficio.append(numero_processo)
                    return False
            
            # Voltar para janela principal
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            self.falhas.append(numero_processo)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Carregando planilha: {arquivo}")
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado!")
            return
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        # Filtrar apenas TJSP
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    processos.append(num)
        
        total = len(processos)
        print(f"✅ {total} processos do TJSP")
        print(f"📁 Salvando em: {os.path.abspath(self.pasta_oficios)}\n")
        
        confirma = input(f">>> Processar {total} processos? (s/n): ").lower()
        
        if confirma != 's':
            print("❌ Cancelado")
            return
        
        # Processar
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficio_processo(numero, idx, total)
            
            if idx < total:
                time.sleep(2)
        
        # Relatório
        fim = datetime.now()
        duracao = fim - inicio
        
        self.gerar_relatorio(duracao)
    
    def gerar_relatorio(self, duracao):
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL")
        print("="*70)
        
        total = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n   Total processado: {total}")
        print(f"   ✅ Com ofício: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        
        print(f"\n   ⏱️  Tempo: {int(duracao.total_seconds()/60)} minutos")
        print(f"   📁 Pasta: {os.path.abspath(self.pasta_oficios)}")
        
        if self.sem_oficio:
            print(f"\n⚠️  PROCESSOS SEM OFÍCIO:")
            for p in self.sem_oficio[:20]:
                print(f"   - {p}")
        
        if self.falhas:
            print(f"\n❌ FALHAS:")
            for p in self.falhas[:20]:
                print(f"   - {p}")
        
        print("="*70)
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"relatorio_oficios_tjsp_{timestamp}.txt"
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write("RELATÓRIO - BUSCA DE OFÍCIOS TJSP\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total: {total}\n")
            f.write(f"Com ofício: {len(self.sucessos)}\n")
            f.write(f"Sem ofício: {len(self.sem_oficio)}\n")
            f.write(f"Falhas: {len(self.falhas)}\n\n")
            
            if self.sucessos:
                f.write("COM OFÍCIO:\n")
                for p in self.sucessos:
                    f.write(f"  {p}\n")
            
            if self.sem_oficio:
                f.write("\nSEM OFÍCIO:\n")
                for p in self.sem_oficio:
                    f.write(f"  {p}\n")
            
            if self.falhas:
                f.write("\nFALHAS:\n")
                for p in self.falhas:
                    f.write(f"  {p}\n")
        
        print(f"\n📄 Relatório: {arquivo}")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 BUSCAR OFÍCIOS REQUISITÓRIOS - PASTA DIGITAL TJSP")
    print("="*70)
    
    buscador = BuscadorOficiosPastaDigitalTJSP()
    
    try:
        input("\nENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.fazer_login():
            
            print("\n💡 MODO:")
            print("   1. Teste (1 processo)")
            print("   2. Planilha completa (137 processos)")
            
            modo = input("\nDigite: ").strip()
            
            if modo == "1":
                num = input("\nNúmero do processo: ").strip()
                buscador.buscar_oficio_processo(num, 1, 1)
                
            elif modo == "2":
                buscador.processar_planilha("processos_push_20260126_185045.xlsx")
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ CONCLUÍDO!")
