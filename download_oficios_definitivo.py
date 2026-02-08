import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

# Configurações
PASTA_DESTINO = 'oficios_requisitorios_tjsp'
CSV_FILE = 'precatorios_bahia_oportunidades.csv'
PROGRESSO_FILE = 'progresso_download.json'
ERRO_LOG = 'erros_download.txt'
MAX_TENTATIVAS = 3
TIMEOUT_DOWNLOAD = 30

os.makedirs(PASTA_DESTINO, exist_ok=True)

def carregar_progresso():
    if os.path.exists(PROGRESSO_FILE):
        with open(PROGRESSO_FILE, 'r') as f:
            return json.load(f)
    return {'baixados': [], 'total': 0}

def salvar_progresso(dados):
    with open(PROGRESSO_FILE, 'w') as f:
        json.dump(dados, f, indent=2)

def log_erro(mensagem):
    with open(ERRO_LOG, 'a', encoding='utf-8') as f:
        f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {mensagem}\n')

def validar_pdf(caminho):
    try:
        with open(caminho, 'rb') as f:
            header = f.read(10)
            return header.startswith(b'%PDF-')
    except:
        return False

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    prefs = {
        'download.default_directory': os.path.abspath(PASTA_DESTINO),
        'download.prompt_for_download': False,
        'plugins.always_open_pdf_externally': True
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def baixar_oficio(driver, numero_oficio, tentativa=1):
    try:
        url = f'https://esaj.tjsp.jus.br/cposg/open.do?gateway=true'
        driver.get(url)
        time.sleep(2)
        
        campo_numero = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'nuOficioRequisitorio'))
        )
        campo_numero.clear()
        campo_numero.send_keys(numero_oficio)
        
        botao_pesquisar = driver.find_element(By.ID, 'pbConsultar')
        botao_pesquisar.click()
        
        time.sleep(3)
        
        link_pdf = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'PDF'))
        )
        link_pdf.click()
        
        nome_arquivo = f'{numero_oficio}.pdf'
        caminho_completo = os.path.join(PASTA_DESTINO, nome_arquivo)
        
        inicio = time.time()
        while time.time() - inicio < TIMEOUT_DOWNLOAD:
            if os.path.exists(caminho_completo):
                time.sleep(1)
                if validar_pdf(caminho_completo):
                    return True, 'Sucesso'
                else:
                    os.remove(caminho_completo)
                    return False, 'PDF inválido (HTML)'
            time.sleep(0.5)
        
        return False, 'Timeout'
        
    except Exception as e:
        if tentativa < MAX_TENTATIVAS:
            time.sleep(2)
            return baixar_oficio(driver, numero_oficio, tentativa + 1)
        return False, str(e)

def main():
    print('=' * 60)
    print('DOWNLOAD DE OFÍCIOS REQUISITÓRIOS - TJSP')
    print('=' * 60)
    
    if not os.path.exists(CSV_FILE):
        print(f'\n❌ ERRO: Arquivo {CSV_FILE} não encontrado!')
        return
    
    df = pd.read_csv(CSV_FILE)
    progresso = carregar_progresso()
    
    print(f'\n📊 Total de registros: {len(df)}')
    print(f'✅ Já baixados: {len(progresso["baixados"])}')
    print(f'⏳ Faltam: {len(df) - len(progresso["baixados"])}\n')
    
    driver = setup_driver()
    
    sucesso = erro = 0
    
    try:
        for idx, row in df.iterrows():
            numero_oficio = row['numero_oficio']
            
            if numero_oficio in progresso['baixados']:
                continue
            
            resultado, mensagem = baixar_oficio(driver, numero_oficio)
            
            if resultado:
                sucesso += 1
                progresso['baixados'].append(numero_oficio)
                print(f'✅ [{sucesso + erro}/{len(df)}] {numero_oficio} - OK')
            else:
                erro += 1
                log_erro(f'{numero_oficio}: {mensagem}')
                print(f'❌ [{sucesso + erro}/{len(df)}] {numero_oficio} - ERRO: {mensagem}')
            
            progresso['total'] = sucesso + erro
            salvar_progresso(progresso)
            
            if (sucesso + erro) % 50 == 0:
                print(f'\n📊 PROGRESSO: {sucesso} sucessos | {erro} erros\n')
    
    except KeyboardInterrupt:
        print('\n\n⏸️ Download interrompido pelo usuário!')
        print('Progresso salvo. Execute novamente para continuar.')
    
    finally:
        driver.quit()
        print('\n' + '=' * 60)
        print(f'🏁 FINALIZADO!')
        print(f'✅ Sucessos: {sucesso}')
        print(f'❌ Erros: {erro}')
        print('=' * 60)

if __name__ == '__main__':
    main()
