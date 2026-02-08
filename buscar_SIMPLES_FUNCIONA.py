import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl
from datetime import datetime

class BuscadorSimples:
    
    def __init__(self):
        self.pasta_oficios = 'oficios_requisitorios_tjsp_NOVOS'
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.driver = None
    
    def iniciar_chrome(self):
        print('\n🌐 Chrome...')
        
        options = webdriver.ChromeOptions()
        
        # Configurar download automático
        prefs = {
            'download.default_directory': os.path.abspath(self.pasta_oficios),
            'download.prompt_for_download': False,
            'plugins.always_open_pdf_externally': True,
            'profile.default_content_settings.popups': 0
        }
        options.add_experimental_option('prefs', prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        print(f'✅ Pasta: {os.path.abspath(self.pasta_oficios)}')
    
    def fazer_login(self):
        print('\n🔐 Login...')
        self.driver.get('https://esaj.tjsp.jus.br/sajcas/login')
        input('\n>>> ENTER após login <<<\n')
    
    def aguardar_downloads(self, num_esperado):
        '''Aguarda downloads completarem'''
        print('   ⏳ Aguardando...', end='')
        
        for _ in range(30):  # 30 segundos max
            arquivos = os.listdir(self.pasta_oficios)
            
            # Arquivos .crdownload = download em andamento
            em_download = [f for f in arquivos if f.endswith('.crdownload')]
            
            if len(em_download) == 0:
                time.sleep(1)
                return True
            
            print('.', end='', flush=True)
            time.sleep(1)
        
        return False
    
    def buscar_processo(self, numero_processo, idx_processo, total):
        try:
            numero_limpo = numero_processo.replace('-', '').replace('.', '')
            
            print(f'\n[{idx_processo}/{total}] {numero_processo}')
            
            # Ir para consulta de requisitórios
            url = 'https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do'
            self.driver.get(url)
            time.sleep(2)
            
            # Buscar pelo código do processo
            input_codigo = self.driver.find_element(By.ID, 'codigoProcesso')
            input_codigo.clear()
            input_codigo.send_keys(numero_limpo)
            
            # Clicar em consultar
            btn = self.driver.find_element(By.ID, 'pbConsultar')
            btn.click()
            
            time.sleep(3)
            
            # Procurar links de PDF
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="pdf"]')
            
            if not links:
                print('   ❌ Sem ofícios')
                return 0
            
            print(f'   ✅ {len(links)} ofícios')
            
            antes = len([f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')])
            
            # Clicar em cada link
            for idx, link in enumerate(links, 1):
                try:
                    print(f'   📥 {idx}/{len(links)}...', end='')
                    
                    # Clicar para baixar
                    self.driver.execute_script('arguments[0].click();', link)
                    
                    time.sleep(2)
                    
                    print(' ✅')
                    
                except:
                    print(' ❌')
                    continue
            
            # Aguardar downloads
            self.aguardar_downloads(len(links))
            
            depois = len([f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')])
            baixados = depois - antes
            
            print(f'   📊 Baixados: {baixados}')
            
            return baixados
            
        except Exception as e:
            print(f'   ❌ Erro: {str(e)[:50]}')
            return 0
    
    def executar(self):
        print('='*70)
        print('🚀 BUSCAR OFÍCIOS - VERSÃO SIMPLES')
        print('='*70)
        
        # Carregar planilha
        wb = openpyxl.load_workbook('processos_push_20260126_185045.xlsx')
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                processos.append(str(row[0]))
        
        print(f'\n📊 {len(processos)} processos')
        
        confirma = input('\nIniciar? (s/n): ').lower()
        
        if confirma != 's':
            return
        
        try:
            self.iniciar_chrome()
            self.fazer_login()
            
            total_baixados = 0
            
            for idx, processo in enumerate(processos, 1):
                baixados = self.buscar_processo(processo, idx, len(processos))
                total_baixados += baixados
                
                if idx % 10 == 0:
                    pdfs = len([f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')])
                    print(f'\n📊 PROGRESSO: {idx}/{len(processos)} - {pdfs} PDFs\n')
            
            print('\n' + '='*70)
            print('🎉 CONCLUÍDO!')
            print('='*70)
            
            pdfs_finais = len([f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')])
            print(f'\n📄 PDFs: {pdfs_finais}')
            print(f'📁 {self.pasta_oficios}/')
            
        finally:
            input('\n\nENTER...\n')
            if self.driver:
                self.driver.quit()

if __name__ == '__main__':
    buscador = BuscadorSimples()
    buscador.executar()
