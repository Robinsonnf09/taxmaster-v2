from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Iniciar Chrome
options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Login
    driver.get('https://esaj.tjsp.jus.br/sajcas/login')
    input('\n>>> ENTER após login <<<\n')
    
    # Ir para requisitórios
    driver.get('https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do')
    time.sleep(3)
    
    print('\n🔍 ANALISANDO PÁGINA...\n')
    
    # Procurar todos os inputs
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    print(f'📝 INPUTS ENCONTRADOS: {len(inputs)}')
    for inp in inputs[:10]:
        id_val = inp.get_attribute('id')
        name_val = inp.get_attribute('name')
        type_val = inp.get_attribute('type')
        placeholder = inp.get_attribute('placeholder')
        print(f'   ID: {id_val or \"(sem id)\"} | Name: {name_val or \"(sem name)\"} | Type: {type_val} | Placeholder: {placeholder}')
    
    # Procurar botões
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    print(f'\n🔘 BUTTONS: {len(buttons)}')
    for btn in buttons:
        id_val = btn.get_attribute('id')
        text = btn.text
        print(f'   ID: {id_val or \"(sem id)\"} | Texto: {text}')
    
    input('\n\nENTER...\n')
    
finally:
    driver.quit()
