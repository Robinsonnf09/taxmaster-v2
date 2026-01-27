"""
Script com URL CORRETA do TRF3 identificada da planilha!
URL: https://web.trf3.jus.br/consultas/internet/consultaregpag
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

class BuscadorOficiosTRF3:
    
    def __init__(self):
        self.driver = None
        self.sucessos = []
        self.falhas = []
        # URL OFICIAL CORRETA DO TRF3!
        self.url_consulta = "https://web.trf3.jus.br/consultas/internet/consultaregpag"
        
        self.pasta_oficios = "oficios_requisitorios_trf3"
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
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
    
    def acessar_sistema(self):
        print(f"\n🔐 Acessando Consulta TRF3...")
        print(f"   URL: {self.url_consulta}")
        
        self.driver.get(self.url_consulta)
        time.sleep(4)
        
        print("\n✅ Sistema acessado!")
        print("⚠️  Se houver login/captcha, resolva manualmente")
        
        input("\n>>> ENTER quando estiver na tela de consulta <<<\n")
        
        return True
    
    def buscar_oficio(self, numero_processo):
        try:
            print(f"\n📝 Buscando: {numero_processo}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Procurar campo de número
            campo = None
            try:
                campo = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='text' or contains(@name, 'processo') or contains(@id, 'processo')]")
                ))
                print(f"   ✅ Campo localizado")
            except:
                print(f"   ⚠️  Campo não encontrado automaticamente")
                input(f"   >>> Digite '{numero_processo}' manualmente e pressione ENTER <<<\n")
                campo = None
            
            if campo:
                campo.clear()
                time.sleep(0.3)
                campo.send_keys(numero_processo)
                time.sleep(0.5)
                print(f"   ✅ Número digitado")
                
                # Procurar botão
                try:
                    btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Consultar') or contains(text(), 'Pesquisar') or contains(text(), 'Buscar')] | //input[@type='submit']")
                    btn.click()
                    print(f"   ⏳ Consultando...")
                    time.sleep(5)
                except:
                    input(f"   >>> Clique em CONSULTAR manualmente e pressione ENTER <<<\n")
            
            # Verificar resultado
            page = self.driver.page_source.lower()
            
            if "não encontrado" in page or "nenhum registro" in page:
                print(f"   ❌ Processo não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            # Procurar ofício/documento
            print(f"   🔍 Procurando documentos...")
            
            links = self.driver.find_elements(By.TAG_NAME, "a")
            documentos = []
            
            for link in links:
                texto = link.text.lower()
                if any(x in texto for x in ['ofício', 'requisitório', 'requisição', 'or', 'pdf', 'documento']):
                    documentos.append(link)
            
            if not documentos:
                print(f"   ⚠️  Nenhum documento encontrado automaticamente")
                opcao = input(f"   >>> Há documentos para baixar? (s/n): ").lower()
                
                if opcao == 's':
                    input(f"   >>> Baixe os documentos e pressione ENTER <<<\n")
                    self.sucessos.append(numero_processo)
                    return True
                else:
                    self.falhas.append(numero_processo)
                    return False
            
            # Baixar documentos
            print(f"   ✅ {len(documentos)} documento(s) encontrado(s)!")
            
            for idx, link in enumerate(documentos, 1):
                try:
                    print(f"   📥 Baixando documento {idx}...")
                    link.click()
                    time.sleep(3)
                    print(f"   ✅ Documento {idx} baixado!")
                    
                    # Voltar
                    self.driver.back()
                    time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Erro ao baixar documento {idx}")
            
            self.sucessos.append(numero_processo)
            return True
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            self.falhas.append(numero_processo)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Processando: {arquivo}")
        
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
        print(f"✅ {total} processos")
        print(f"📁 Salvando em: {os.path.abspath(self.pasta_oficios)}\n")
        
        for idx, numero in enumerate(processos, 1):
            print(f"\n{'='*70}")
            print(f"Processo {idx}/{total}")
            print(f"{'='*70}")
            
            self.buscar_oficio(numero)
            
            if idx < total:
                time.sleep(3)
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO FINAL:")
        print("="*70)
        print(f"   Total: {total}")
        print(f"   ✅ Com documentos: {len(self.sucessos)}")
        print(f"   ❌ Sem documentos: {len(self.falhas)}")
        if total > 0:
            print(f"   📊 Taxa: {(len(self.sucessos)/total*100):.1f}%")
        
        print(f"\n📁 Documentos em: {os.path.abspath(self.pasta_oficios)}")
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 BUSCA DE OFÍCIOS REQUISITÓRIOS - TRF3")
    print("="*70)
    print(f"\n🎯 URL OFICIAL: web.trf3.jus.br/consultas/internet/consultaregpag")
    
    buscador = BuscadorOficiosTRF3()
    
    try:
        input("\nENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.acessar_sistema():
            
            print("\n💡 MODO:")
            print("   1. Planilha (215 processos)")
            print("   2. Teste individual")
            
            modo = input("\nDigite: ").strip()
            
            if modo == "1":
                buscador.processar_planilha("processos_push_20260126_185045.xlsx")
            
            elif modo == "2":
                num = input("\nNúmero: ").strip()
                buscador.buscar_oficio(num)
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ CONCLUÍDO!")
