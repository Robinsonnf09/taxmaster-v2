"""
Automatizador de Busca de Ofícios Requisitórios - SEJU TRF3
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
from pathlib import Path

class BuscadorOficiosRequisitorios:
    
    def __init__(self):
        self.driver = None
        self.sucessos = []
        self.falhas = []
        self.url_seju = "https://sistemas.trf3.jus.br/seju/consulta-processual"
        
        # Pasta para salvar ofícios
        self.pasta_oficios = "oficios_requisitorios"
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        # Configurar download automático
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        
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
    
    def acessar_seju(self):
        print(f"\n🔐 Acessando SEJU TRF3: {self.url_seju}")
        self.driver.get(self.url_seju)
        
        print("\n" + "="*70)
        print("⚠️  FAÇA LOGIN NO SEJU (se necessário):")
        print("="*70)
        print("   1. Se pedir certificado, selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   2. Digite o PIN")
        print("   3. Aguarde carregar a página de consulta")
        print("="*70)
        
        input("\n>>> ENTER quando estiver na página de consulta <<<\n")
        
        print("✅ SEJU acessado!")
        return True
    
    def buscar_oficio(self, numero_processo):
        try:
            print(f"\n📝 Buscando: {numero_processo}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Localizar campo de busca
            campo = None
            try:
                # Tentar vários seletores possíveis
                campo = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='text' and (contains(@name, 'processo') or contains(@id, 'processo') or contains(@placeholder, 'processo'))]")
                ))
                print(f"   ✅ Campo de busca localizado")
            except:
                print(f"   ❌ Campo de busca não encontrado!")
                self.falhas.append(numero_processo)
                return False
            
            # Preencher número
            campo.clear()
            time.sleep(0.3)
            campo.send_keys(numero_processo)
            time.sleep(0.5)
            print(f"   ✅ Número digitado")
            
            # Buscar botão de consulta
            btn = None
            botoes_possiveis = [
                "//button[contains(text(), 'Consultar')]",
                "//button[contains(text(), 'Buscar')]",
                "//button[contains(text(), 'Pesquisar')]",
                "//input[@type='submit' and contains(@value, 'Consultar')]",
                "//button[@type='submit']"
            ]
            
            for xpath in botoes_possiveis:
                try:
                    btn = self.driver.find_element(By.XPATH, xpath)
                    break
                except:
                    continue
            
            if not btn:
                print(f"   ❌ Botão de consulta não encontrado!")
                self.falhas.append(numero_processo)
                return False
            
            # Clicar
            btn.click()
            print(f"   ⏳ Aguardando resultados...")
            time.sleep(5)
            
            # Verificar se processo foi encontrado
            page = self.driver.page_source.lower()
            
            if "não encontrado" in page or "nenhum resultado" in page:
                print(f"   ❌ Processo não encontrado no SEJU")
                self.falhas.append(numero_processo)
                return False
            
            # Procurar link do ofício requisitório
            print(f"   🔍 Procurando Ofício Requisitório...")
            
            oficios_encontrados = []
            
            # Tentar vários textos possíveis
            textos_oficio = [
                "ofício requisitório",
                "oficio requisitorio",
                "requisição",
                "precatório",
                "rpv",
                "or"
            ]
            
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                texto_link = link.text.lower()
                for texto in textos_oficio:
                    if texto in texto_link:
                        oficios_encontrados.append(link)
                        break
            
            if not oficios_encontrados:
                print(f"   ⚠️  Nenhum ofício requisitório encontrado para este processo")
                print(f"   💡 Processo existe, mas pode não ter OR ainda")
                self.falhas.append(numero_processo)
                return False
            
            # Baixar ofícios
            print(f"   ✅ {len(oficios_encontrados)} ofício(s) encontrado(s)!")
            
            for idx, link in enumerate(oficios_encontrados, 1):
                try:
                    print(f"   📥 Baixando ofício {idx}...")
                    link.click()
                    time.sleep(3)
                    print(f"   ✅ Ofício {idx} baixado!")
                except Exception as e:
                    print(f"   ⚠️  Erro ao baixar ofício {idx}: {str(e)[:50]}")
            
            self.sucessos.append(numero_processo)
            return True
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            self.falhas.append(numero_processo)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Processando planilha: {arquivo}")
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado!")
            return
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                processos.append(str(row[0]).strip())
        
        total = len(processos)
        print(f"✅ {total} processos na planilha")
        print(f"📁 Ofícios serão salvos em: {os.path.abspath(self.pasta_oficios)}\n")
        
        for idx, numero in enumerate(processos, 1):
            print(f"\n{'='*70}")
            print(f"Processo {idx}/{total}")
            print(f"{'='*70}")
            
            self.buscar_oficio(numero)
            
            # Intervalo entre buscas
            if idx < total:
                time.sleep(3)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   📋 Total: {total}")
        print(f"   ✅ Com ofício: {len(self.sucessos)}")
        print(f"   ❌ Sem ofício/erro: {len(self.falhas)}")
        if total > 0:
            print(f"   📊 Taxa: {(len(self.sucessos)/total*100):.1f}%")
        
        print(f"\n📁 Ofícios salvos em:")
        print(f"   {os.path.abspath(self.pasta_oficios)}")
        
        if self.falhas:
            print(f"\n❌ Processos sem ofício:")
            for p in self.falhas[:20]:
                print(f"   - {p}")
            if len(self.falhas) > 20:
                print(f"   ... e mais {len(self.falhas)-20}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 BUSCA AUTOMÁTICA DE OFÍCIOS REQUISITÓRIOS - SEJU TRF3")
    print("="*70)
    
    buscador = BuscadorOficiosRequisitorios()
    
    try:
        input("\nToken A3 conectado? ENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.acessar_seju():
            
            print("\n💡 MODO:")
            print("   1. Planilha em lote (215 processos)")
            print("   2. Processo individual (teste)")
            
            modo = input("\nDigite 1 ou 2: ").strip()
            
            if modo == "1":
                arq = "processos_push_20260126_185045.xlsx"
                buscador.processar_planilha(arq)
            
            elif modo == "2":
                num = input("\nNúmero do processo: ").strip()
                buscador.buscar_oficio(num)
        
        input("\n\n>>> ENTER para fechar <<<\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada")
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        buscador.fechar()
    
    print("\n✅ CONCLUÍDO!")
