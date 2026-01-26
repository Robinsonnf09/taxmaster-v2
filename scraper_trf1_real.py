"""
Scraper REAL para TRF1 - Consulta Pública PJe
Busca e baixa ofícios requisitórios de verdade
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import requests

class ScraperTRF1Real:
    def __init__(self):
        self.base_url = "https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam"
        self.driver = None
    
    def iniciar_navegador(self):
        """Inicia Chrome com configurações otimizadas"""
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Download automático
        prefs = {
            "download.default_directory": os.path.join(os.getcwd(), "oficios_baixados"),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def buscar_processo_real(self, numero_processo):
        """Busca REAL no PJe"""
        try:
            if not self.driver:
                self.iniciar_navegador()
            
            print(f"\n🔍 Buscando processo real: {numero_processo}")
            
            # Acessar consulta pública
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # Limpar número do processo
            numero_limpo = numero_processo.replace('.', '').replace('-', '').replace('/', '')
            
            # Preencher campo de busca
            wait = WebDriverWait(self.driver, 10)
            
            # Campo: Número do Processo
            campo_numero = wait.until(
                EC.presence_of_element_located((By.ID, "fPP:numeroProcesso:numeroSequencial"))
            )
            campo_numero.clear()
            campo_numero.send_keys(numero_limpo[:7])  # Primeiros 7 dígitos
            
            # Digito verificador
            campo_digito = self.driver.find_element(By.ID, "fPP:numeroProcesso:digitoVerificador")
            campo_digito.send_keys(numero_limpo[7:9])
            
            # Ano
            campo_ano = self.driver.find_element(By.ID, "fPP:numeroProcesso:ano")
            campo_ano.send_keys(numero_limpo[9:13])
            
            # Segmento
            campo_segmento = self.driver.find_element(By.ID, "fPP:numeroProcesso:segmento")
            campo_segmento.send_keys(numero_limpo[13:14])
            
            # Tribunal
            campo_tribunal = self.driver.find_element(By.ID, "fPP:numeroProcesso:tribunal")
            campo_tribunal.send_keys(numero_limpo[14:18])
            
            # Origem
            campo_origem = self.driver.find_element(By.ID, "fPP:numeroProcesso:origem")
            campo_origem.send_keys(numero_limpo[18:22])
            
            print("✅ Campos preenchidos")
            
            # Clicar em Pesquisar
            btn_pesquisar = self.driver.find_element(By.ID, "fPP:searchProcessos")
            btn_pesquisar.click()
            
            time.sleep(3)
            
            # Verificar se encontrou
            try:
                resultado = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rich-table-row"))
                )
                print("✅ Processo encontrado!")
                
                # Clicar no processo para ver detalhes
                resultado.click()
                time.sleep(2)
                
                return {
                    'sucesso': True,
                    'encontrado': True,
                    'mensagem': 'Processo encontrado no PJe'
                }
                
            except:
                print("❌ Processo não encontrado")
                return {
                    'sucesso': False,
                    'encontrado': False,
                    'mensagem': 'Processo não encontrado no PJe'
                }
        
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def buscar_oficio_na_pagina(self):
        """Procura ofício requisitório nos documentos"""
        try:
            print("\n📄 Buscando ofício requisitório...")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Ir para aba de documentos
            try:
                aba_docs = wait.until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Documentos"))
                )
                aba_docs.click()
                time.sleep(2)
            except:
                print("⚠️  Não encontrou aba de documentos")
            
            # Procurar por "Ofício Requisitório" ou "Requisição de Pagamento"
            documentos = self.driver.find_elements(By.CLASS_NAME, "documento-link")
            
            for doc in documentos:
                texto = doc.text.lower()
                if 'ofício' in texto or 'requisitório' in texto or 'requisição' in texto:
                    print(f"✅ Ofício encontrado: {doc.text}")
                    return {
                        'sucesso': True,
                        'encontrado': True,
                        'documento': doc.text,
                        'elemento': doc
                    }
            
            print("❌ Ofício requisitório não encontrado nos documentos")
            return {
                'sucesso': False,
                'encontrado': False,
                'mensagem': 'Ofício não encontrado'
            }
        
        except Exception as e:
            print(f"❌ Erro ao buscar ofício: {str(e)}")
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def baixar_oficio(self, elemento_documento, numero_processo):
        """Baixa o ofício requisitório"""
        try:
            print("\n⬇️  Baixando ofício...")
            
            # Clicar no documento
            elemento_documento.click()
            time.sleep(3)
            
            # Aguardar download
            pasta_download = os.path.join(os.getcwd(), "oficios_baixados")
            os.makedirs(pasta_download, exist_ok=True)
            
            # Aguardar arquivo aparecer na pasta
            for i in range(10):
                arquivos = os.listdir(pasta_download)
                if arquivos:
                    arquivo_baixado = arquivos[-1]  # Último arquivo
                    print(f"✅ Ofício baixado: {arquivo_baixado}")
                    
                    # Renomear com número do processo
                    novo_nome = f"oficio_{numero_processo.replace('/', '_')}.pdf"
                    caminho_antigo = os.path.join(pasta_download, arquivo_baixado)
                    caminho_novo = os.path.join(pasta_download, novo_nome)
                    
                    os.rename(caminho_antigo, caminho_novo)
                    
                    return {
                        'sucesso': True,
                        'arquivo': caminho_novo
                    }
                
                time.sleep(1)
            
            return {
                'sucesso': False,
                'erro': 'Timeout ao aguardar download'
            }
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def executar_busca_completa(self, numero_processo):
        """Execução completa: buscar processo + ofício + baixar"""
        try:
            # 1. Buscar processo
            resultado_busca = self.buscar_processo_real(numero_processo)
            
            if not resultado_busca.get('encontrado'):
                return resultado_busca
            
            # 2. Buscar ofício
            resultado_oficio = self.buscar_oficio_na_pagina()
            
            if not resultado_oficio.get('encontrado'):
                return resultado_oficio
            
            # 3. Baixar ofício
            resultado_download = self.baixar_oficio(
                resultado_oficio['elemento'],
                numero_processo
            )
            
            return resultado_download
        
        finally:
            if self.driver:
                self.driver.quit()

# Teste
if __name__ == "__main__":
    scraper = ScraperTRF1Real()
    
    # Processo de exemplo (use um processo real público)
    numero = "0000000-00.0000.4.01.0000"  # SUBSTITUA por processo real
    
    resultado = scraper.executar_busca_completa(numero)
    print(f"\n📊 Resultado final: {resultado}")
