from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging
from datetime import datetime
from pathlib import Path
import time
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("BuscadorOficio")

class BuscadorOficioRequisitorio:
    """Robô para buscar e baixar ofícios requisitórios dos tribunais"""
    
    def __init__(self):
        self.downloads_dir = Path("data/oficios")
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # URLs dos portais dos tribunais
        self.portais = {
            "TJRJ": "http://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProc.do",
            "TJSP": "https://esaj.tjsp.jus.br/cpopg/open.do",
            "TJRS": "https://www.tjrs.jus.br/novo/processos/consulta-processual/",
            "TJMG": "https://www4.tjmg.jus.br/juridico/sf/proc_complemento.jsp",
            "TJPR": "https://projudi.tjpr.jus.br/projudi/",
            "TRF1": "https://processual.trf1.jus.br/consultaProcessual/",
            "TRF2": "https://eproc.trf2.jus.br/eproc/",
            "TRF3": "https://web.trf3.jus.br/consultas/Internet/ConsultaProcessual",
            "TRF4": "https://www2.trf4.jus.br/trf4/processos/acompanhamento/",
            "TRF5": "https://cp.trf5.jus.br/processo/"
        }
    
    def limpar_numero_processo(self, numero):
        """Remove formatação do número do processo"""
        return re.sub(r'[^0-9]', '', numero)
    
    def buscar_oficio(self, numero_processo, tribunal):
        """Método principal para buscar ofício em qualquer tribunal"""
        logger.info(f"Iniciando busca de ofício - Processo: {numero_processo}, Tribunal: {tribunal}")
        
        try:
            with sync_playwright() as p:
                # Configurar navegador
                browser = p.chromium.launch(
                    headless=False,
                    downloads_path=str(self.downloads_dir),
                    slow_mo=1000  # Delay de 1 segundo entre ações
                )
                
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    accept_downloads=True
                )
                
                page = context.new_page()
                
                try:
                    # Verificar se tribunal está implementado
                    if tribunal not in self.portais:
                        return {
                            "sucesso": False,
                            "erro": "tribunal_nao_implementado",
                            "mensagem": f"Tribunal {tribunal} ainda não está implementado"
                        }
                    
                    # Acessar portal
                    logger.info(f"Acessando portal: {self.portais[tribunal]}")
                    page.goto(self.portais[tribunal], timeout=60000, wait_until="networkidle")
                    logger.info("Portal carregado com sucesso")
                    time.sleep(3)  # Aguardar carregamento completo
                    
                    # Buscar processo conforme tribunal
                    if tribunal == "TJRJ":
                        resultado = self._buscar_tjrj(numero_processo, page)
                    elif tribunal == "TJSP":
                        resultado = self._buscar_tjsp(numero_processo, page)
                    elif tribunal in ["TRF1", "TRF2", "TRF3", "TRF4", "TRF5"]:
                        resultado = self._buscar_trf(numero_processo, tribunal, page)
                    else:
                        resultado = {
                            "sucesso": False,
                            "erro": "tribunal_nao_implementado",
                            "mensagem": f"Busca não implementada para {tribunal}"
                        }
                    
                    return resultado
                    
                except PlaywrightTimeout as e:
                    logger.error(f"Timeout ao acessar portal: {str(e)}")
                    return {
                        "sucesso": False,
                        "erro": "timeout",
                        "mensagem": "Tempo limite excedido ao acessar o portal do tribunal"
                    }
                
                except Exception as e:
                    logger.error(f"Erro durante busca: {str(e)}")
                    return {
                        "sucesso": False,
                        "erro": "erro_busca",
                        "mensagem": f"Erro durante a busca: {str(e)}"
                    }
                
                finally:
                    try:
                        time.sleep(2)  # Aguardar antes de fechar
                        browser.close()
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Erro ao iniciar navegador: {str(e)}")
            return {
                "sucesso": False,
                "erro": "erro_navegador",
                "mensagem": f"Erro ao iniciar navegador: {str(e)}"
            }
    
    def _buscar_tjrj(self, numero_processo, page):
        """Busca processo no TJRJ"""
        try:
            logger.info(f"Buscando processo {numero_processo} no TJRJ")
            
            # Tirar screenshot para debug
            page.screenshot(path=str(self.downloads_dir / "tjrj_inicial.png"))
            logger.info("Screenshot salvo: tjrj_inicial.png")
            
            # Tentar múltiplos seletores para o campo de busca
            seletores_possiveis = [
                "input[name='numProcesso']",
                "input[id='numProcesso']",
                "#numProcesso",
                "input[type='text']",
                "input.form-control"
            ]
            
            campo_encontrado = False
            for seletor in seletores_possiveis:
                try:
                    if page.locator(seletor).count() > 0:
                        logger.info(f"Campo encontrado com seletor: {seletor}")
                        
                        # Preencher número do processo
                        numero_limpo = self.limpar_numero_processo(numero_processo)
                        page.fill(seletor, numero_limpo)
                        logger.info(f"Número preenchido: {numero_limpo}")
                        
                        campo_encontrado = True
                        break
                except Exception as e:
                    logger.debug(f"Seletor {seletor} não funcionou: {str(e)}")
                    continue
            
            if not campo_encontrado:
                logger.error("Nenhum campo de busca encontrado")
                return {
                    "sucesso": False,
                    "erro": "campo_nao_encontrado",
                    "mensagem": "Campo de busca não encontrado no portal do TJRJ"
                }
            
            # Tirar screenshot após preencher
            page.screenshot(path=str(self.downloads_dir / "tjrj_preenchido.png"))
            logger.info("Screenshot salvo: tjrj_preenchido.png")
            
            # Clicar em consultar - tentar múltiplos seletores
            botoes_possiveis = [
                "input[value='Consultar']",
                "button:has-text('Consultar')",
                "input[type='submit']",
                "button[type='submit']"
            ]
            
            botao_clicado = False
            for botao in botoes_possiveis:
                try:
                    if page.locator(botao).count() > 0:
                        logger.info(f"Botão encontrado: {botao}")
                        page.click(botao)
                        botao_clicado = True
                        break
                except Exception as e:
                    logger.debug(f"Botão {botao} não funcionou: {str(e)}")
                    continue
            
            if not botao_clicado:
                logger.error("Botão de consulta não encontrado")
                return {
                    "sucesso": False,
                    "erro": "botao_nao_encontrado",
                    "mensagem": "Botão de consulta não encontrado no portal do TJRJ"
                }
            
            # Aguardar resultado
            logger.info("Aguardando resultado da busca...")
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(3)
            
            # Tirar screenshot do resultado
            page.screenshot(path=str(self.downloads_dir / "tjrj_resultado.png"))
            logger.info("Screenshot salvo: tjrj_resultado.png")
            
            # Verificar se processo foi encontrado
            conteudo = page.content().lower()
            
            if "processo não encontrado" in conteudo or "não foi encontrado" in conteudo or "não encontrado" in conteudo:
                logger.warning(f"Processo {numero_processo} não encontrado no TJRJ")
                return {
                    "sucesso": False,
                    "erro": "processo_nao_existe",
                    "mensagem": f"O processo {numero_processo} não existe no TJRJ"
                }
            
            logger.info("Processo encontrado! Buscando ofício...")
            
            # Buscar links de documentos
            links = page.locator("a").all()
            logger.info(f"Total de links encontrados: {len(links)}")
            
            for i, link in enumerate(links):
                try:
                    texto = link.inner_text().strip().lower()
                    if texto and ("ofício" in texto or "requisitório" in texto or "requisitorio" in texto):
                        logger.info(f"Ofício encontrado no link {i}: {link.inner_text()}")
                        
                        # Tentar fazer download
                        with page.expect_download(timeout=30000) as download_info:
                            link.click()
                        
                        download = download_info.value
                        filename = f"oficio_TJRJ_{numero_processo.replace('/', '_').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        filepath = self.downloads_dir / filename
                        download.save_as(filepath)
                        
                        logger.info(f"Ofício baixado: {filepath}")
                        return {
                            "sucesso": True,
                            "caminho": str(filepath),
                            "mensagem": "Ofício baixado com sucesso"
                        }
                except Exception as e:
                    logger.debug(f"Erro ao processar link {i}: {str(e)}")
                    continue
            
            # Se chegou aqui, processo existe mas ofício não foi encontrado
            logger.warning("Processo existe, mas ofício não foi encontrado")
            return {
                "sucesso": False,
                "erro": "oficio_nao_encontrado",
                "mensagem": "Processo existe no tribunal, mas o ofício requisitório não foi encontrado ou ainda não foi expedido"
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar no TJRJ: {str(e)}")
            return {
                "sucesso": False,
                "erro": "erro_tjrj",
                "mensagem": f"Erro ao buscar no TJRJ: {str(e)}"
            }
    
    def _buscar_tjsp(self, numero_processo, page):
        """Busca processo no TJSP"""
        try:
            logger.info(f"Buscando processo {numero_processo} no TJSP")
            
            # Screenshot inicial
            page.screenshot(path=str(self.downloads_dir / "tjsp_inicial.png"))
            
            # Aguardar carregamento
            time.sleep(3)
            
            # Preencher número do processo
            numero_limpo = self.limpar_numero_processo(numero_processo)
            
            # Tentar diferentes seletores
            campo_preenchido = False
            
            if page.locator("#numeroDigitoAnoUnificado").count() > 0:
                logger.info("Usando campos unificados do TJSP")
                page.fill("#numeroDigitoAnoUnificado", numero_limpo[:15])
                if len(numero_limpo) > 15:
                    page.fill("#foroNumeroUnificado", numero_limpo[15:])
                campo_preenchido = True
            elif page.locator("input[name='nuProcesso']").count() > 0:
                logger.info("Usando campo nuProcesso")
                page.fill("input[name='nuProcesso']", numero_limpo)
                campo_preenchido = True
            elif page.locator("input[type='text']").count() > 0:
                logger.info("Usando primeiro campo de texto")
                page.locator("input[type='text']").first.fill(numero_limpo)
                campo_preenchido = True
            
            if not campo_preenchido:
                return {
                    "sucesso": False,
                    "erro": "campo_nao_encontrado",
                    "mensagem": "Campo de busca não encontrado no portal do TJSP"
                }
            
            logger.info(f"Número preenchido: {numero_limpo}")
            page.screenshot(path=str(self.downloads_dir / "tjsp_preenchido.png"))
            
            # Clicar em consultar
            page.click("input[type='submit']")
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(3)
            
            page.screenshot(path=str(self.downloads_dir / "tjsp_resultado.png"))
            
            # Verificar se processo foi encontrado
            conteudo = page.content().lower()
            
            if "não encontrado" in conteudo or "não foi possível" in conteudo:
                logger.warning(f"Processo {numero_processo} não encontrado no TJSP")
                return {
                    "sucesso": False,
                    "erro": "processo_nao_existe",
                    "mensagem": f"O processo {numero_processo} não existe no TJSP"
                }
            
            logger.info("Processo encontrado! Buscando ofício...")
            
            # Tentar clicar em "Documentos"
            if page.locator("text=Documentos").count() > 0:
                page.click("text=Documentos")
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)
            
            # Buscar ofício
            links = page.locator("a").all()
            logger.info(f"Total de links encontrados: {len(links)}")
            
            for i, link in enumerate(links):
                try:
                    texto = link.inner_text().strip().lower()
                    if texto and ("ofício" in texto or "requisitório" in texto):
                        logger.info(f"Ofício encontrado no link {i}: {link.inner_text()}")
                        
                        with page.expect_download(timeout=30000) as download_info:
                            link.click()
                        
                        download = download_info.value
                        filename = f"oficio_TJSP_{numero_processo.replace('/', '_').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        filepath = self.downloads_dir / filename
                        download.save_as(filepath)
                        
                        logger.info(f"Ofício baixado: {filepath}")
                        return {
                            "sucesso": True,
                            "caminho": str(filepath),
                            "mensagem": "Ofício baixado com sucesso"
                        }
                except Exception as e:
                    logger.debug(f"Erro ao processar link {i}: {str(e)}")
                    continue
            
            return {
                "sucesso": False,
                "erro": "oficio_nao_encontrado",
                "mensagem": "Processo existe no tribunal, mas o ofício requisitório não foi encontrado ou ainda não foi expedido"
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar no TJSP: {str(e)}")
            return {
                "sucesso": False,
                "erro": "erro_tjsp",
                "mensagem": f"Erro ao buscar no TJSP: {str(e)}"
            }
    
    def _buscar_trf(self, numero_processo, tribunal, page):
        """Busca processo nos TRFs"""
        try:
            logger.info(f"Buscando processo {numero_processo} no {tribunal}")
            
            time.sleep(3)
            page.screenshot(path=str(self.downloads_dir / f"{tribunal.lower()}_inicial.png"))
            
            numero_limpo = self.limpar_numero_processo(numero_processo)
            
            # Tentar preencher campo
            seletores = [
                "input[name='processo']",
                "input[name='numProcesso']",
                "input[id='processo']",
                "input[type='text']"
            ]
            
            preenchido = False
            for seletor in seletores:
                if page.locator(seletor).count() > 0:
                    page.fill(seletor, numero_limpo)
                    preenchido = True
                    logger.info(f"Campo preenchido com seletor: {seletor}")
                    break
            
            if not preenchido:
                return {
                    "sucesso": False,
                    "erro": "campo_nao_encontrado",
                    "mensagem": f"Campo de busca não encontrado no portal do {tribunal}"
                }
            
            # Clicar em consultar
            botoes = ["input[type='submit']", "button[type='submit']", "text=Consultar", "text=Pesquisar"]
            for botao in botoes:
                if page.locator(botao).count() > 0:
                    page.click(botao)
                    break
            
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(2)
            page.screenshot(path=str(self.downloads_dir / f"{tribunal.lower()}_resultado.png"))
            
            # Verificar resultado
            conteudo = page.content().lower()
            
            if "não encontrado" in conteudo or "não localizado" in conteudo:
                return {
                    "sucesso": False,
                    "erro": "processo_nao_existe",
                    "mensagem": f"O processo {numero_processo} não existe no {tribunal}"
                }
            
            # Buscar ofício
            links = page.locator("a").all()
            
            for link in links:
                try:
                    texto = link.inner_text().strip().lower()
                    if texto and ("ofício" in texto or "requisitório" in texto):
                        logger.info(f"Ofício encontrado: {link.inner_text()}")
                        
                        with page.expect_download(timeout=30000) as download_info:
                            link.click()
                        
                        download = download_info.value
                        filename = f"oficio_{tribunal}_{numero_processo.replace('/', '_').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        filepath = self.downloads_dir / filename
                        download.save_as(filepath)
                        
                        return {
                            "sucesso": True,
                            "caminho": str(filepath),
                            "mensagem": "Ofício baixado com sucesso"
                        }
                except Exception as e:
                    continue
            
            return {
                "sucesso": False,
                "erro": "oficio_nao_encontrado",
                "mensagem": "Processo existe no tribunal, mas o ofício requisitório não foi encontrado"
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar no {tribunal}: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"erro_{tribunal.lower()}",
                "mensagem": f"Erro ao buscar no {tribunal}: {str(e)}"
            }

if __name__ == "__main__":
    # Teste
    buscador = BuscadorOficioRequisitorio()
    
    # Testar TJRJ
    print("\n=== Testando TJRJ ===")
    resultado = buscador.buscar_oficio("7654313-59.2021.9.81.5556", "TJRJ")
    print(f"Resultado: {resultado}")
    
    print("\n📸 Verifique os screenshots em: data/oficios/")
    print("   - tjrj_inicial.png")
    print("   - tjrj_preenchido.png")
    print("   - tjrj_resultado.png")
