"""
BUSCAR OFÍCIOS REQUISITÓRIOS - URL DIRETA TJSP
Acessa diretamente a página de requisitórios
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import openpyxl
from datetime import datetime

class BuscadorRequisitoriosDireto:
    
    def __init__(self):
        self.driver = None
        self.url_base_requisitorios = "https://esaj.tjsp.jus.br/cpopg/show.do"
        
        self.pasta_oficios = "oficios_requisitorios_tjsp"
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome iniciado!")
        print(f"📁 PDFs salvos em: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login(self):
        print(f"\n🔐 Acessando e-SAJ...")
        self.driver.get("https://esaj.tjsp.jus.br")
        time.sleep(3)
        
        print("\n" + "="*70)
        print("👉 FAÇA LOGIN:")
        print("="*70)
        input("\n>>> ENTER após login <<<\n")
        return True
    
    def buscar_codigo_processo(self, numero_processo):
        """Busca o código interno do processo"""
        try:
            # Acessar consulta normal primeiro
            url_consulta = "https://esaj.tjsp.jus.br/cpopg/open.do"
            self.driver.get(url_consulta)
            time.sleep(2)
            
            # Buscar processo
            campo = self.driver.find_element(By.ID, "nuProcessoAntigoFormatado")
            campo.clear()
            campo.send_keys(numero_processo)
            
            btn = self.driver.find_element(By.ID, "pbConsultar")
            btn.click()
            time.sleep(3)
            
            # Extrair código da URL atual
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                # Extrair código
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                return codigo
            
            return None
            
        except:
            return None
    
    def buscar_oficio_direto(self, numero_processo, idx, total):
        """Acessa diretamente a página de requisitórios"""
        try:
            print(f"\n{'='*70}")
            print(f"📝 [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            # Extrair foro do número (ex: 0500)
            foro = numero_processo.split(".")[-1]
            
            print(f"   🔍 Buscando código do processo...")
            
            # Buscar código interno
            codigo = self.buscar_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"   ⚠️  Não foi possível obter código automaticamente")
                print(f"   💡 Busque manualmente: {numero_processo}")
                input(f"   >>> ENTER após buscar <<<\n")
                
                # Tentar extrair da URL atual
                url_atual = self.driver.current_url
                if "processo.codigo=" in url_atual:
                    codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                else:
                    print(f"   ❌ Código não encontrado")
                    self.falhas.append(numero_processo)
                    return False
            
            print(f"   ✅ Código: {codigo}")
            
            # Construir URL direta de requisitórios
            url_requisitorios = (
                f"{self.url_base_requisitorios}?"
                f"processo.codigo={codigo}&"
                f"processo.foro={foro}&"
                f"processo.numero={numero_processo}&"
                f"consultaDeRequisitorios=true"
            )
            
            print(f"   🎯 Acessando página de requisitórios...")
            self.driver.get(url_requisitorios)
            time.sleep(3)
            
            # Procurar ofícios na página
            print(f"   🔍 Procurando ofícios requisitórios...")
            
            # Salvar HTML para debug
            with open(f"debug_requisitorios_{numero_processo.replace('-','').replace('.','')}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            
            # Procurar links de PDF
            links_pdf = []
            
            # Procurar todos os links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                href = link.get_attribute("href") or ""
                texto = link.text.lower()
                
                if any(x in texto for x in ['ofício', 'requisitório', 'or', 'pdf']):
                    if link.is_displayed():
                        links_pdf.append({
                            "elemento": link,
                            "texto": link.text,
                            "href": href
                        })
            
            if links_pdf:
                print(f"   ✅ {len(links_pdf)} ofício(s) encontrado(s)!")
                
                for of in links_pdf:
                    print(f"      - {of['texto']}")
                
                # Baixar ofícios
                print(f"\n   📥 DOWNLOAD MANUAL:")
                print(f"   ===================================")
                print(f"   1. Clique COM BOTÃO DIREITO no ofício")
                print(f"   2. Escolha 'Salvar link como...'")
                print(f"   3. Salve em: {os.path.abspath(self.pasta_oficios)}")
                print(f"   4. Nome sugerido: oficio_{numero_processo.replace('-','').replace('.','')}.pdf")
                print(f"   ===================================")
                
                input(f"\n   >>> ENTER após salvar <<<\n")
                
                self.sucessos.append(numero_processo)
                return True
                
            else:
                print(f"   ⚠️  Nenhum ofício encontrado")
                print(f"   💡 Há ofício visível na página?")
                
                opcao = input(f"   >>> (s/n): ").lower()
                
                if opcao == 's':
                    print(f"   📥 Salve manualmente")
                    input(f"   >>> ENTER após salvar <<<\n")
                    self.sucessos.append(numero_processo)
                    return True
                else:
                    self.sem_oficio.append(numero_processo)
                    return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            self.falhas.append(numero_processo)
            return False
    
    def processar_planilha(self, arquivo):
        print(f"\n📊 Carregando: {arquivo}")
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    processos.append(num)
        
        total = len(processos)
        print(f"✅ {total} processos do TJSP")
        
        confirma = input(f"\n>>> Processar {total} processos? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficio_direto(numero, idx, total)
            
            if idx < total:
                time.sleep(2)
        
        # Relatório
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL")
        print("="*70)
        
        total_proc = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n   Total: {total_proc}")
        print(f"   ✅ Com ofício: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        print(f"\n   ⏱️  Tempo: {int(duracao.total_seconds()/60)} min")
        
        if self.sem_oficio:
            print(f"\n⚠️  SEM OFÍCIO:")
            for p in self.sem_oficio[:15]:
                print(f"   - {p}")
        
        if self.falhas:
            print(f"\n❌ FALHAS:")
            for p in self.falhas[:15]:
                print(f"   - {p}")
        
        print("="*70)
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 BUSCAR REQUISITÓRIOS - URL DIRETA")
    print("="*70)
    
    buscador = BuscadorRequisitoriosDireto()
    
    try:
        input("\nENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.fazer_login():
            
            print("\n💡 MODO:")
            print("   1. Teste (1 processo)")
            print("   2. Planilha completa")
            
            modo = input("\nDigite: ").strip()
            
            if modo == "1":
                num = input("\nProcesso: ").strip()
                buscador.buscar_oficio_direto(num, 1, 1)
            elif modo == "2":
                buscador.processar_planilha("processos_push_20260126_185045.xlsx")
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ FIM!")
