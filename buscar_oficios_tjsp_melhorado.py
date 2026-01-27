"""
BUSCAR OFÍCIOS TJSP - VERSÃO MELHORADA COMPLETA
Baixa PDFs com método robusto
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class BuscadorOficiosMelhorado:
    
    def __init__(self):
        self.driver = None
        self.url_base = "https://esaj.tjsp.jus.br"
        self.pasta_oficios = "oficios_tjsp_pasta_digital"
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome com configuração de download...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        # Configuração FORÇADA de download
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome iniciado!")
        print(f"📁 PDFs serão salvos em: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login(self):
        print(f"\n🔐 Acessando e-SAJ...")
        self.driver.get(self.url_base)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("👉 FAÇA LOGIN:")
        print("="*70)
        input("\n>>> ENTER após login <<<\n")
        return True
    
    def baixar_oficio_teste(self, numero_processo):
        print(f"\n{'='*70}")
        print(f"📝 {numero_processo}")
        print(f"{'='*70}")
        
        # Consulta processual
        url_consulta = f"{self.url_base}/cpopg/open.do"
        print(f"   🔍 Acessando consulta...")
        self.driver.get(url_consulta)
        time.sleep(2)
        
        # Buscar processo
        print(f"   ⌨️  Busque: {numero_processo}")
        input(f"   >>> ENTER após buscar <<<\n")
        
        # Pasta Digital
        print(f"   📂 Clique em 'Pasta Digital'")
        input(f"   >>> ENTER após clicar <<<\n")
        time.sleep(3)
        
        # MÉTODO DEFINITIVO: Botão direito + Salvar como
        print(f"\n   📥 INSTRUÇÕES DE DOWNLOAD:")
        print(f"   =====================================")
        print(f"   1. Clique COM BOTÃO DIREITO no ofício")
        print(f"   2. Escolha 'Salvar link como...' OU 'Save link as...'")
        print(f"   3. Verifique que a pasta é:")
        print(f"      {os.path.abspath(self.pasta_oficios)}")
        print(f"   4. Salve o arquivo")
        print(f"   =====================================")
        
        input(f"\n   >>> ENTER após SALVAR o PDF <<<\n")
        
        # Verificar se salvou
        arquivos = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        
        if arquivos:
            print(f"\n   ✅ PDF ENCONTRADO!")
            for arq in arquivos:
                tam = os.path.getsize(os.path.join(self.pasta_oficios, arq))
                print(f"      📄 {arq} ({tam:,} bytes)")
            return True
        else:
            print(f"\n   ⚠️  PDF não encontrado na pasta")
            print(f"   💡 Verifique se salvou no local correto")
            return False
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 BUSCAR OFÍCIOS - TJSP")
    print("="*70)
    
    buscador = BuscadorOficiosMelhorado()
    
    try:
        input("\nENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.fazer_login():
            num = input("\nNúmero do processo: ").strip()
            buscador.baixar_oficio_teste(num)
            
            # Verificar
            print("\n" + "="*70)
            print("📂 RESULTADO FINAL:")
            print("="*70)
            
            arquivos = [f for f in os.listdir("oficios_tjsp_pasta_digital") 
                       if f.endswith('.pdf')]
            
            if arquivos:
                print(f"\n✅ {len(arquivos)} PDF(s) na pasta:")
                for pdf in arquivos:
                    path = os.path.join("oficios_tjsp_pasta_digital", pdf)
                    tam = os.path.getsize(path)
                    print(f"   📄 {pdf} ({tam:,} bytes)")
                    
                print(f"\n🎉 SUCESSO!")
            else:
                print(f"\n⚠️  Nenhum PDF na pasta")
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ FIM!")
