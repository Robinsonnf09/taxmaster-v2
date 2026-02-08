"""
Sistema de Download Automático de Ofícios Requisitórios - TJSP ESAJ
Autor: TAX MASTER Consultoria
Data: 2026-01-28
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
    print("❌ Selenium não instalado. Execute: pip install selenium webdriver-manager")
    sys.exit(1)

class DownloaderOficiosTJSP:
    """Classe para download automático de ofícios requisitórios"""
    
    def __init__(self, pasta_destino="./oficios_pdf"):
        self.pasta_destino = Path(pasta_destino)
        self.pasta_destino.mkdir(exist_ok=True)
        
        # Configurar Chrome
        self.chrome_options = Options()
        
        # Configurar download automático
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
    
    def iniciar_navegador(self):
        """Inicializar Chrome com Selenium"""
        print("🚀 Iniciando navegador Chrome...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        print("✅ Navegador iniciado!")
    
    def construir_url(self, numero_processo):
        """Construir URL de consulta ESAJ TJSP"""
        # Remover formatação do número
        numero_limpo = numero_processo.replace("-", "").replace(".", "")
        
        base_url = "https://esaj.tjsp.jus.br/cpopg/search.do"
        params = {
            "conversationId": "",
            "cbPesquisa": "NUMPROC",
            "numeroDigitoAnoUnificado": "",
            "foroNumeroUnificado": "",
            "dadosConsulta.valorConsultaNuUnificado": "",
            "dadosConsulta.valorConsultaNuUnificado": "UNIFICADO",
            "dadosConsulta.valorConsulta": numero_processo,
            "dadosConsulta.tipoNuProcesso": "SAJ",
            "consultaDeRequisitorios": "true"
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    def buscar_oficios(self, numero_processo):
        """Buscar e baixar ofícios de um processo"""
        print(f"\n{'='*60}")
        print(f"📋 Processo: {numero_processo}")
        print(f"{'='*60}")
        
        url = self.construir_url(numero_processo)
        print(f"🌐 Acessando: {url[:80]}...")
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Aguardar carregamento
            
            # Verificar se encontrou o processo
            try:
                # Procurar por ofícios requisitórios
                oficios = self.driver.find_elements(
                    By.XPATH, 
                    "//a[contains(@href, 'oficioRequisitorio') or contains(text(), 'Ofício')]"
                )
                
                if oficios:
                    print(f"✅ Encontrados {len(oficios)} ofício(s) requisitório(s)!")
                    
                    pasta_processo = self.pasta_destino / numero_processo.replace(".", "_").replace("-", "_")
                    pasta_processo.mkdir(exist_ok=True)
                    
                    oficios_baixados = []
                    
                    for idx, oficio in enumerate(oficios, 1):
                        try:
                            print(f"  [{idx}/{len(oficios)}] Baixando ofício...")
                            
                            # Clicar no link do ofício
                            oficio.click()
                            time.sleep(5)  # Aguardar download
                            
                            # Procurar arquivo baixado
                            arquivos = list(self.pasta_destino.glob("*.pdf"))
                            if arquivos:
                                ultimo_arquivo = max(arquivos, key=lambda x: x.stat().st_mtime)
                                
                                # Renomear arquivo
                                novo_nome = pasta_processo / f"oficio_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                ultimo_arquivo.rename(novo_nome)
                                
                                oficios_baixados.append(str(novo_nome))
                                print(f"    ✅ Salvo: {novo_nome.name}")
                            
                            # Voltar para página anterior
                            self.driver.back()
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f"    ⚠️  Erro ao baixar ofício {idx}: {str(e)[:50]}")
                    
                    resultado = {
                        "numero": numero_processo,
                        "status": "sucesso",
                        "oficios_encontrados": len(oficios),
                        "oficios_baixados": len(oficios_baixados),
                        "arquivos": oficios_baixados,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    print(f"✅ Total baixado: {len(oficios_baixados)}")
                    
                else:
                    print("⚠️  Nenhum ofício requisitório encontrado")
                    resultado = {
                        "numero": numero_processo,
                        "status": "sem_oficios",
                        "oficios_encontrados": 0,
                        "timestamp": datetime.now().isoformat()
                    }
                
            except Exception as e:
                print(f"⚠️  Erro ao procurar ofícios: {str(e)[:100]}")
                resultado = {
                    "numero": numero_processo,
                    "status": "erro",
                    "erro": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            self.resultados.append(resultado)
            return resultado
            
        except Exception as e:
            print(f"❌ Erro crítico: {str(e)[:100]}")
            resultado = {
                "numero": numero_processo,
                "status": "erro_critico",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.resultados.append(resultado)
            return resultado
    
    def processar_excel(self, caminho_excel):
        """Processar lista de processos do Excel"""
        print(f"📂 Lendo Excel: {caminho_excel}")
        
        try:
            df = pd.read_excel(caminho_excel)
            print(f"✅ {len(df)} processos encontrados no Excel")
            print(f"📊 Colunas disponíveis: {', '.join(df.columns.tolist())}")
            
            # Tentar identificar coluna com números de processos
            coluna_processo = None
            for col in df.columns:
                if any(palavra in col.lower() for palavra in ['processo', 'numero', 'nº', 'num']):
                    coluna_processo = col
                    break
            
            if not coluna_processo:
                # Usar primeira coluna
                coluna_processo = df.columns[0]
            
            print(f"🎯 Usando coluna: '{coluna_processo}'")
            print("")
            
            numeros_processos = df[coluna_processo].dropna().tolist()
            
            return numeros_processos
            
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {str(e)}")
            return []
    
    def fechar(self):
        """Fechar navegador"""
        if self.driver:
            self.driver.quit()
            print("🔒 Navegador fechado")
    
    def salvar_relatorio(self):
        """Salvar relatório JSON"""
        relatorio_path = f"./resultados/relatorio_oficios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_processos": len(self.resultados),
                "com_sucesso": len([r for r in self.resultados if r['status'] == 'sucesso']),
                "sem_oficios": len([r for r in self.resultados if r['status'] == 'sem_oficios']),
                "com_erro": len([r for r in self.resultados if 'erro' in r['status']]),
                "resultados": self.resultados
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo: {relatorio_path}")
        return relatorio_path

def main():
    if len(sys.argv) < 2:
        print("Uso: python Baixar-Oficios-TJSP.py <caminho_excel>")
        print("Exemplo: python Baixar-Oficios-TJSP.py processos_push_20260126_185045.xlsx")
        sys.exit(1)
    
    caminho_excel = sys.argv[1]
    
    print("═══════════════════════════════════════════")
    print("  DOWNLOAD DE OFÍCIOS REQUISITÓRIOS TJSP")
    print("  TAX MASTER Consultoria")
    print("═══════════════════════════════════════════")
    print("")
    
    downloader = DownloaderOficiosTJSP()
    
    try:
        # Processar Excel
        processos = downloader.processar_excel(caminho_excel)
        
        if not processos:
            print("❌ Nenhum processo encontrado no Excel")
            return
        
        print(f"🎯 Total de processos a processar: {len(processos)}")
        print("")
        
        # Iniciar navegador
        downloader.iniciar_navegador()
        
        # Processar cada processo
        for idx, numero in enumerate(processos, 1):
            print(f"\n[{idx}/{len(processos)}] Processando...")
            downloader.buscar_oficios(str(numero))
            time.sleep(2)  # Pausa entre processos
        
        # Salvar relatório
        downloader.salvar_relatorio()
        
        # Resumo final
        print("\n" + "="*60)
        print("  RESUMO FINAL")
        print("="*60)
        print(f"Total processado: {len(downloader.resultados)}")
        print(f"✅ Com sucesso: {len([r for r in downloader.resultados if r['status'] == 'sucesso'])}")
        print(f"⚠️  Sem ofícios: {len([r for r in downloader.resultados if r['status'] == 'sem_oficios'])}")
        print(f"❌ Com erro: {len([r for r in downloader.resultados if 'erro' in r['status']])}")
        print(f"\n📁 Ofícios salvos em: ./oficios_pdf/")
        print("")
        
    finally:
        downloader.fechar()
    
    print("✅ Processamento concluído!")

if __name__ == "__main__":
    main()
