"""
Robô de Busca de Ofícios Requisitórios - TJSP
Versão Final e Robusta
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BuscadorOficioTJSP:
    """Classe para buscar e baixar ofícios requisitórios do TJSP"""
    
    def __init__(self, headless=False):
        self.downloads_dir = Path("data/oficios")
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
    
    def iniciar_driver(self):
        """Inicializa o driver do Chrome"""
        logger.info("Iniciando Chrome WebDriver...")
        
        options = webdriver.ChromeOptions()
        
        # Configurar diretório de download
        prefs = {
            "download.default_directory": str(self.downloads_dir.absolute()),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        # Configurações adicionais
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(10)
        
        logger.info("Chrome WebDriver iniciado com sucesso")
    
    def buscar_oficio(self, numero_processo):
        """
        Busca e baixa o ofício requisitório de um processo do TJSP
        
        Args:
            numero_processo: Número do processo no formato NNNNNNN-DD.AAAA.J.TR.OOOO
            
        Returns:
            dict: {"sucesso": bool, "caminho": str, "mensagem": str}
        """
        logger.info(f"Iniciando busca de ofício - Processo: {numero_processo}")
        
        try:
            if not self.driver:
                self.iniciar_driver()
            
            # Separar número do processo
            partes = numero_processo.split('.')
            if len(partes) < 5:
                return {
                    "sucesso": False,
                    "erro": "formato_invalido",
                    "mensagem": f"Formato de processo inválido: {numero_processo}"
                }
            
            parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
            parte2 = partes[4]
            
            logger.info(f"Processo separado: {parte1} / {parte2}")
            
            # PASSO 1: Acessar consulta processual normal para verificar se existe
            logger.info("PASSO 1: Verificando se o processo existe...")
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(3)
            
            self.driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
            self.driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
            self.driver.find_element(By.ID, "botaoConsultarProcessos").click()
            
            time.sleep(5)
            self.driver.save_screenshot(str(self.downloads_dir / f"verif_{numero_processo.replace('.', '_')}.png"))
            
            page_source = self.driver.page_source.lower()
            
            if "não encontrado" in page_source or "não existem" in page_source:
                logger.warning("Processo não encontrado na consulta processual")
                return {
                    "sucesso": False,
                    "erro": "processo_nao_existe",
                    "mensagem": f"Processo {numero_processo} não existe no TJSP"
                }
            
            logger.info("✅ Processo existe no TJSP")
            
            # PASSO 2: Acessar consulta de requisitórios
            logger.info("PASSO 2: Acessando consulta de requisitórios...")
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do")
            time.sleep(3)
            
            self.driver.find_element(By.ID, "numeroDigitoAnoUnificado").clear()
            self.driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
            
            self.driver.find_element(By.ID, "foroNumeroUnificado").clear()
            self.driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
            
            self.driver.save_screenshot(str(self.downloads_dir / f"req_preenchido_{numero_processo.replace('.', '_')}.png"))
            
            self.driver.find_element(By.ID, "botaoConsultarProcessos").click()
            time.sleep(5)
            
            self.driver.save_screenshot(str(self.downloads_dir / f"req_resultado_{numero_processo.replace('.', '_')}.png"))
            
            page_source = self.driver.page_source.lower()
            
            if "não encontrado" in page_source or "não existem" in page_source:
                logger.warning("Processo não tem requisitórios cadastrados")
                return {
                    "sucesso": False,
                    "erro": "sem_requisitorios",
                    "mensagem": f"Processo {numero_processo} não tem ofícios requisitórios cadastrados"
                }
            
            logger.info("✅ Requisitórios encontrados")
            
            # PASSO 3: Procurar e clicar no link de visualização
            logger.info("PASSO 3: Procurando link de visualização...")
            
            link_visualizar = None
            
            # Estratégia 1: Por texto
            try:
                link_visualizar = self.driver.find_element(By.LINK_TEXT, "Visualizar")
                logger.info("Link encontrado por texto")
            except NoSuchElementException:
                pass
            
            # Estratégia 2: Por href
            if not link_visualizar:
                try:
                    link_visualizar = self.driver.find_element(By.CSS_SELECTOR, "a[href*='abrirDownload']")
                    logger.info("Link encontrado por href")
                except NoSuchElementException:
                    pass
            
            # Estratégia 3: Buscar em todos os links
            if not link_visualizar:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    texto = link.text.strip().lower()
                    href = link.get_attribute("href") or ""
                    
                    if "visualizar" in texto or "download" in href.lower():
                        link_visualizar = link
                        logger.info(f"Link encontrado: {texto} | {href}")
                        break
            
            if not link_visualizar:
                logger.error("Link de visualização não encontrado")
                return {
                    "sucesso": False,
                    "erro": "link_nao_encontrado",
                    "mensagem": "Link de visualização do ofício não encontrado"
                }
            
            # PASSO 4: Clicar no link e capturar download
            logger.info("PASSO 4: Clicando no link de visualização...")
            
            janelas_antes = self.driver.window_handles
            
            # Scroll até o elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link_visualizar)
            time.sleep(1)
            
            # Clicar
            link_visualizar.click()
            time.sleep(5)
            
            # Verificar se abriu nova janela
            janelas_depois = self.driver.window_handles
            
            if len(janelas_depois) > len(janelas_antes):
                logger.info("Nova janela/aba aberta")
                nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                self.driver.switch_to.window(nova_janela)
                time.sleep(3)
                
                logger.info(f"URL da nova janela: {self.driver.current_url}")
                self.driver.save_screenshot(str(self.downloads_dir / f"visualizacao_{numero_processo.replace('.', '_')}.png"))
                
                self.driver.close()
                self.driver.switch_to.window(janelas_antes[0])
            
            # PASSO 5: Verificar se o arquivo foi baixado
            logger.info("PASSO 5: Verificando download...")
            time.sleep(5)
            
            arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
            
            if arquivos_pdf:
                # Pegar o arquivo mais recente
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                
                # Verificar se foi criado nos últimos 30 segundos
                if time.time() - arquivo_mais_recente.stat().st_mtime < 30:
                    # Renomear arquivo
                    novo_nome = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    novo_caminho = self.downloads_dir / novo_nome
                    
                    arquivo_mais_recente.rename(novo_caminho)
                    
                    logger.info(f"✅ OFÍCIO BAIXADO: {novo_caminho}")
                    
                    return {
                        "sucesso": True,
                        "caminho": str(novo_caminho),
                        "mensagem": "Ofício baixado com sucesso"
                    }
            
            logger.warning("Arquivo não foi baixado automaticamente")
            return {
                "sucesso": False,
                "erro": "download_nao_realizado",
                "mensagem": "O ofício não foi baixado automaticamente. Verifique os screenshots."
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar ofício: {str(e)}", exc_info=True)
            return {
                "sucesso": False,
                "erro": "erro_geral",
                "mensagem": f"Erro ao buscar ofício: {str(e)}"
            }
    
    def fechar(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver fechado")

# Função principal para uso standalone
def main():
    """Função principal para teste"""
    buscador = BuscadorOficioTJSP(headless=False)
    
    try:
        # Testar com o processo fornecido
        numero_processo = "0034565-98.2018.8.26.0053"
        
        print(f"\n{'='*60}")
        print(f"BUSCADOR DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print(f"Processo: {numero_processo}")
        print('='*60)
        
        resultado = buscador.buscar_oficio(numero_processo)
        
        print(f"\n{'='*60}")
        print("RESULTADO:")
        print(f"Sucesso: {resultado['sucesso']}")
        
        if resultado['sucesso']:
            print(f"Arquivo: {resultado['caminho']}")
        else:
            print(f"Erro: {resultado.get('erro')}")
            print(f"Mensagem: {resultado['mensagem']}")
        
        print('='*60)
        
        if not resultado['sucesso']:
            print("\n🌐 O navegador ficará aberto para inspeção...")
            print("Pressione ENTER para fechar...")
            input()
        
    finally:
        buscador.fechar()

if __name__ == "__main__":
    main()
