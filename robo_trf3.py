import os
import sys
import subprocess
import asyncio
import csv
from datetime import datetime

def bootstrap():
    """Garante que o ambiente esteja pronto para rodar o robô."""
    try:
        import playwright
    except ImportError:
        print("--- [SISTEMA] Instalando pacotes necessários... ---")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

async def robot_execution():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        print(f"--- [LOG] Iniciando Robô: {datetime.now().strftime('%H:%M:%S')} ---")
        
        # Lançamento no Microsoft Edge
        browser = await p.chromium.launch(channel="msedge", headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # URL OFICIAL DE CONSULTA DO TRF3
        url = "https://web.trf3.jus.br/consultas/Internet/ConsultaReqPre"
        
        try:
            print(f"--- [LOG] Acessando Portal Oficial: {url} ---")
            await page.goto(url, wait_until="load", timeout=90000)
            
            print("--- [AÇÃO] O portal oficial exige preenchimento de CAPTCHA ou Filtro. ---")
            print("--- [AÇÃO] Você tem 30 segundos para preencher e clicar em 'Pesquisar'. ---")
            
            # Pausa estendida para você preencher os filtros e o Captcha manualmente no piloto
            await page.wait_for_timeout(30000)

            # Extração dos resultados
            print("--- [DADOS] Tentando capturar resultados da consulta... ---")
            
            # O TRF3 costuma exibir resultados em tabelas ou grids. Vamos capturar o conteúdo visível.
            conteudo = await page.content()
            
            if "Não foram encontrados registros" in conteudo:
                print("--- [AVISO] A consulta não retornou resultados com os filtros usados. ---")
            else:
                # Captura simples de linhas de dados (adaptável conforme o resultado da busca)
                linhas = await page.locator("tr").all()
                dados_extraidos = []
                for i, linha in enumerate(linhas):
                    texto = await linha.inner_text()
                    registro = texto.replace('\t', ' | ').replace('\n', ' ')
                    dados_extraidos.append([datetime.now().isoformat(), registro])
                    if i < 10: # Log dos primeiros 10 para não poluir o terminal
                        print(f"--- [CAPTURADO] Item {i}: {registro[:100]}...")

                # Geração do CSV
                filename = f"extracao_trf3_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                with open(filename, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Dados Capturados"])
                    writer.writerows(dados_extraidos)
                print(f"--- [SUCESSO] Dados salvos em: {filename} ---")

        except Exception as e:
            print(f"--- [ERRO] Falha durante a navegação: {str(e)} ---")
        finally:
            await browser.close()
            print("--- [SISTEMA] Robô finalizado. ---")

if __name__ == "__main__":
    bootstrap()
    asyncio.run(robot_execution())