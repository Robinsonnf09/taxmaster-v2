from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging
from datetime import datetime
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/robot_tjrj.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TJRJ_Robot")

class TJRJRobot:
    def __init__(self):
        self.name = "TJRJ"
        self.url = "https://www.tjrj.jus.br"
        self.data_dir = Path("data/tjrj")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
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
                # Navegar para o site
                logger.info(f"Acessando {self.url}")
                page.goto(self.url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Aqui voce implementa a logica especifica do TJRJ
                # Exemplo: buscar precatorios
                
                # Buscar link de precatorios
                precatorios_link = page.locator("text=/precatório/i").first
                if precatorios_link.is_visible():
                    logger.info("Link de precatorios encontrado")
                    precatorios_link.click()
                    page.wait_for_load_state("networkidle")
                
                # Extrair dados
                processos = []
                # Implementar logica de extracao aqui
                
                # Salvar dados
                output_file = self.data_dir / f"coleta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(processos, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Coleta concluida: {len(processos)} processos encontrados")
                logger.info(f"Dados salvos em: {output_file}")
                
            except PlaywrightTimeout:
                logger.error("Timeout ao acessar o site")
            except Exception as e:
                logger.error(f"Erro durante a coleta: {str(e)}")
            finally:
                browser.close()

if __name__ == "__main__":
    robot = TJRJRobot()
    robot.run()
