"""
VERSÃO FINAL - Download de Ofícios usando link correto
Descoberto: abrirConsultaDeRequisitorios.do
"""
import sys
import os
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("❌ Erro: Instale selenium e pandas")
    sys.exit(1)

class DownloaderOficiosFinal:
    """Download de ofícios usando link correto descoberto"""
    
    def __init__(self, pasta_destino="./oficios_pdf"):
        self.pasta_destino = Path(pasta_destino)
        self.pasta_destino.mkdir(exist_ok=True)
        
        self.pasta_debug = Path("./debug_screenshots")
        self.pasta_debug.mkdir(exist_ok=True)
        
        # Configurar Chrome
        chrome_options = Options()
        
        prefs = {
            "download.default_directory": str(self.pasta_destino.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--start-maximized')
        
        self.driver = None
        self.resultados = []
        self.oficios_baixados = 0
    
    def iniciar(self):
        print("🚀 Iniciando Chrome...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        print("✅ Pronto!\n")
    
    def buscar_oficios_v2(self, numero_processo, idx):
        """Versão 2 - usando link correto de requisitórios"""
        print(f"\n{'='*70}")
        print(f"[{idx}] 📋 {numero_processo}")
        print(f"{'='*70}")
        
        try:
            # URL CORRETA descoberta
            url_base = "https://esaj.tjsp.jus.br/cpopg/search.do"
            url = f"{url_base}?conversationId=&cbPesquisa=NUMPROC&dadosConsulta.valorConsulta={numero_processo}&dadosConsulta.tipoNuProcesso=UNIFICADO&consultaDeRequisitorios=true"
            
            print(f"🌐 Acessando processo...")
            self.driver.get(url)
            time.sleep(4)
            
            # Screenshot
            numero_limpo = numero_processo.replace('.', '_').replace('-', '_')
            screenshot1 = self.pasta_debug / f"{idx:04d}_a_processo_{numero_limpo}.png"
            self.driver.save_screenshot(str(screenshot1))
            print(f"📸 Screenshot processo: {screenshot1.name}")
            
            # CLICAR NO LINK DE REQUISITÓRIOS
            print(f"🔍 Procurando link 'Consulta de Requisitórios'...")
            
            try:
                # Tentar encontrar o link
                link_requisitorios = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(@href, 'abrirConsultaDeRequisitorios') or contains(text(), 'Requisitório')]"
                )
                
                print(f"✅ Link encontrado!")
                print(f"   Texto: {link_requisitorios.text}")
                print(f"   Clicando...")
                
                link_requisitorios.click()
                time.sleep(5)
                
                # Screenshot da página de requisitórios
                screenshot2 = self.pasta_debug / f"{idx:04d}_b_requisitorios_{numero_limpo}.png"
                self.driver.save_screenshot(str(screenshot2))
                print(f"📸 Screenshot requisitórios: {screenshot2.name}")
                
                # Salvar HTML
                html_path = self.pasta_debug / f"{idx:04d}_requisitorios_{numero_limpo}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                
                # PROCURAR PDFs NA PÁGINA DE REQUISITÓRIOS
                print(f"📄 Procurando PDFs de ofícios...")
                
                # Múltiplas estratégias
                pdfs = self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(@href, '.pdf') or contains(@onclick, 'pdf') or contains(text(), 'PDF') or contains(text(), 'Ofício')]"
                )
                
                if not pdfs:
                    # Procurar na tabela
                    pdfs = self.driver.find_elements(
                        By.XPATH,
                        "//table//a"
                    )
                
                if pdfs:
                    print(f"✅ {len(pdfs)} documento(s) encontrado(s)!")
                    
                    documentos_info = []
                    for idx_doc, pdf in enumerate(pdfs[:10], 1):
                        try:
                            texto = pdf.text.strip()[:60] if pdf.text else "[Sem texto]"
                            href = pdf.get_attribute('href') or "[Sem URL]"
                            
                            print(f"\n   [{idx_doc}] {texto}")
                            print(f"       {href[:70]}...")
                            
                            documentos_info.append({
                                "texto": texto,
                                "href": href
                            })
                            
                            # Tentar baixar
                            if 'pdf' in href.lower():
                                print(f"       ⬇️  Tentando baixar...")
                                try:
                                    pdf.click()
                                    time.sleep(3)
                                    self.oficios_baixados += 1
                                    print(f"       ✅ Download iniciado!")
                                except Exception as e:
                                    print(f"       ⚠️  Erro: {str(e)[:40]}")
                        
                        except Exception as e:
                            print(f"   [{idx_doc}] Erro ao processar: {str(e)[:40]}")
                    
                    resultado = {
                        "numero": numero_processo,
                        "status": "sucesso",
                        "documentos_encontrados": len(pdfs),
                        "documentos": documentos_info,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    print(f"\n   🎯 Status: DOCUMENTOS ENCONTRADOS ✅")
                    
                else:
                    print(f"   ⚠️  Nenhum PDF encontrado na página de requisitórios")
                    
                    resultado = {
                        "numero": numero_processo,
                        "status": "sem_pdfs",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    print(f"   🎯 Status: SEM PDFs")
                
            except Exception as e:
                print(f"   ⚠️  Link de requisitórios não encontrado: {str(e)[:60]}")
                
                resultado = {
                    "numero": numero_processo,
                    "status": "sem_link_requisitorios",
                    "erro": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"   🎯 Status: SEM LINK")
            
            self.resultados.append(resultado)
            return resultado
            
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)[:100]}")
            resultado = {
                "numero": numero_processo,
                "status": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.resultados.append(resultado)
            return resultado
    
    def processar_excel(self, caminho, limite=None):
        print(f"📂 Lendo: {caminho}")
        df = pd.read_excel(caminho)
        
        coluna = None
        for col in df.columns:
            if any(p in col.lower() for p in ['processo', 'numero']):
                coluna = col
                break
        
        if not coluna:
            coluna = df.columns[0]
        
        processos = df[coluna].dropna().tolist()
        
        if limite:
            processos = processos[:limite]
        
        print(f"✅ {len(df)} processos no total")
        print(f"🎯 Processando: {len(processos)}\n")
        
        return processos
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
    
    def salvar_relatorio(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        relatorio_path = Path(f"./resultados/relatorio_final_{timestamp}.json")
        
        relatorio = {
            "timestamp": timestamp,
            "total": len(self.resultados),
            "com_sucesso": len([r for r in self.resultados if r['status'] == 'sucesso']),
            "oficios_baixados": self.oficios_baixados,
            "resultados": self.resultados
        }
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório: {relatorio_path}")
        return relatorio_path

def main():
    if len(sys.argv) < 2:
        print("Uso: python Baixar-Oficios-Final.py <excel> [limite]")
        sys.exit(1)
    
    excel = sys.argv[1]
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print("═"*70)
    print("  DOWNLOAD DE OFÍCIOS - VERSÃO FINAL")
    print("  Usando link correto: abrirConsultaDeRequisitorios")
    print("═"*70)
    print()
    
    downloader = DownloaderOficiosFinal()
    
    try:
        processos = downloader.processar_excel(excel, limite)
        
        if not processos:
            return
        
        downloader.iniciar()
        
        for idx, num in enumerate(processos, 1):
            downloader.buscar_oficios_v2(str(num), idx)
            time.sleep(2)
        
        downloader.salvar_relatorio()
        
        print("\n" + "="*70)
        print("  RESUMO")
        print("="*70)
        print(f"Total: {len(downloader.resultados)}")
        print(f"✅ Sucesso: {len([r for r in downloader.resultados if r['status'] == 'sucesso'])}")
        print(f"📄 Ofícios baixados: {downloader.oficios_baixados}")
        print(f"📁 PDFs: oficios_pdf/")
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido!")
    finally:
        downloader.fechar()
        if downloader.resultados:
            downloader.salvar_relatorio()

if __name__ == "__main__":
    main()
