"""
Scraper PJe com TOKEN A3 usando MICROSOFT EDGE
Edge tem melhor suporte a certificados digitais no Windows!
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class ScraperPJeEdgeTokenA3:
    """Scraper usando Microsoft Edge com certificado A3"""
    
    def __init__(self):
        self.driver = None
        self.token_info = {
            'titular': 'ELIANA DE CAMARGO FIGUEIREDO',
            'cpf': '16111791818',
            'tipo': 'RFB e-CPF A3',
            'leitor': 'Giesecke & Devrient StarSign CUT S'
        }
    
    def iniciar_edge_com_certificado(self):
        """Inicia Microsoft Edge configurado para usar certificado A3"""
        
        print("\n🌐 Iniciando Microsoft Edge...")
        print(f"   Certificado: {self.token_info['titular']}")
        print(f"   Tipo: {self.token_info['tipo']}")
        print(f"   Leitor: {self.token_info['leitor']}")
        
        edge_options = Options()
        
        # Configurações básicas
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # CRÍTICO: Configurações SSL/TLS para certificado digital
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--allow-running-insecure-content')
        
        # Edge respeita certificados do Windows automaticamente!
        # Não precisa especificar caminho do certificado
        
        # Download automático de ofícios
        pasta_oficios = os.path.join(os.getcwd(), 'oficios_baixados')
        os.makedirs(pasta_oficios, exist_ok=True)
        
        prefs = {
            'download.default_directory': pasta_oficios,
            'download.prompt_for_download': False,
            'plugins.always_open_pdf_externally': True,
            'profile.default_content_setting_values.automatic_downloads': 1
        }
        edge_options.add_experimental_option('prefs', prefs)
        
        # Usar perfil padrão do Edge (onde certificados estão)
        user_data = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
        
        # IMPORTANTE: Comentar estas linhas para primeiro teste
        # edge_options.add_argument(f'--user-data-dir={user_data}')
        # edge_options.add_argument('--profile-directory=Default')
        
        # Iniciar Edge
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=edge_options)
        
        print("✅ Edge iniciado com sucesso!")
        return self.driver
    
    def acessar_pje_com_certificado(self, url_pje):
        """Acessa PJe e aguarda login com certificado"""
        
        if not self.driver:
            self.iniciar_edge_com_certificado()
        
        print(f"\n🌐 Acessando: {url_pje}")
        self.driver.get(url_pje)
        
        print("\n⚠️  INSTRUÇÕES:")
        print("   1. Na página do PJe, clique em 'Certificado Digital'")
        print("   2. Windows vai solicitar seleção de certificado")
        print("   3. Selecione: ELIANA DE CAMARGO FIGUEIREDO")
        print("   4. Digite o PIN do token quando solicitado")
        print("   5. Aguarde o login automático")
        print("\n   Após LOGAR COM SUCESSO, volte aqui!")
        
        input("\n>>> Pressione ENTER após fazer login completo <<<")
        
        # Verificar se logou
        url_atual = self.driver.current_url
        print(f"\n📍 URL atual: {url_atual}")
        
        if "login" not in url_atual.lower():
            print("✅ LOGIN REALIZADO COM SUCESSO!")
            print("   Você está autenticado no sistema!")
            return True
        else:
            print("⚠️  Parece que ainda está na tela de login")
            print("   Tente novamente ou verifique o certificado")
            return False
    
    def buscar_oficio_processo(self, numero_processo):
        """Busca ofício requisitório de um processo"""
        
        try:
            print(f"\n🔍 Buscando ofício do processo: {numero_processo}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # ATENÇÃO: Adaptar seletores conforme interface real do PJe
            # Este é um exemplo genérico
            
            # Campo de busca de processo
            try:
                campo_busca = wait.until(
                    EC.presence_of_element_located((By.ID, "numeroProcesso"))
                )
                campo_busca.clear()
                campo_busca.send_keys(numero_processo)
                
                # Botão pesquisar
                btn_pesquisar = self.driver.find_element(By.ID, "btnPesquisar")
                btn_pesquisar.click()
                
                time.sleep(3)
                
                print("✅ Processo localizado!")
                
                # Procurar link do ofício requisitório
                # Adaptar conforme HTML real
                oficios = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Ofício")
                
                if oficios:
                    print(f"✅ Encontrados {len(oficios)} ofícios")
                    
                    # Clicar no primeiro ofício
                    oficios[0].click()
                    time.sleep(2)
                    
                    print("✅ Ofício baixado/aberto!")
                    return True
                else:
                    print("⚠️  Ofício não encontrado neste processo")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao buscar processo: {str(e)}")
                return False
        
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def processar_planilha(self, arquivo_excel):
        """Processa planilha com múltiplos processos"""
        
        import openpyxl
        
        print(f"\n📊 Processando planilha: {arquivo_excel}")
        
        wb = openpyxl.load_workbook(arquivo_excel)
        ws = wb.active
        
        resultados = []
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            numero_processo = row[0]
            tribunal = row[1] if len(row) > 1 else "TRF1"
            
            if numero_processo:
                print(f"\n{'='*60}")
                print(f"Processo {numero_processo} - {tribunal}")
                
                sucesso = self.buscar_oficio_processo(numero_processo)
                
                resultados.append({
                    'processo': numero_processo,
                    'tribunal': tribunal,
                    'sucesso': sucesso
                })
                
                time.sleep(2)  # Intervalo entre buscas
        
        # Resumo
        print(f"\n{'='*60}")
        print("📊 RESUMO:")
        print(f"   Total processado: {len(resultados)}")
        print(f"   Sucesso: {sum(1 for r in resultados if r['sucesso'])}")
        print(f"   Falhas: {sum(1 for r in resultados if not r['sucesso'])}")
        
        return resultados
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Edge fechado")

# TESTE
if __name__ == "__main__":
    print("="*70)
    print("🌐 SCRAPER PJE COM MICROSOFT EDGE + TOKEN A3")
    print("="*70)
    
    scraper = ScraperPJeEdgeTokenA3()
    
    try:
        print("\n📋 PRÉ-REQUISITOS:")
        print("   ✅ Token A3 conectado")
        print("   ✅ PIN do token em mãos")
        print("   ✅ Microsoft Edge instalado")
        
        input("\nPressione ENTER para iniciar o Edge...")
        
        # URL do PJe
        url_pje = "https://pje1g.trf1.jus.br/pje/login.seam"
        
        # Acessar e fazer login
        if scraper.acessar_pje_com_certificado(url_pje):
            print("\n✅ Sistema pronto!")
            print("\n💡 OPÇÕES:")
            print("   1. Buscar processo individual")
            print("   2. Processar planilha em lote")
            print("   3. Sair")
            
            opcao = input("\nEscolha (1/2/3): ")
            
            if opcao == "1":
                numero = input("\nNúmero do processo: ")
                scraper.buscar_oficio_processo(numero)
            
            elif opcao == "2":
                arquivo = input("\nCaminho da planilha: ")
                scraper.processar_planilha(arquivo)
        
        input("\n\nPressione ENTER para fechar o Edge...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
    
    finally:
        scraper.fechar()
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO!")
    print("="*70)
