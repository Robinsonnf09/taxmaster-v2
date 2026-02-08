"""
VERSÃO MELHORADA - Download de Ofícios TJSP com Debug
TAX MASTER Consultoria - 2026
"""
import sys
import os
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_OK = True
except ImportError:
    SELENIUM_OK = False
    print("❌ Erro: Selenium não instalado")
    sys.exit(1)

class DownloaderOficiosDebug:
    """Downloader com debug e screenshots"""
    
    def __init__(self, pasta_destino="./oficios_pdf"):
        self.pasta_destino = Path(pasta_destino)
        self.pasta_destino.mkdir(exist_ok=True)
        
        # Pasta para debug
        self.pasta_debug = Path("./debug_screenshots")
        self.pasta_debug.mkdir(exist_ok=True)
        
        # Configurar Chrome para download automático
        self.chrome_options = Options()
        
        prefs = {
            "download.default_directory": str(self.pasta_destino.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = None
        self.resultados = []
        self.oficios_encontrados_total = 0
        self.documentos_baixados_total = 0
    
    def iniciar_navegador(self):
        """Iniciar Chrome"""
        print("🚀 Iniciando navegador Chrome...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        print("✅ Navegador iniciado!\n")
    
    def construir_url(self, numero_processo):
        """Construir URL de consulta ESAJ"""
        base_url = "https://esaj.tjsp.jus.br/cpopg/search.do"
        params = {
            "conversationId": "",
            "cbPesquisa": "NUMPROC",
            "dadosConsulta.valorConsulta": numero_processo,
            "dadosConsulta.tipoNuProcesso": "UNIFICADO",
            "consultaDeRequisitorios": "true"
        }
        return f"{base_url}?{urlencode(params)}"
    
    def buscar_oficios(self, numero_processo, idx_total):
        """Buscar e analisar ofícios de um processo"""
        print(f"\n{'='*70}")
        print(f"[{idx_total}] 📋 Processo: {numero_processo}")
        print(f"{'='*70}")
        
        url = self.construir_url(numero_processo)
        print(f"🌐 URL: {url[:80]}...")
        
        try:
            # Acessar página
            self.driver.get(url)
            time.sleep(4)
            
            # Screenshot
            numero_limpo = numero_processo.replace('.', '_').replace('-', '_')
            screenshot_path = self.pasta_debug / f"{idx_total:04d}_{numero_limpo}.png"
            self.driver.save_screenshot(str(screenshot_path))
            print(f"📸 Screenshot salvo: {screenshot_path.name}")
            
            # Salvar HTML para análise
            html_path = self.pasta_debug / f"{idx_total:04d}_{numero_limpo}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"💾 HTML salvo: {html_path.name}")
            
            # MÚLTIPLAS ESTRATÉGIAS DE BUSCA
            
            print(f"🔍 Procurando ofícios requisitórios...")
            
            # Estratégia 1: Links específicos de ofícios
            oficios = self.driver.find_elements(
                By.XPATH, 
                "//a[contains(translate(text(), 'ÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑABCDEFGHIJKLMNOPQRSTUVWXYZ', 'aaaaeeeiiooooucnabcdefghijklmnopqrstuvwxyz'), 'oficio') or contains(translate(text(), 'ÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑABCDEFGHIJKLMNOPQRSTUVWXYZ', 'aaaaeeeiiooooucnabcdefghijklmnopqrstuvwxyz'), 'requisitorio')]"
            )
            
            if oficios:
                print(f"   ✅ Estratégia 1: {len(oficios)} link(s) com 'oficio/requisitorio'")
            else:
                # Estratégia 2: Tabela de documentos
                oficios = self.driver.find_elements(
                    By.XPATH,
                    "//table[@id='tabelaTodasMovimentacoes']//a[contains(@href, 'pdf')] | //table[@id='tabelaDocumentosProcesso']//a"
                )
                if oficios:
                    print(f"   ✅ Estratégia 2: {len(oficios)} documento(s) na tabela")
            
            if not oficios:
                # Estratégia 3: Qualquer link PDF
                oficios = self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(@href, '.pdf') or contains(@onclick, 'pdf') or contains(@href, 'downloadPdf')]"
                )
                if oficios:
                    print(f"   ✅ Estratégia 3: {len(oficios)} link(s) PDF genérico(s)")
            
            if not oficios:
                # Estratégia 4: Iframes com PDFs
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    print(f"   ✅ Estratégia 4: {len(iframes)} iframe(s) encontrado(s)")
                    oficios = iframes
            
            # Processar documentos encontrados
            if oficios:
                self.oficios_encontrados_total += len(oficios)
                
                print(f"\n   📄 Total de documentos encontrados: {len(oficios)}")
                print(f"   🔗 Analisando links:\n")
                
                links_info = []
                for idx, oficio in enumerate(oficios[:10], 1):  # Limitar a 10 para não poluir
                    try:
                        texto = oficio.text.strip()[:60] if oficio.text else "[Sem texto]"
                        href = oficio.get_attribute('href') or oficio.get_attribute('src') or "[Sem URL]"
                        href_resumido = href[:70] + "..." if len(href) > 70 else href
                        
                        print(f"      [{idx}] {texto}")
                        print(f"          {href_resumido}\n")
                        
                        links_info.append({
                            "texto": texto,
                            "href": href
                        })
                    except Exception as e:
                        print(f"      [{idx}] Erro ao analisar: {str(e)[:50]}\n")
                
                # Tentar baixar o primeiro documento (teste)
                baixado = False
                if oficios:
                    try:
                        print(f"   ⬇️  Tentando baixar primeiro documento...")
                        oficios[0].click()
                        time.sleep(5)
                        
                        # Verificar se baixou
                        pdfs_baixados = list(self.pasta_destino.glob("*.pdf"))
                        if pdfs_baixados:
                            baixado = True
                            self.documentos_baixados_total += 1
                            print(f"   ✅ Documento baixado com sucesso!")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao baixar: {str(e)[:60]}")
                
                resultado = {
                    "numero": numero_processo,
                    "status": "encontrado",
                    "documentos_encontrados": len(oficios),
                    "documento_baixado": baixado,
                    "links": links_info,
                    "screenshot": str(screenshot_path),
                    "html": str(html_path),
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"\n   🎯 Status: DOCUMENTOS ENCONTRADOS")
                
            else:
                print(f"   ⚠️  Nenhum documento encontrado")
                
                # Informações da página
                titulo = self.driver.title
                url_atual = self.driver.current_url
                
                print(f"   📄 Título: {titulo}")
                print(f"   🔗 URL: {url_atual[:70]}...")
                
                # Verificar se há mensagem de erro
                try:
                    mensagem_erro = self.driver.find_element(By.CLASS_NAME, "mensagemErro").text
                    print(f"   ⚠️  Mensagem: {mensagem_erro[:100]}")
                except:
                    mensagem_erro = None
                
                resultado = {
                    "numero": numero_processo,
                    "status": "sem_documentos",
                    "titulo_pagina": titulo,
                    "url_final": url_atual,
                    "mensagem_erro": mensagem_erro,
                    "screenshot": str(screenshot_path),
                    "html": str(html_path),
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"   🎯 Status: SEM DOCUMENTOS")
            
            self.resultados.append(resultado)
            return resultado
            
        except Exception as e:
            print(f"   ❌ ERRO CRÍTICO: {str(e)[:100]}")
            resultado = {
                "numero": numero_processo,
                "status": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.resultados.append(resultado)
            return resultado
    
    def processar_excel(self, caminho_excel, limite=None):
        """Ler processos do Excel"""
        print(f"📂 Lendo Excel: {caminho_excel}")
        
        try:
            df = pd.read_excel(caminho_excel)
            print(f"✅ {len(df)} processos encontrados")
            print(f"📊 Colunas: {', '.join(df.columns.tolist())}\n")
            
            # Identificar coluna de processo
            coluna_processo = None
            for col in df.columns:
                if any(p in col.lower() for p in ['processo', 'numero', 'num', 'nº']):
                    coluna_processo = col
                    break
            
            if not coluna_processo:
                coluna_processo = df.columns[0]
            
            print(f"🎯 Usando coluna: '{coluna_processo}'\n")
            
            processos = df[coluna_processo].dropna().tolist()
            
            if limite:
                processos = processos[:limite]
                print(f"⚠️  MODO TESTE: Limitado a {limite} processos\n")
            
            return processos
            
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {str(e)}")
            return []
    
    def fechar(self):
        """Fechar navegador"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")
    
    def salvar_relatorio(self):
        """Salvar relatório JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        relatorio_path = Path(f"./resultados/relatorio_debug_{timestamp}.json")
        
        relatorio = {
            "timestamp": timestamp,
            "total_processos_analisados": len(self.resultados),
            "documentos_encontrados_total": self.oficios_encontrados_total,
            "documentos_baixados_total": self.documentos_baixados_total,
            "processos_com_documentos": len([r for r in self.resultados if r.get('status') == 'encontrado']),
            "processos_sem_documentos": len([r for r in self.resultados if r.get('status') == 'sem_documentos']),
            "processos_com_erro": len([r for r in self.resultados if r.get('status') == 'erro']),
            "detalhes": self.resultados
        }
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo: {relatorio_path}")
        return relatorio_path

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python Baixar-Oficios-Debug.py <arquivo_excel> [limite_processos]")
        print("\nExemplo:")
        print("  python Baixar-Oficios-Debug.py processos.xlsx 10")
        sys.exit(1)
    
    caminho_excel = sys.argv[1]
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print("═"*70)
    print("  DOWNLOAD DE OFÍCIOS REQUISITÓRIOS - MODO DEBUG")
    print("  TAX MASTER Consultoria")
    print("  Com Screenshots e Análise Detalhada")
    print("═"*70)
    print()
    
    downloader = DownloaderOficiosDebug()
    
    try:
        # Ler processos
        processos = downloader.processar_excel(caminho_excel, limite)
        
        if not processos:
            print("❌ Nenhum processo para processar")
            return
        
        print(f"🎯 Total de processos a analisar: {len(processos)}\n")
        
        # Confirmar
        if not limite or limite > 20:
            print("⚠️  Pressione ENTER para continuar ou CTRL+C para cancelar...")
            input()
        
        # Iniciar navegador
        downloader.iniciar_navegador()
        
        # Processar cada processo
        for idx, numero in enumerate(processos, 1):
            downloader.buscar_oficios(str(numero), idx)
            time.sleep(2)  # Pausa entre processos
        
        # Salvar relatório
        downloader.salvar_relatorio()
        
        # Resumo final
        print("\n" + "="*70)
        print("  RESUMO FINAL")
        print("="*70)
        print(f"📊 Total analisado: {len(downloader.resultados)}")
        print(f"✅ Com documentos: {len([r for r in downloader.resultados if r.get('status') == 'encontrado'])}")
        print(f"📄 Total documentos encontrados: {downloader.oficios_encontrados_total}")
        print(f"⬇️  Documentos baixados: {downloader.documentos_baixados_total}")
        print(f"⚠️  Sem documentos: {len([r for r in downloader.resultados if r.get('status') == 'sem_documentos'])}")
        print(f"❌ Com erro: {len([r for r in downloader.resultados if r.get('status') == 'erro'])}")
        print(f"\n📁 Screenshots: debug_screenshots/")
        print(f"📁 PDFs: oficios_pdf/")
        print(f"📊 Relatório: resultados/relatorio_debug_*.json\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário!")
        print(f"📊 Processos analisados até agora: {len(downloader.resultados)}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
    finally:
        downloader.fechar()
        if downloader.resultados:
            downloader.salvar_relatorio()
    
    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    main()
