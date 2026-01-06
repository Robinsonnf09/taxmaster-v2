from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging
from datetime import datetime
import json
from pathlib import Path
import sys
sys.path.append("src")
from database import SessionLocal, Processo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/robot_tjsp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TJSP_Robot")

class TJSPRobot:
    def __init__(self):
        self.name = "TJSP"
        self.url = "https://www.tjsp.jus.br/Precatorios"
        self.data_dir = Path("data/tjsp")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def calcular_score(self, processo_data):
        """Calcula score de oportunidade baseado em multiplos fatores"""
        score = 5.0
        
        # Valor alto aumenta score
        if processo_data.get("valor_atualizado", 0) > 1000000:
            score += 2.0
        elif processo_data.get("valor_atualizado", 0) > 500000:
            score += 1.0
            
        # Fase avancada aumenta score
        if "expedido" in processo_data.get("fase", "").lower():
            score += 2.5
        elif "transito" in processo_data.get("fase", "").lower():
            score += 1.5
            
        # Prioridade aumenta score
        if processo_data.get("prioridade") == "Idoso":
            score += 1.0
            
        return min(score, 10.0)
        
    def salvar_banco_dados(self, processos):
        """Salva processos no banco de dados PostgreSQL"""
        db = SessionLocal()
        try:
            for proc_data in processos:
                # Verificar se processo ja existe
                processo_existente = db.query(Processo).filter(
                    Processo.numero_processo == proc_data["numero_processo"]
                ).first()
                
                if processo_existente:
                    # Atualizar
                    for key, value in proc_data.items():
                        setattr(processo_existente, key, value)
                    logger.info(f"Processo atualizado: {proc_data['numero_processo']}")
                else:
                    # Criar novo
                    novo_processo = Processo(**proc_data)
                    db.add(novo_processo)
                    logger.info(f"Novo processo criado: {proc_data['numero_processo']}")
                    
            db.commit()
            logger.info(f"Total de {len(processos)} processos salvos no banco")
        except Exception as e:
            logger.error(f"Erro ao salvar no banco: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
    def run(self):
        logger.info(f"Iniciando coleta - {self.name}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                logger.info(f"Acessando {self.url}")
                page.goto(self.url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                processos = []
                
                # Exemplo de extracao (adaptar conforme estrutura real do site)
                # Aguardar tabela de precatorios
                page.wait_for_selector("table", timeout=10000)
                
                # Extrair linhas da tabela
                rows = page.locator("table tbody tr").all()
                
                for row in rows[:10]:  # Limitar a 10 para teste
                    try:
                        cells = row.locator("td").all()
                        if len(cells) >= 5:
                            processo_data = {
                                "numero_processo": cells[0].inner_text().strip(),
                                "tribunal": self.name,
                                "tipo": "Precatorio",
                                "credor_nome": cells[1].inner_text().strip(),
                                "valor_principal": float(cells[2].inner_text().replace("R$", "").replace(".", "").replace(",", ".").strip()),
                                "fase": cells[3].inner_text().strip(),
                                "data_expedicao": datetime.now(),
                                "dados_completos": json.dumps({
                                    "fonte": self.url,
                                    "data_coleta": datetime.now().isoformat()
                                })
                            }
                            
                            # Calcular score
                            processo_data["score_oportunidade"] = self.calcular_score(processo_data)
                            processo_data["valor_atualizado"] = processo_data["valor_principal"] * 1.1
                            
                            processos.append(processo_data)
                            
                    except Exception as e:
                        logger.warning(f"Erro ao processar linha: {str(e)}")
                        continue
                
                # Salvar em arquivo JSON
                output_file = self.data_dir / f"coleta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(processos, f, ensure_ascii=False, indent=2, default=str)
                
                # Salvar no banco de dados
                if processos:
                    self.salvar_banco_dados(processos)
                
                logger.info(f"Coleta concluida: {len(processos)} processos encontrados")
                logger.info(f"Dados salvos em: {output_file}")
                
            except PlaywrightTimeout:
                logger.error("Timeout ao acessar o site")
            except Exception as e:
                logger.error(f"Erro durante a coleta: {str(e)}")
            finally:
                browser.close()

if __name__ == "__main__":
    robot = TJSPRobot()
    robot.run()
