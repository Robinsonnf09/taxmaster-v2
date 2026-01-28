import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl
import requests
from datetime import datetime

class BuscadorOficiosCorrigido:
    
    def __init__(self):
        self.pasta_oficios = 'oficios_requisitorios_tjsp'
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.session = requests.Session()
        self.driver = None
    
    def iniciar_chrome(self):
        print('\n🌐 Iniciando Chrome...')
        
        options = webdriver.ChromeOptions()
        
        prefs = {
            'download.default_directory': os.path.abspath(self.pasta_oficios),
            'download.prompt_for_download': False,
            'plugins.always_open_pdf_externally': True,
            'profile.default_content_settings.popups': 0
        }
        options.add_experimental_option('prefs', prefs)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        print('   ✅ Chrome iniciado!')
        print(f'📁 PDFs em: {os.path.abspath(self.pasta_oficios)}')
    
    def fazer_login(self):
        print('\n🔐 Login...')
        
        self.driver.get('https://esaj.tjsp.jus.br/sajcas/login')
        
        print('\n' + '='*70)
        print('>>> FAÇA LOGIN NO E-SAJ <<<')
        print('='*70)
        
        input('\n>>> Pressione ENTER após fazer login <<<\n')
        
        print('   ✅ Login OK!')
    
    def baixar_pdf_automatico(self, url_pdf, nome_arquivo):
        '''VERSÃO CORRIGIDA - Valida se é PDF antes de salvar'''
        
        try:
            # Transferir cookies
            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://esaj.tjsp.jus.br/'
            }
            
            response = self.session.get(url_pdf, headers=headers, timeout=30)
            
            if response.status_code == 200:
                
                # ✅ VALIDAÇÃO CRÍTICA: Verificar se é PDF
                if not response.content.startswith(b'%PDF-'):
                    # Não é PDF - pode ser HTML ou erro
                    return False, 0
                
                # ✅ É PDF válido!
                if len(response.content) > 1000:
                    caminho = os.path.join(self.pasta_oficios, nome_arquivo)
                    
                    with open(caminho, 'wb') as f:
                        f.write(response.content)
                    
                    return True, len(response.content)
            
            return False, 0
            
        except Exception as e:
            return False, 0
    
    def buscar_oficios_processo(self, numero_processo):
        try:
            numero_limpo = numero_processo.replace('-', '').replace('.', '')
            
            url = f'https://esaj.tjsp.jus.br/cpopg/show.do?processo.numero={numero_processo}'
            
            self.driver.get(url)
            time.sleep(2)
            
            # Tentar encontrar lista de ofícios
            try:
                tabela = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'requisitorio'))
                )
            except:
                return 0, 0
            
            # Buscar links de PDFs
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*=\"pdf\"]')
            
            if not links:
                return 0, 0
            
            total_oficios = len(links)
            baixados = 0
            
            for idx_of, link in enumerate(links, 1):
                try:
                    url_pdf = link.get_attribute('href')
                    
                    if not url_pdf or 'pdf' not in url_pdf.lower():
                        continue
                    
                    nome_arquivo = f'{numero_limpo}_of{idx_of}.pdf'
                    
                    # Baixar com validação
                    sucesso, tamanho = self.baixar_pdf_automatico(
                        url_pdf, 
                        nome_arquivo
                    )
                    
                    if sucesso:
                        baixados += 1
                    
                    time.sleep(0.5)
                    
                except:
                    continue
            
            return total_oficios, baixados
            
        except:
            return 0, 0
    
    def processar_planilha(self, arquivo_excel):
        print('\n📊 Carregando planilha...')
        
        wb = openpyxl.load_workbook(arquivo_excel)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                processos.append(str(row[0]))
        
        print(f'   ✅ {len(processos)} processos')
        
        return processos
    
    def executar(self, arquivo_excel='processos_push_20260126_185045.xlsx'):
        print('='*70)
        print('🔍 BUSCAR OFÍCIOS - VERSÃO CORRIGIDA')
        print('='*70)
        
        processos = self.processar_planilha(arquivo_excel)
        
        print(f'\n📋 Total: {len(processos)} processos')
        
        confirma = input('\nIniciar busca? (s/n): ').lower()
        
        if confirma != 's':
            print('\n❌ Cancelado')
            return
        
        try:
            self.iniciar_chrome()
            self.fazer_login()
            
            print('\n' + '='*70)
            print('📋 PROCESSANDO...')
            print('='*70)
            
            total_oficios = 0
            total_baixados = 0
            processos_com_oficio = 0
            
            inicio = datetime.now()
            
            for idx, processo in enumerate(processos, 1):
                print(f'\n[{idx}/{len(processos)}] {processo}', end=' ')
                
                oficios, baixados = self.buscar_oficios_processo(processo)
                
                if oficios > 0:
                    processos_com_oficio += 1
                    total_oficios += oficios
                    total_baixados += baixados
                    
                    print(f'✅ {baixados}/{oficios} PDFs')
                else:
                    print('❌ Sem ofícios')
                
                if idx % 10 == 0:
                    pdfs_pasta = len([f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')])
                    print(f'\n   📊 Progresso: {idx}/{len(processos)} ({idx/len(processos)*100:.1f}%)')
                    print(f'   📄 PDFs válidos na pasta: {pdfs_pasta}')
            
            fim = datetime.now()
            duracao = int((fim - inicio).total_seconds() / 60)
            
            print('\n' + '='*70)
            print('🎉 CONCLUÍDO!')
            print('='*70)
            
            pdfs_finais = len([f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')])
            
            print(f'\n   Total processos: {len(processos)}')
            print(f'   ✅ Com ofício: {processos_com_oficio}')
            print(f'   📄 PDFs válidos: {pdfs_finais}')
            print(f'   ⏱️  Tempo: {duracao} min')
            print(f'   📁 Pasta: {self.pasta_oficios}/')
            
        except Exception as e:
            print(f'\n❌ Erro: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            if self.driver:
                input('\n\nENTER para fechar...\n')
                self.driver.quit()

if __name__ == '__main__':
    buscador = BuscadorOficiosCorrigido()
    buscador.executar()
