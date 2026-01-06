"""
Buscador Avançado de Ofícios Requisitórios - TJSP
Versão Corrigida com Melhor Detecção
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from pathlib import Path
import logging
from datetime import datetime
import sys

# Configurar encoding UTF-8 para evitar erros
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('buscador_oficios.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BuscadorOficioTJSP:
    """Classe para buscar e baixar ofícios requisitórios do TJSP"""
    
    def __init__(self, headless=False):
        self.downloads_dir = Path("data/oficios")
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def iniciar_driver(self):
        """Inicializa o Chrome WebDriver"""
        logger.info("="*60)
        logger.info("Iniciando Chrome WebDriver...")
        logger.info("="*60)
        
        options = webdriver.ChromeOptions()
        
        prefs = {
            "download.default_directory": str(self.downloads_dir.absolute()),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        if self.headless:
            options.add_argument("--headless=new")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        self.wait = WebDriverWait(self.driver, 30)
        
        logger.info("OK Chrome WebDriver iniciado")
    
    def buscar_processo(self, numero_processo, processo_principal=None):
        """Busca o processo - VERSÃO MELHORADA"""
        logger.info("\n" + "="*60)
        logger.info(f"PASSO 1: Buscando processo")
        logger.info("="*60)
        
        processos_para_tentar = [numero_processo]
        if processo_principal:
            processos_para_tentar.append(processo_principal)
        
        for i, processo in enumerate(processos_para_tentar):
            logger.info(f"\nTentativa {i+1}: {processo}")
            
            try:
                self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
                time.sleep(3)
                
                partes = processo.split('.')
                if len(partes) < 5:
                    continue
                
                parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
                parte2 = partes[4]
                
                logger.info(f"Preenchendo: {parte1} / {parte2}")
                
                self.driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
                self.driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
                
                screenshot_path = self.downloads_dir / f"busca_{i+1}_preenchido.png"
                self.driver.save_screenshot(str(screenshot_path))
                
                self.driver.find_element(By.ID, "botaoConsultarProcessos").click()
                time.sleep(5)
                
                screenshot_path = self.downloads_dir / f"busca_{i+1}_resultado.png"
                self.driver.save_screenshot(str(screenshot_path))
                
                # VERIFICAÇÃO MELHORADA
                page_source = self.driver.page_source
                
                # Verificar se NÃO tem mensagens de erro
                mensagens_erro = [
                    "não encontrado",
                    "não existem",
                    "nenhum processo",
                    "não foi possível"
                ]
                
                tem_erro = any(msg in page_source.lower() for msg in mensagens_erro)
                
                # Verificar se TEM indicadores de sucesso
                indicadores_sucesso = [
                    "processo",
                    "assunto",
                    "classe",
                    "área",
                    "distribuição"
                ]
                
                tem_sucesso = sum(1 for ind in indicadores_sucesso if ind in page_source.lower()) >= 3
                
                logger.info(f"Tem erro: {tem_erro}, Tem sucesso: {tem_sucesso}")
                
                if not tem_erro and tem_sucesso:
                    logger.info(f"OK Processo encontrado: {processo}")
                    return True
                else:
                    logger.warning(f"Processo nao encontrado: {processo}")
                    logger.info(f"Verifique screenshot: {screenshot_path}")
                    
            except Exception as e:
                logger.error(f"Erro: {str(e)}")
        
        # Se não encontrou, deixar usuário verificar
        logger.warning("\nProcesso nao encontrado automaticamente")
        print("\n" + "="*60)
        print("VERIFICACAO MANUAL NECESSARIA")
        print("="*60)
        print("\nO navegador esta aberto. Verifique:")
        print("1. Os screenshots em data/oficios/")
        print("2. Se o processo apareceu na tela do navegador")
        print("\nSe o processo APARECEU, pressione ENTER para continuar...")
        print("Se NAO apareceu, feche esta janela (Ctrl+C)")
        
        resposta = input("\nProcesso apareceu na tela? (s/n): ").lower()
        
        if resposta == 's':
            logger.info("Usuario confirmou que processo foi encontrado")
            return True
        
        return False
    
    def acessar_pasta_digital(self):
        """Acessa a Pasta Digital"""
        logger.info("\n" + "="*60)
        logger.info("PASSO 2: Acessando Pasta Digital...")
        logger.info("="*60)
        
        try:
            # Procurar link
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            link_encontrado = None
            
            for link in links:
                try:
                    texto = link.text.strip().lower()
                    href = link.get_attribute("href") or ""
                    
                    if ("visualizar" in texto and "auto" in texto) or \
                       "pasta digital" in texto or \
                       "pastadigital" in href.lower():
                        link_encontrado = link
                        logger.info(f"OK Link encontrado: {link.text.strip()}")
                        break
                except:
                    pass
            
            if not link_encontrado:
                print("\nClique manualmente em 'Visualizar Autos' ou 'Pasta Digital'")
                print("Depois pressione ENTER...")
                input()
                return True
            
            janelas_antes = self.driver.window_handles
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link_encontrado)
            time.sleep(1)
            link_encontrado.click()
            time.sleep(5)
            
            janelas_depois = self.driver.window_handles
            
            if len(janelas_depois) > len(janelas_antes):
                logger.info("OK Nova janela aberta")
                nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                self.driver.switch_to.window(nova_janela)
                time.sleep(3)
            
            # Verificar autenticação
            if "login" in self.driver.current_url.lower() or "validacao" in self.driver.current_url.lower():
                logger.info("\n" + "="*60)
                logger.info("AUTENTICACAO NECESSARIA")
                logger.info("="*60)
                
                print("\nFaca login e valide com codigo de e-mail")
                print("Depois pressione ENTER...")
                
                self.driver.save_screenshot(str(self.downloads_dir / "autenticacao.png"))
                
                input()
                
                logger.info("Continuando apos autenticacao...")
                time.sleep(3)
            
            self.driver.save_screenshot(str(self.downloads_dir / "pasta_digital.png"))
            
            return True
            
        except Exception as e:
            logger.error(f"Erro: {str(e)}")
            return False
    
    def buscar_e_baixar_oficio(self):
        """Busca e baixa o ofício"""
        logger.info("\n" + "="*60)
        logger.info("PASSO 3: Buscando oficio nos documentos...")
        logger.info("="*60)
        
        try:
            time.sleep(5)
            
            # Buscar elementos com "oficio"
            todos_elementos = self.driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ÁÉÍÓÚÂÊÔÃÕÇ', 'aeiouaeoaoc'), 'oficio')]")
            
            logger.info(f"Elementos com 'oficio' encontrados: {len(todos_elementos)}")
            
            oficios = []
            
            for elem in todos_elementos:
                try:
                    texto = elem.text.strip()
                    if texto and elem.is_displayed():
                        logger.info(f"Documento: {texto[:60]}")
                        oficios.append(elem)
                except:
                    pass
            
            if not oficios:
                print("\nProcure manualmente pelo 'Oficio' na arvore de documentos")
                print("Clique no documento para visualizar")
                print("Depois pressione ENTER...")
                input()
            else:
                # Clicar no primeiro ofício
                logger.info(f"\nClicando no oficio...")
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", oficios[0])
                time.sleep(1)
                oficios[0].click()
                time.sleep(5)
            
            # Aguardar download
            logger.info("Aguardando download...")
            time.sleep(10)
            
            # Verificar arquivos
            arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
            
            if arquivos_pdf:
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                
                if time.time() - arquivo_mais_recente.stat().st_mtime < 60:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    novo_nome = f"oficio_TJSP_{timestamp}.pdf"
                    novo_caminho = self.downloads_dir / novo_nome
                    
                    arquivo_mais_recente.rename(novo_caminho)
                    
                    logger.info(f"OK OFICIO BAIXADO: {novo_caminho}")
                    
                    return {
                        "sucesso": True,
                        "caminho": str(novo_caminho),
                        "mensagem": "Oficio baixado com sucesso"
                    }
            
            print("\nSe o PDF abriu em nova aba, salve manualmente em data/oficios/")
            print("Pressione ENTER quando terminar...")
            input()
            
            # Verificar novamente
            arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
            if arquivos_pdf:
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                if time.time() - arquivo_mais_recente.stat().st_mtime < 120:
                    return {
                        "sucesso": True,
                        "caminho": str(arquivo_mais_recente),
                        "mensagem": "Oficio salvo"
                    }
            
            return {
                "sucesso": False,
                "erro": "download_nao_realizado",
                "mensagem": "Download nao confirmado"
            }
            
        except Exception as e:
            logger.error(f"Erro: {str(e)}")
            return {
                "sucesso": False,
                "erro": "erro_download",
                "mensagem": str(e)
            }
    
    def executar(self, numero_processo, processo_principal=None):
        """Executa o fluxo completo"""
        try:
            if not self.driver:
                self.iniciar_driver()
            
            if not self.buscar_processo(numero_processo, processo_principal):
                return {
                    "sucesso": False,
                    "erro": "processo_nao_encontrado",
                    "mensagem": "Processo nao encontrado"
                }
            
            if not self.acessar_pasta_digital():
                return {
                    "sucesso": False,
                    "erro": "pasta_digital_inacessivel",
                    "mensagem": "Nao foi possivel acessar Pasta Digital"
                }
            
            resultado = self.buscar_e_baixar_oficio()
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na execucao: {str(e)}", exc_info=True)
            
            print("\nNavegador ficara aberto para inspecao...")
            print("Pressione ENTER para fechar...")
            input()
            
            return {
                "sucesso": False,
                "erro": "erro_geral",
                "mensagem": str(e)
            }
    
    def fechar(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver fechado")

def main():
    """Função principal"""
    buscador = BuscadorOficioTJSP(headless=False)
    
    try:
        processo_execucao = "0034565-98.2018.8.26.0053"
        processo_principal = "0048680-71.2011.8.26.0053"
        
        print(f"\n{'='*60}")
        print("BUSCADOR DE OFICIOS REQUISITORIOS - TJSP")
        print("Versao Corrigida")
        print(f"Processo Execucao: {processo_execucao}")
        print(f"Processo Principal: {processo_principal}")
        print('='*60)
        
        resultado = buscador.executar(processo_execucao, processo_principal)
        
        print(f"\n{'='*60}")
        print("RESULTADO FINAL:")
        print(f"Sucesso: {resultado['sucesso']}")
        
        if resultado['sucesso']:
            print(f"OK Arquivo: {resultado['caminho']}")
            print(f"OK {resultado['mensagem']}")
        else:
            print(f"ERRO: {resultado.get('erro')}")
            print(f"Mensagem: {resultado['mensagem']}")
        
        print('='*60)
        
    finally:
        buscador.fechar()

if __name__ == "__main__":
    main()
