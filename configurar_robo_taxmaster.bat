@echo off
setlocal

set PYTHON_EXE=python.exe
set PIP_EXE="%PYTHON_EXE%" -m pip

echo --- Iniciando Configuracao Automatica do Robo Taxmaster ---
echo.

:: 1. Verificar se o Python esta instalado e no PATH
echo --- Verificando instalacao do Python... ---

:: Tenta executar Python diretamente para verificar se esta no PATH e funcionando
"%PYTHON_EXE%" -c "import sys; sys.exit(0)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado ou nao esta funcionando corretamente no PATH.
    echo Por favor, instale o Python 3.12 (ou mais recente) de https://www.python.org/downloads/
    echo IMPORTANTE: Marque a opcao "Add python.exe to PATH" durante a instalacao.
    echo Pressione qualquer tecla para sair e instalar o Python.
    pause
    exit /b 1
) else (
    echo Python encontrado e funcionando no PATH.
)
echo.

:: 2. Instalar bibliotecas Python
echo --- Instalando bibliotecas Python necessarias (playwright, 2captcha-python)... ---
%PIP_EXE% install playwright 2captcha-python
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar bibliotecas Python. Verifique sua conexao com a internet ou as permissoes.
    pause
    exit /b 1
)
echo Bibliotecas instaladas com sucesso.
echo.

:: 3. Instalar navegadores do Playwright
echo --- Instalando navegadores para o Playwright (Chromium)... ---
%PYTHON_EXE% -m playwright install chromium
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar navegadores do Playwright.
    pause
    exit /b 1
)
echo Navegadores Playwright instalados com sucesso.
echo.

:: 4. Criar o arquivo do robo principal (robo_taxmaster_v2.py)
echo --- Criando o arquivo robo_taxmaster_v2.py ---
(
    echo import os
    echo import sys
    echo import subprocess
    echo import asyncio
    echo import csv
    echo import re
    echo from datetime import datetime
    echo from twocaptcha import TwoCaptcha
    echo.
    echo # --- CONFIGURACOES GLOBAIS ---
    echo API_KEY_2CAPTCHA = 'gGzLb2bGDCni_S5dsBKHHmAboPJJ4cTDATk'
    echo URL_TRF3 = "https://web.trf3.jus.br/consultas/Internet/ConsultaReqPre"
    echo HEADLESS_MODE = False
    echo FILTRO_VALOR_MINIMO_DIAMANTE = 500000.00
    echo FILTRO_VALOR_MINIMO_OURO = 100000.00
    echo # --- FIM CONFIGURACOES GLOBAIS ---
    echo.
    echo def bootstrap():
    echo     """Garante que o ambiente esteja pronto para rodar o robo."""
    echo     print("--- [SISTEMA] Verificando ambiente de execucao ---")
    echo     required_packages = ['playwright', '2captcha-python']
    echo     for package in required_packages:
    echo         try:
    echo             __import__(package.split('-')[0])
    echo         except ImportError:
    echo             print(f"--- [SISTEMA] Instalando {package}... ---")
    echo             subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    echo.
    echo     try:
    echo         subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    echo     except Exception as e:
    echo         print(f"--- [AVISO] Nao foi possivel instalar o Chromium automaticamente: {e}. Certifique-se de que o Edge esta atualizado. ---")
    echo     print("--- [SISTEMA] Ambiente pronto ---")
    echo.
    echo def parse_precatorio_data(raw_text):
    echo     """Extrai dados estruturados de um texto bruto de precatorio."""
    echo     data = {
    echo         "Numero_Processo": "N/A",
    echo         "CPF_CNPJ": "N/A",
    echo         "Valor_Bruto": 0.0,
    echo         "Ente_Devedor": "N/A",
    echo         "Natureza": "N/A",
    echo         "Status": "N/A",
    echo         "Data_Expedicao": "N/A"
    echo     }
    echo.
    echo     # Exemplo de Regex (precisara de ajustes finos com base no formato real do portal)
    echo     # Processo
    echo     match_proc = re.search(r'Processo:\s*(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})', raw_text)
    echo     if match_proc: data["Numero_Processo"] = match_proc.group(1)
    echo.
    echo     # CPF/CNPJ
    echo     match_doc = re.search(r'(CPF|CNPJ):\s*(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', raw_text)
    echo     if match_doc: data["CPF_CNPJ"] = match_doc.group(2)
    echo.
    echo     # Valor Bruto
    echo     match_valor = re.search(r'Valor\s*Bruto:\s*R\$\s*([\d\.,]+)', raw_text)
    echo     if match_valor: data["Valor_Bruto"] = float(match_valor.group(1).replace('.', '').replace(',', '.'))
    echo.
    echo     # Ente Devedor
    echo     match_ente = re.search(r'Ente\s*Devedor:\s*(.+?)(?=\s*Natureza|\s*Status|$)', raw_text)
    echo     if match_ente: data["Ente_Devedor"] = match_ente.group(1).strip()
    echo.
    echo     # Natureza
    echo     match_natureza = re.search(r'Natureza:\s*(Alimentar|Comum)', raw_text, re.IGNORECASE)
    echo     if match_natureza: data["Natureza"] = match_natureza.group(1).strip()
    echo.
    echo     # Status (Exemplo: "Expedido", "Pago", "Aguardando")
    echo     match_status = re.search(r'Status:\s*(.+?)(?=\s*Data\s*Expedicao|$)', raw_text)
    echo     if match_status: data["Status"] = match_status.group(1).strip()
    echo.
    echo     # Data de Expedicao
    echo     match_data = re.search(r'Data\s*Expedicao:\s*(\d{2}/\d{2}/\d{4})', raw_text)
    echo     if match_data: data["Data_Expedicao"] = match_data.group(1)
    echo.
    echo     return data
    echo.
    echo def classify_precatorio(data):
    echo     """Classifica o precatorio em DIAMANTE, OURO ou PRATA."""
    echo     if data["Ente_Devedor"] == "Uniao Federal" and ^^
    echo        data["Natureza"].lower() == "alimentar" and ^^
    echo        data["Valor_Bruto"] >= FILTRO_VALOR_MINIMO_DIAMANTE and ^^
    echo        data["Status"].lower() == "expedido":
    echo         return "DIAMANTE"
    echo     elif (data["Ente_Devedor"] == "Uniao Federal" or data["Ente_Devedor"] == "Estado de Sao Paulo") and ^^
    echo          (data["Natureza"].lower() == "alimentar" or data["Natureza"].lower() == "comum") and ^^
    echo          data["Valor_Bruto"] >= FILTRO_VALOR_MINIMO_OURO and ^^
    echo          data["Status"].lower() == "expedido":
    echo         return "OURO"
    echo     else:
    echo         return "PRATA"
    echo.
    echo async def robot_execution():
    echo     from playwright.async_api import async_playwright
    echo     solver = TwoCaptcha(API_KEY_2CAPTCHA)
    echo.
    echo     async with async_playwright() as p:
    echo         print(f"--- [LOG] Iniciando Robo Taxmaster v2.0: {datetime.now().strftime('%%H:%%M:%%S')} ---")
    echo.
    echo         browser = await p.chromium.launch(channel="msedge", headless=HEADLESS_MODE)
    echo         context = await browser.new_context()
    echo         page = await context.new_page()
    echo.
    echo         try:
    echo             print(f"--- [LOG] Acessando Portal TRF3: {URL_TRF3} ---")
    echo             await page.goto(URL_TRF3, wait_until="load", timeout=90000)
    echo.
    echo             # --- RESOLUCAO DE CAPTCHA AUTOMATICA ---
    echo             print("--- [CAPTCHA] Detectando e resolvendo CAPTCHA... ---")
    echo             captcha_image_locator = page.locator("#captchaImage")
    echo             captcha_input_locator = page.locator("#captchaText")
    echo             submit_button_locator = page.locator("#btnPesquisar")
    echo.
    echo             if await captcha_image_locator.is_visible():
    echo                 captcha_image_path = "captcha.png"
    echo                 await captcha_image_locator.screenshot(path=captcha_image_path)
    echo.
    echo                 try:
    echo                     result = solver.normal(captcha_image_path)
    echo                     captcha_solution = result['code']
    echo                     print(f"--- [CAPTCHA] Solucao obtida: {captcha_solution} ---")
    echo                     await captcha_input_locator.fill(captcha_solution)
    echo                     await submit_button_locator.click()
    echo                     await page.wait_for_loadstate('networkidle')
    echo                 except Exception as e:
    echo                     print(f"--- [ERRO CAPTCHA] Falha ao resolver ou submeter CAPTCHA: {str(e)} ---")
    echo             else:
    echo                 print("--- [CAPTCHA] CAPTCHA nao detectado ou ja resolvido. Continuando... ---")
    echo             # --- FIM RESOLUCAO DE CAPTCHA ---
    echo.
    echo             # --- AQUI VOCE PODE ADICIONAR LOGICA PARA PREENCHER FILTROS DE BUSCA (DATA, ENTE, ETC.) ---
    echo             # Exemplo: await page.locator("#campoDataInicial").fill("01/01/2025")
    echo             # Exemplo: await page.locator("#campoEnteDevedor").select_option("UNIAO FEDERAL")
    echo             # --- FIM FILTROS ---
    echo.
    echo             print("--- [DADOS] Extraindo informacoes da tabela de oficios... ---")
    echo.
    echo             # Localizador generico para linhas de dados na tabela de resultados
    echo             # Ajuste este seletor conforme a estrutura HTML da tabela de resultados do TRF3
    echo             linhas_resultados = await page.locator(".grid-resultado tr").all()
    echo.
    echo             if len(linhas_resultados) <= 1:
    echo                 print("--- [AVISO] Nenhuma requisicao encontrada com os filtros aplicados. ---")
    echo             else:
    echo                 all_precatorios = []
    echo                 for i, linha in enumerate(linhas_resultados):
    echo                     if i == 0: continue
    echo.
    echo                     raw_text = await linha.inner_text()
    echo                     parsed_data = parse_precatorio_data(raw_text)
    echo                     parsed_data["Timestamp_Captura"] = datetime.now().isoformat()
    echo.
    echo                     parsed_data["Prioridade"] = classify_precatorio(parsed_data)
    echo                     all_precatorios.append(parsed_data)
    echo.
    echo                     print(f"--- [CAPTURADO] {parsed_data['Prioridade']}: {parsed_data['Numero_Processo']} - R$%.2f ---" %% parsed_data['Valor_Bruto'])
    echo.
    echo                 # Geracao de CSVs separados por prioridade
    echo                 output_dir = "Taxmaster_Precatorios"
    echo                 os.makedirs(output_dir, exist_ok=True)
    echo.
    echo                 fieldnames = list(all_precatorios[0].keys()) if all_precatorios else []
    echo.
    echo                 for categoria in ["DIAMANTE", "OURO", "PRATA"]:
    echo                     categorized_data = [p for p in all_precatorios if p["Prioridade"] == categoria]
    echo                     if categorized_data:
    echo                         filename = os.path.join(output_dir, f"{categoria}_Precatorios_{datetime.now().strftime('%%Y%%m%%d_%%H%%M')}.csv")
    echo                         with open(filename, mode='w', newline='', encoding='utf-8') as file:
    echo                             writer = csv.DictWriter(file, fieldnames=fieldnames)
    echo                             writer.writeheader()
    echo                             writer.writerows(categorized_data)
    echo                         print(f"--- [SUCESSO] {len(categorized_data)} precatorios '{categoria}' salvos em: {filename} ---")
    echo                     else:
    echo                         print(f"--- [INFO] Nenhuma oportunidade '{categoria}' encontrada nesta execucao. ---")
    echo.
    echo         except Exception as e:
    echo             print(f"--- [ERRO CRITICO] Falha na automacao: {str(e)} ---", file=sys.stderr)
    echo         finally:
    echo             await browser.close()
    echo             print("--- [SISTEMA] Robo Taxmaster v2.0 finalizado. ---")
    echo.
    echo if __name__ == "__main__":
    echo     bootstrap()
    echo     asyncio.run(robot_execution())
) > robo_taxmaster_v2.py
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar o arquivo robo_taxmaster_v2.py.
    pause
    exit /b 1
)
echo Arquivo robo_taxmaster_v2.py criado com sucesso.
echo.

:: 5. Criar o arquivo de execucao rapida (iniciar_robo_taxmaster.bat)
echo --- Criando o arquivo iniciar_robo_taxmaster.bat ---
(
    echo @echo off
    echo setlocal
    echo echo --- Iniciando Robo Taxmaster ---
    echo python robo_taxmaster_v2.py
    echo echo --- Execucao Concluida ---
    echo pause
) > iniciar_robo_taxmaster.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar o arquivo iniciar_robo_taxmaster.bat.
    pause
    exit /b 1
)
echo Arquivo iniciar_robo_taxmaster.bat criado com sucesso.
echo.

echo --- Configuracao Concluida! ---
echo Agora, para executar o robo, basta digitar:
echo   .\iniciar_robo_taxmaster.bat
echo ou clicar duas vezes no arquivo "iniciar_robo_taxmaster.bat" no Explorador de Arquivos.
echo.
pause
endlocal