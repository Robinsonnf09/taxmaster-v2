"""
Buscador Avançado de Ofícios Requisitórios - TJSP
Versão Final com Acesso à Pasta Digital
Autor: Adapta AI
Data: 2026-01-03
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('buscador_oficios.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BuscadorOficioTJSPAvancado:
    """
    Classe avançada para buscar e baixar ofícios requisitórios do TJSP
    através da Pasta Digital
    """
    
    def __init__(self, headless=False, timeout=30):
        self.downloads_dir = Path("data/oficios")
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
    
    def iniciar_driver(self):
        """Inicializa o Chrome WebDriver com configurações otimizadas"""
        logger.info("="*60)
        logger.info("Iniciando Chrome WebDriver...")
        logger.info("="*60)
        
        options = webdriver.ChromeOptions()
        
        # Configurações de download
        prefs = {
            "download.default_directory": str(self.downloads_dir.absolute()),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        options.add_experimental_option("prefs", prefs)
        
        # Configurações para evitar detecção
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        
        if self.headless:
            options.add_argument("--headless=new")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Configurar wait
        self.wait = WebDriverWait(self.driver, self.timeout)
        
        # Executar script para remover detecção de webdriver
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        logger.info("✅ Chrome WebDriver iniciado com sucesso")
    
    def aguardar_autenticacao(self):
        """Aguarda o usuário fazer login e validar código de e-mail"""
        logger.info("\n" + "="*60)
        logger.info("AUTENTICAÇÃO NECESSÁRIA")
        logger.info("="*60)
        
        print("\n🔐 O portal e-SAJ requer autenticação.")
        print("\n📋 INSTRUÇÕES:")
        print("1. Faça login manualmente no navegador que abriu")
        print("2. Insira o código de validação enviado para seu e-mail")
        print("3. Aguarde a página carregar completamente")
        print("4. Pressione ENTER aqui para continuar...")
        
        self.driver.save_screenshot(str(self.downloads_dir / "autenticacao_necessaria.png"))
        
        input("\n⏸️  Pressione ENTER após completar a autenticação...")
        
        logger.info("✅ Continuando após autenticação...")
        time.sleep(3)
    
    def buscar_processo(self, numero_processo, processo_principal=None):
        """
        Busca o processo na consulta processual
        
        Args:
            numero_processo: Número do processo de execução
            processo_principal: Número do processo principal (opcional)
            
        Returns:
            bool: True se encontrou, False caso contrário
        """
        logger.info("\n" + "="*60)
        logger.info(f"PASSO 1: Buscando processo {numero_processo}")
        logger.info("="*60)
        
        processos_para_tentar = [numero_processo]
        if processo_principal:
            processos_para_tentar.append(processo_principal)
        
        for i, processo in enumerate(processos_para_tentar):
            logger.info(f"\nTentativa {i+1}: {processo}")
            
            try:
                # Acessar consulta processual
                self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
                time.sleep(3)
                
                # Separar número
                partes = processo.split('.')
                if len(partes) < 5:
                    logger.warning(f"Formato inválido: {processo}")
                    continue
                
                parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
                parte2 = partes[4]
                
                logger.info(f"Preenchendo: {parte1} / {parte2}")
                
                # Preencher campos
                self.wait.until(EC.presence_of_element_located((By.ID, "numeroDigitoAnoUnificado")))
                self.driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
                self.driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
                
                self.driver.save_screenshot(str(self.downloads_dir / f"passo1_{i+1}_preenchido.png"))
                
                # Consultar
                self.driver.find_element(By.ID, "botaoConsultarProcessos").click()
                time.sleep(5)
                
                self.driver.save_screenshot(str(self.downloads_dir / f"passo1_{i+1}_resultado.png"))
                
                # Verificar se encontrou
                page_source = self.driver.page_source.lower()
                
                if "não encontrado" not in page_source and "não existem" not in page_source:
                    logger.info(f"✅ Processo encontrado: {processo}")
                    return True
                else:
                    logger.warning(f"Processo não encontrado: {processo}")
                    
            except Exception as e:
                logger.error(f"Erro ao buscar processo: {str(e)}")
        
        return False
    
    def acessar_pasta_digital(self):
        """
        Acessa a Pasta Digital do processo
        
        Returns:
            bool: True se conseguiu acessar, False caso contrário
        """
        logger.info("\n" + "="*60)
        logger.info("PASSO 2: Acessando Pasta Digital...")
        logger.info("="*60)
        
        try:
            # Procurar link "Visualizar Autos" ou "Pasta Digital"
            seletores = [
                "a:has-text('Visualizar Autos')",
                "a:has-text('Pasta Digital')",
                "a[href*='pastadigital']",
                "a[href*='abrirPastaProcessoDigital']"
            ]
            
            link_encontrado = None
            
            for seletor in seletores:
                try:
                    # Tentar encontrar o link
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a")
                    
                    for link in links:
                        texto = link.text.strip().lower()
                        href = link.get_attribute("href") or ""
                        
                        if ("visualizar" in texto and "auto" in texto) or \
                           "pasta digital" in texto or \
                           "pastadigital" in href:
                            link_encontrado = link
                            logger.info(f"✅ Link encontrado: {link.text.strip()}")
                            break
                    
                    if link_encontrado:
                        break
                        
                except Exception as e:
                    logger.debug(f"Erro ao tentar seletor {seletor}: {e}")
            
            if not link_encontrado:
                logger.warning("Link não encontrado automaticamente")
                print("\n💡 Clique manualmente em 'Visualizar Autos' ou 'Pasta Digital'")
                print("Depois pressione ENTER aqui...")
                input()
                return True
            
            # Clicar no link
            janelas_antes = self.driver.window_handles
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link_encontrado)
            time.sleep(1)
            link_encontrado.click()
            time.sleep(5)
            
            # Verificar se abriu nova janela
            janelas_depois = self.driver.window_handles
            
            if len(janelas_depois) > len(janelas_antes):
                logger.info("✅ Pasta Digital aberta em nova janela")
                nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                self.driver.switch_to.window(nova_janela)
                time.sleep(3)
            
            # Verificar se precisa de autenticação
            if "login" in self.driver.current_url.lower() or "validacao" in self.driver.current_url.lower():
                self.aguardar_autenticacao()
            
            self.driver.save_screenshot(str(self.downloads_dir / "passo2_pasta_digital.png"))
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao acessar Pasta Digital: {str(e)}")
            return False
    
    def buscar_oficio_na_pasta(self):
        """
        Busca o documento "Ofício" na árvore de documentos da Pasta Digital
        
        Returns:
            dict: Informações sobre o ofício encontrado ou None
        """
        logger.info("\n" + "="*60)
        logger.info("PASSO 3: Buscando 'Ofício' nos documentos...")
        logger.info("="*60)
        
        try:
            # Aguardar carregamento da árvore de documentos
            time.sleep(5)
            
            # Procurar por links/elementos que contenham "ofício"
            todos_elementos = self.driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ÁÉÍÓÚÂÊÔÃÕÇ', 'aeiouaeoaoc'), 'oficio')]")
            
            logger.info(f"Elementos com 'ofício' encontrados: {len(todos_elementos)}")
            
            oficios_encontrados = []
            
            for elemento in todos_elementos:
                try:
                    texto = elemento.text.strip()
                    tag = elemento.tag_name
                    
                    if texto:
                        logger.info(f"📄 {tag}: {texto[:80]}")
                        
                        # Verificar se é clicável
                        if tag in ['a', 'span', 'div'] and elemento.is_displayed():
                            oficios_encontrados.append({
                                "elemento": elemento,
                                "texto": texto,
                                "tag": tag
                            })
                            logger.info(f"   🎯 Elemento clicável encontrado!")
                            
                except Exception as e:
                    logger.debug(f"Erro ao processar elemento: {e}")
            
            if not oficios_encontrados:
                logger.warning("Nenhum ofício clicável encontrado")
                
                print("\n💡 Procure manualmente pelo 'Ofício' na árvore de documentos")
                print("Clique no documento e pressione ENTER aqui...")
                input()
                
                return {"manual": True}
            
            logger.info(f"\n✅ {len(oficios_encontrados)} ofício(s) encontrado(s)")
            
            return oficios_encontrados[0]
            
        except Exception as e:
            logger.error(f"Erro ao buscar ofício: {str(e)}")
            return None
    
    def baixar_oficio(self, oficio_info):
        """
        Baixa o PDF do ofício
        
        Args:
            oficio_info: Informações do ofício encontrado
            
        Returns:
            dict: Resultado do download
        """
        logger.info("\n" + "="*60)
        logger.info("PASSO 4: Baixando ofício...")
        logger.info("="*60)
        
        try:
            if oficio_info.get("manual"):
                # Aguardar download manual
                print("\n💡 Clique no documento para visualizar/baixar")
                print("Depois pressione ENTER aqui...")
                input()
            else:
                # Clicar no elemento
                elemento = oficio_info["elemento"]
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                time.sleep(1)
                
                logger.info(f"Clicando em: {oficio_info['texto'][:50]}")
                elemento.click()
                time.sleep(5)
            
            # Aguardar download
            logger.info("Aguardando download...")
            time.sleep(10)
            
            # Verificar arquivos baixados
            arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
            
            if arquivos_pdf:
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                
                # Verificar se foi baixado recentemente (últimos 60 segundos)
                if time.time() - arquivo_mais_recente.stat().st_mtime < 60:
                    # Renomear arquivo
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    novo_nome = f"oficio_TJSP_{timestamp}.pdf"
                    novo_caminho = self.downloads_dir / novo_nome
                    
                    if novo_caminho.exists():
                        novo_caminho = self.downloads_dir / f"oficio_TJSP_{timestamp}_{int(time.time())}.pdf"
                    
                    arquivo_mais_recente.rename(novo_caminho)
                    
                    logger.info(f"✅ OFÍCIO BAIXADO: {novo_caminho}")
                    
                    return {
                        "sucesso": True,
                        "caminho": str(novo_caminho),
                        "mensagem": "Ofício baixado com sucesso"
                    }
            
            logger.warning("Arquivo não foi baixado automaticamente")
            
            print("\n💡 Se o PDF abriu em uma nova aba:")
            print("1. Clique com botão direito no PDF")
            print("2. Selecione 'Salvar como...'")
            print("3. Salve na pasta 'data/oficios'")
            print("4. Pressione ENTER aqui quando terminar...")
            input()
            
            # Verificar novamente
            arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
            if arquivos_pdf:
                arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                if time.time() - arquivo_mais_recente.stat().st_mtime < 120:
                    return {
                        "sucesso": True,
                        "caminho": str(arquivo_mais_recente),
                        "mensagem": "Ofício salvo manualmente"
                    }
            
            return {
                "sucesso": False,
                "erro": "download_nao_realizado",
                "mensagem": "Não foi possível confirmar o download"
            }
            
        except Exception as e:
            logger.error(f"Erro ao baixar ofício: {str(e)}")
            return {
                "sucesso": False,
                "erro": "erro_download",
                "mensagem": str(e)
            }
    
    def executar(self, numero_processo, processo_principal=None):
        """
        Executa o fluxo completo de busca e download do ofício
        
        Args:
            numero_processo: Número do processo de execução
            processo_principal: Número do processo principal (opcional)
            
        Returns:
            dict: Resultado da execução
        """
        try:
            if not self.driver:
                self.iniciar_driver()
            
            # Passo 1: Buscar processo
            if not self.buscar_processo(numero_processo, processo_principal):
                return {
                    "sucesso": False,
                    "erro": "processo_nao_encontrado",
                    "mensagem": "Processo não encontrado no TJSP"
                }
            
            # Passo 2: Acessar Pasta Digital
            if not self.acessar_pasta_digital():
                return {
                    "sucesso": False,
                    "erro": "pasta_digital_inacessivel",
                    "mensagem": "Não foi possível acessar a Pasta Digital"
                }
            
            # Passo 3: Buscar ofício
            oficio_info = self.buscar_oficio_na_pasta()
            
            if not oficio_info:
                return {
                    "sucesso": False,
                    "erro": "oficio_nao_encontrado",
                    "mensagem": "Ofício não encontrado nos documentos"
                }
            
            # Passo 4: Baixar ofício
            resultado = self.baixar_oficio(oficio_info)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na execução: {str(e)}", exc_info=True)
            
            print("\n🌐 Navegador ficará aberto para inspeção...")
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
    buscador = BuscadorOficioTJSPAvancado(headless=False, timeout=30)
    
    try:
        # Processos do exemplo
        processo_execucao = "0034565-98.2018.8.26.0053"
        processo_principal = "0048680-71.2011.8.26.0053"
        
        print(f"\n{'='*60}")
        print("BUSCADOR AVANÇADO DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print("Versão Final com Acesso à Pasta Digital")
        print(f"Processo Execução: {processo_execucao}")
        print(f"Processo Principal: {processo_principal}")
        print('='*60)
        
        resultado = buscador.executar(processo_execucao, processo_principal)
        
        print(f"\n{'='*60}")
        print("RESULTADO FINAL:")
        print(f"Sucesso: {resultado['sucesso']}")
        
        if resultado['sucesso']:
            print(f"✅ Arquivo: {resultado['caminho']}")
            print(f"✅ {resultado['mensagem']}")
        else:
            print(f"❌ Erro: {resultado.get('erro')}")
            print(f"❌ Mensagem: {resultado['mensagem']}")
        
        print('='*60)
        
    finally:
        buscador.fechar()

if __name__ == "__main__":
    main()
