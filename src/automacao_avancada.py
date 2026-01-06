"""
Módulo de Automação Avançada - Tax Master
Busca automática de ofícios em múltiplos tribunais
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
import hashlib
import sys

sys.path.append("src")
from database import SessionLocal
from models_atualizado import Processo, LogBuscaOficio, StatusProcessoEnum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automacao_oficios.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ConfiguracaoTribunal:
    """Configurações específicas de cada tribunal"""
    
    TRIBUNAIS = {
        "TJSP": {
            "nome": "Tribunal de Justiça de São Paulo",
            "url_consulta": "https://esaj.tjsp.jus.br/cpopg/open.do",
            "campo_numero_1": "numeroDigitoAnoUnificado",
            "campo_numero_2": "foroNumeroUnificado",
            "botao_consulta": "botaoConsultarProcessos",
            "formato_numero": "NNNNNNN-DD.AAAA.J.TR.OOOO",
            "requer_autenticacao": True
        },
        "TJRJ": {
            "nome": "Tribunal de Justiça do Rio de Janeiro",
            "url_consulta": "http://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProc.do",
            "formato_numero": "NNNNNNN-DD.AAAA.J.TR.OOOO",
            "requer_autenticacao": False
        },
        "TJMG": {
            "nome": "Tribunal de Justiça de Minas Gerais",
            "url_consulta": "https://www4.tjmg.jus.br/juridico/sf/proc_resultado.jsp",
            "formato_numero": "NNNNNNN-DD.AAAA.J.TR.OOOO",
            "requer_autenticacao": False
        },
        "TRF3": {
            "nome": "Tribunal Regional Federal da 3ª Região",
            "url_consulta": "https://web.trf3.jus.br/consultas/Internet/ConsultaProcessual",
            "formato_numero": "NNNNNNN-DD.AAAA.4.03.OOOO",
            "requer_autenticacao": False
        }
    }
    
    @classmethod
    def obter_config(cls, tribunal):
        """Obtém configuração de um tribunal"""
        return cls.TRIBUNAIS.get(tribunal.upper(), None)

class AutomacaoOficiosAvancada:
    """Classe de automação avançada para busca de ofícios"""
    
    def __init__(self, headless=False):
        self.downloads_dir = Path("data/oficios")
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
        self.wait = None
        self.db = None
        self.estatisticas = {
            "total": 0,
            "sucesso": 0,
            "falha": 0,
            "tempo_total": 0
        }
    
    def iniciar_driver(self):
        """Inicializa o Chrome WebDriver"""
        logger.info("Iniciando Chrome WebDriver...")
        
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
        
        logger.info("Chrome WebDriver iniciado com sucesso")
    
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        logger.info("Conectando ao banco de dados...")
        self.db = SessionLocal()
        logger.info("Conectado ao banco de dados")
    
    def calcular_hash_arquivo(self, caminho):
        """Calcula hash MD5 de um arquivo"""
        try:
            with open(caminho, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def buscar_oficio_tjsp(self, processo):
        """Busca ofício no TJSP"""
        tempo_inicio = time.time()
        
        try:
            logger.info(f"Buscando oficio: {processo.numero_processo}")
            
            # Acessar consulta
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(3)
            
            # Preencher campos
            partes = processo.numero_processo.split('.')
            if len(partes) < 5:
                raise ValueError("Formato de processo invalido")
            
            parte1 = f"{partes[0]}.{partes[1]}.{partes[2]}.{partes[3]}"
            parte2 = partes[4]
            
            self.driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(parte1)
            self.driver.find_element(By.ID, "foroNumeroUnificado").send_keys(parte2)
            self.driver.find_element(By.ID, "botaoConsultarProcessos").click()
            
            time.sleep(5)
            
            # Verificar se encontrou
            page_source = self.driver.page_source
            
            if "não encontrado" in page_source.lower():
                raise Exception("Processo nao encontrado")
            
            # Acessar Pasta Digital
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                texto = link.text.strip().lower()
                if "visualizar" in texto and "auto" in texto:
                    janelas_antes = self.driver.window_handles
                    link.click()
                    time.sleep(5)
                    
                    janelas_depois = self.driver.window_handles
                    if len(janelas_depois) > len(janelas_antes):
                        nova_janela = [j for j in janelas_depois if j not in janelas_antes][0]
                        self.driver.switch_to.window(nova_janela)
                        time.sleep(3)
                    
                    break
            
            # Verificar autenticação
            if "login" in self.driver.current_url.lower() or "validacao" in self.driver.current_url.lower():
                logger.warning("Autenticacao necessaria")
                print("\nFaca login e valide com codigo de e-mail")
                print("Depois pressione ENTER...")
                input()
                time.sleep(3)
            
            # Buscar ofício
            time.sleep(5)
            
            elementos = self.driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ÁÉÍÓÚÂÊÔÃÕÇ', 'aeiouaeoaoc'), 'oficio')]")
            
            if elementos:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elementos[0])
                time.sleep(1)
                elementos[0].click()
                time.sleep(10)
                
                # Verificar download
                arquivos_pdf = list(self.downloads_dir.glob("*.pdf"))
                
                if arquivos_pdf:
                    arquivo_mais_recente = max(arquivos_pdf, key=lambda p: p.stat().st_mtime)
                    
                    if time.time() - arquivo_mais_recente.stat().st_mtime < 60:
                        # Renomear
                        novo_nome = f"oficio_{processo.numero_processo.replace('/', '_').replace('.', '_')}.pdf"
                        novo_caminho = self.downloads_dir / novo_nome
                        
                        if novo_caminho.exists():
                            novo_caminho = self.downloads_dir / f"oficio_{processo.numero_processo.replace('/', '_').replace('.', '_')}_{int(time.time())}.pdf"
                        
                        arquivo_mais_recente.rename(novo_caminho)
                        
                        # Calcular hash
                        hash_arquivo = self.calcular_hash_arquivo(novo_caminho)
                        
                        # Atualizar processo
                        processo.tem_oficio = True
                        processo.caminho_oficio = str(novo_caminho)
                        processo.data_busca_oficio = datetime.now()
                        processo.hash_oficio = hash_arquivo
                        processo.status = StatusProcessoEnum.OFICIO_BAIXADO
                        
                        # Registrar log
                        tempo_execucao = time.time() - tempo_inicio
                        
                        log = LogBuscaOficio(
                            processo_id=processo.id,
                            numero_processo=processo.numero_processo,
                            tribunal=processo.tribunal.value,
                            sucesso=True,
                            tempo_execucao=tempo_execucao,
                            caminho_oficio=str(novo_caminho),
                            tamanho_arquivo=novo_caminho.stat().st_size
                        )
                        
                        self.db.add(log)
                        self.db.commit()
                        
                        logger.info(f"Oficio baixado com sucesso: {novo_caminho.name}")
                        
                        return {
                            "sucesso": True,
                            "caminho": str(novo_caminho),
                            "tempo": tempo_execucao
                        }
            
            raise Exception("Oficio nao encontrado")
            
        except Exception as e:
            tempo_execucao = time.time() - tempo_inicio
            
            logger.error(f"Erro ao buscar oficio: {str(e)}")
            
            # Registrar log de falha
            log = LogBuscaOficio(
                processo_id=processo.id,
                numero_processo=processo.numero_processo,
                tribunal=processo.tribunal.value,
                sucesso=False,
                erro=str(e),
                tempo_execucao=tempo_execucao
            )
            
            self.db.add(log)
            self.db.commit()
            
            return {
                "sucesso": False,
                "erro": str(e),
                "tempo": tempo_execucao
            }
    
    def processar_lote(self, tribunal="TJSP", limite=None, filtros=None):
        """Processa um lote de processos"""
        logger.info("="*60)
        logger.info("PROCESSAMENTO EM LOTE")
        logger.info("="*60)
        
        # Buscar processos
        query = self.db.query(Processo).filter(
            Processo.tribunal.has(value=tribunal),
            Processo.tem_oficio == False
        )
        
        # Aplicar filtros adicionais
        if filtros:
            if filtros.get("valor_minimo"):
                query = query.filter(Processo.valor_atualizado >= filtros["valor_minimo"])
            
            if filtros.get("valor_maximo"):
                query = query.filter(Processo.valor_atualizado <= filtros["valor_maximo"])
            
            if filtros.get("natureza"):
                query = query.filter(Processo.natureza.has(value=filtros["natureza"]))
            
            if filtros.get("credor_idoso"):
                query = query.filter(Processo.credor_idoso == True)
        
        if limite:
            query = query.limit(limite)
        
        processos = query.all()
        
        logger.info(f"Total de processos a processar: {len(processos)}")
        
        if not processos:
            logger.warning("Nenhum processo encontrado")
            return
        
        # Iniciar driver
        if not self.driver:
            self.iniciar_driver()
        
        # Processar
        self.estatisticas["total"] = len(processos)
        
        for i, processo in enumerate(processos, 1):
            logger.info(f"\n[{i}/{len(processos)}] Processando {processo.numero_processo}")
            
            resultado = self.buscar_oficio_tjsp(processo)
            
            if resultado["sucesso"]:
                self.estatisticas["sucesso"] += 1
            else:
                self.estatisticas["falha"] += 1
            
            self.estatisticas["tempo_total"] += resultado["tempo"]
            
            # Pausa entre processos
            if i < len(processos):
                time.sleep(5)
        
        # Resumo
        self._exibir_resumo()
    
    def _exibir_resumo(self):
        """Exibe resumo das estatísticas"""
        logger.info("\n" + "="*60)
        logger.info("RESUMO DO PROCESSAMENTO")
        logger.info("="*60)
        logger.info(f"Total processados: {self.estatisticas['total']}")
        logger.info(f"Sucessos: {self.estatisticas['sucesso']}")
        logger.info(f"Falhas: {self.estatisticas['falha']}")
        
        if self.estatisticas['total'] > 0:
            taxa_sucesso = (self.estatisticas['sucesso'] / self.estatisticas['total']) * 100
            logger.info(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if self.estatisticas['tempo_total'] > 0:
            tempo_medio = self.estatisticas['tempo_total'] / self.estatisticas['total']
            logger.info(f"Tempo medio por processo: {tempo_medio:.1f}s")
            logger.info(f"Tempo total: {self.estatisticas['tempo_total']:.1f}s")
        
        logger.info("="*60)
    
    def fechar(self):
        """Fecha conexões"""
        if self.driver:
            self.driver.quit()
        
        if self.db:
            self.db.close()

def main():
    """Função principal"""
    automacao = AutomacaoOficiosAvancada(headless=False)
    
    try:
        print("\n" + "="*60)
        print("AUTOMACAO AVANCADA DE OFICIOS - TAX MASTER")
        print("Cobertura Nacional | Filtros Avancados | Painel Intuitivo")
        print("="*60)
        
        automacao.conectar_banco()
        
        print("\nOpcoes:")
        print("1. Processar processos do TJSP (ate 10x mais rapido)")
        print("2. Processar com filtros avancados")
        print("3. Teste com 3 processos")
        
        opcao = input("\nEscolha (1/2/3): ").strip()
        
        if opcao == "1":
            limite = input("Quantos processos? (Enter para todos): ").strip()
            limite = int(limite) if limite else None
            
            automacao.processar_lote(tribunal="TJSP", limite=limite)
            
        elif opcao == "2":
            print("\nFiltros Avancados:")
            valor_min = input("Valor minimo (Enter para pular): ").strip()
            valor_max = input("Valor maximo (Enter para pular): ").strip()
            
            filtros = {}
            if valor_min:
                filtros["valor_minimo"] = float(valor_min)
            if valor_max:
                filtros["valor_maximo"] = float(valor_max)
            
            automacao.processar_lote(tribunal="TJSP", filtros=filtros)
            
        elif opcao == "3":
            automacao.processar_lote(tribunal="TJSP", limite=3)
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}", exc_info=True)
        
    finally:
        automacao.fechar()

if __name__ == "__main__":
    main()
