"""
Buscador de Ofícios Requisitórios - TJSP
Versão com múltiplas estratégias de busca
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time
from pathlib import Path
import logging

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
        
        prefs = {
            "download.default_directory": str(self.downloads_dir.absolute()),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(10)
        
        logger.info("Chrome WebDriver iniciado")
    
    def buscar_oficio(self, numero_processo, processo_principal=None):
        """
        Busca e baixa o ofício requisitório
        
        Args:
            numero_processo: Número do processo de execução
            processo_principal: Número do processo principal/conhecimento (opcional)
        """
        logger.info(f"Buscando ofício - Processo: {numero_processo}")
        
        if processo_principal:
            logger.info(f"Processo principal: {processo_principal}")
        
        try:
            if not self.driver:
                self.iniciar_driver()
            
            # ESTRATÉGIA: Ir direto para consulta de requisitórios
            logger.info("Acessando consulta de requisitórios diretamente...")
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do")
            time.sleep(3)
            
            # Tentar com o processo de execução primeiro
            processos_para_tentar = [numero_processo]
            
            # Se tiver processo principal, adicionar à lista
            if processo_principal:
                processos_para_tentar.append(processo_principal)
            
            resultado_encontrado = None
            
            for i, processo in enumerate(processos_para_tentar):
                logger.info(f"\nTentativa {i+1}: Buscando com processo {processo}")
                
                # Separar número
                partes = processo.split('.')
                if len(partes) < 5:
                    logger.warning(f"Formato inválido: {processo}")
                    continue
                
                parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
                parte2 = partes[4]
                
                logger.info(f"Preenchendo: {parte1} / {parte2}")
                
                # Limpar e preencher campos
                campo1 = self.driver.find_element(By.ID, "numeroDigitoAnoUnificado")
                campo1.clear()
                campo1.send_keys(parte1)
                
                campo2 = self.driver.find_element(By.ID, "foroNumeroUnificado")
                campo2.clear()
                campo2.send_keys(parte2)
                
                self.driver.save_screenshot(str(self.downloads_dir / f"busca_{i+1}_preenchido.png"))
                
                # Consultar
                self.driver.find_element(By.ID, "botaoConsultarProcessos").click()
                time.sleep(5)
                
                self.driver.save_screenshot(str(self.downloads_dir / f"busca_{i+1}_resultado.png"))
                
                # Verificar resultado
                page_source = self.driver.page_source.lower()
                
                if "não encontrado" not in page_source and "não existem" not in page_source:
                    logger.info(f"✅ Requisitório encontrado com processo: {processo}")
                    resultado_encontrado = processo
                    break
                else:
                    logger.warning(f"Requisitório não encontrado para: {processo}")
                    
                    # Se não for a última tentativa, voltar para a página de busca
                    if i < len(processos_para_tentar) - 1:
                        self.driver.get("https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do")
                        time.sleep(3)
            
            if not resultado_encontrado:
                logger.error("Requisitório não encontrado com nenhum dos processos")
                return {
                    "sucesso": False,
                    "erro": "sem_requisitorios",
                    "mensagem": "Ofício requisitório não encontrado no TJSP"
                }
            
            # Procurar link de visualização
            logger.info("Procurando link de visualização...")
            
            link_visualizar = None
            
            # Estratégia 1: Por texto
            try:
                link_visualizar = self.driver.find_element(By.LINK_TEXT, "Visualizar")
                logger.info("✅ Link encontrado por texto")
            except NoSuchElementException:
                pass
            
            # Estratégia 2: Por href
            if not link_visualizar:
                try:
                    link_visualizar = self.driver.find_element(By.CSS_SELECTOR, "a[href*='abrirDownload']")
                    logger.info("✅ Link encontrado por href")
                except NoSuchElementException:
                    pass
            
            # Estratégia 3: Listar todos os links
            if not link_visualizar:
                logger.info("Listando todos os links da página...")
                links = self.driver.find_elements(By.TAG_NAME, "a")
                
                logger.info(f"Total de links: {len(links)}")
                
                for j, link in enumerate(links):
                    try:
                        texto = link.text.strip()
                        href = link.get_attribute("href") or ""
                        
                        if j < 30:  # Mostrar primeiros 30
                            logger.info(f"Link {j+1}: {texto[:40]} | {href[:50]}")
                        
                        if "visualizar" in texto.lower() or "download" in href.lower():
                            link_visualizar = link
                            logger.info(f"✅ Link encontrado: {texto}")
                            break
                    except:
                        pass
            
            if not link_visualizar:
                logger.error("Link de visualização não encontrado")
                
                logger.info("\n🌐 Navegador ficará aberto para inspeção manual...")
                logger.info("Verifique os screenshots:")
                for img in self.downloads_dir.glob("busca_*_resultado.png"):
                    logger.info(f"  - {img.name}")
                
                print("\nPressione ENTER para fechar...")
                input()
                
                return {
                    "sucesso": False,
                    "erro": "link_nao_encontrado",
                    "mensagem": "Link de visualização não encontrado"
                }
            
            # Clicar no link
            logger.info("Clicando no link de visualização...")
            
            janelas_antes = self.driver.window_handles
            
            # Scroll e click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link_visualizar)
            time.sleep(1)
            link_visualizar.click()
            time.sleep(5)
            
            # Verificar novas janelas
            janelas_depois = self.driver.window_handles
            
            if len(janelas_depois) > len(janelas_antes):
                logger.info("✅ Nova janela aberta")
                nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                self.driver.switch_to.window(nova_janela)
                time.sleep(3)
                
                logger.info(f"URL: {self.driver.current_url}")
                self.driver.save_screenshot(str(self.downloads_dir / "visualizacao.png"))
                
                self.driver.close()
                self.driver.switch_to.window(janelas_antes[0])
            
            # Verificar download
            logger.info("Verificando download...")
            time.sleep(5)
            
            arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
            
            if arquivos_pdf:
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                
                if time.time() - arquivo_mais_recente.stat().st_mtime < 30:
                    novo_nome = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                    novo_caminho = self.downloads_dir / novo_nome
                    
                    if novo_caminho.exists():
                        novo_caminho = self.downloads_dir / f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{int(time.time())}.pdf"
                    
                    arquivo_mais_recente.rename(novo_caminho)
                    
                    logger.info(f"✅ OFÍCIO BAIXADO: {novo_caminho}")
                    
                    return {
                        "sucesso": True,
                        "caminho": str(novo_caminho),
                        "mensagem": "Ofício baixado com sucesso"
                    }
            
            logger.warning("Download não realizado")
            return {
                "sucesso": False,
                "erro": "download_nao_realizado",
                "mensagem": "Download não foi realizado"
            }
            
        except Exception as e:
            logger.error(f"Erro: {str(e)}", exc_info=True)
            return {
                "sucesso": False,
                "erro": "erro_geral",
                "mensagem": str(e)
            }
    
    def fechar(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Função principal"""
    buscador = BuscadorOficioTJSP(headless=False)
    
    try:
        # Processos do exemplo
        processo_execucao = "0034565-98.2018.8.26.0053"
        processo_principal = "0048680-71.2011.8.26.0053"
        
        print(f"\n{'='*60}")
        print("BUSCADOR DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print(f"Processo Execução: {processo_execucao}")
        print(f"Processo Principal: {processo_principal}")
        print('='*60)
        
        resultado = buscador.buscar_oficio(processo_execucao, processo_principal)
        
        print(f"\n{'='*60}")
        print("RESULTADO:")
        print(f"Sucesso: {resultado['sucesso']}")
        
        if resultado['sucesso']:
            print(f"Arquivo: {resultado['caminho']}")
        else:
            print(f"Erro: {resultado.get('erro')}")
            print(f"Mensagem: {resultado['mensagem']}")
        
        print('='*60)
        
    finally:
        buscador.fechar()

if __name__ == "__main__":
    main()
