"""
BUSCADOR DE OFÍCIOS REQUISITÓRIOS TJSP - VERSÃO CORRIGIDA
Lê planilha Excel e baixa automaticamente todos os ofícios requisitórios em PDF
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import os
import openpyxl
from datetime import datetime
import requests
from dotenv import load_dotenv

class BuscadorRequisitoriosProfissional:
    
    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        
        self.driver = None
        self.session = None
        
        # Configurações do .env
        self.usuario = os.getenv("TJSP_USUARIO")
        self.senha = os.getenv("TJSP_SENHA")
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_requisitorios_tjsp")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_push_20260126_185045.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        # Criar pasta se não existir
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        # Controle de resultados
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
    
    def iniciar_chrome(self):
        """Inicia o Chrome com configurações otimizadas"""
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-extensions')
        
        # Configurações de download
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.session = requests.Session()
        
        print("✅ Chrome iniciado com sucesso!")
        print(f"📁 PDFs serão salvos em: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login(self):
        """Faz login único no e-SAJ TJSP"""
        print(f"\n🔐 Fazendo login no TJSP...")
        
        self.driver.get("https://esaj.tjsp.jus.br/sajcas/login")
        time.sleep(3)
        
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Aguardar campo de usuário
            campo_usuario = wait.until(
                EC.presence_of_element_located((By.ID, "usernameForm"))
            )
            
            campo_senha = self.driver.find_element(By.ID, "passwordForm")
            botao_login = self.driver.find_element(By.ID, "pbEntrar")
            
            # Preencher credenciais
            campo_usuario.clear()
            campo_usuario.send_keys(self.usuario)
            
            campo_senha.clear()
            campo_senha.send_keys(self.senha)
            
            # Clicar em entrar
            botao_login.click()
            
            time.sleep(4)
            
            # Verificar se logou
            if "sajcas/login" not in self.driver.current_url:
                print("✅ Login realizado com sucesso!")
                
                # Salvar cookies para requisições
                for cookie in self.driver.get_cookies():
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                return True
            else:
                print("❌ Falha no login - Verifique usuário e senha no .env")
                return False
                
        except Exception as e:
            print(f"❌ Erro no login: {str(e)}")
            return False
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca o processo e extrai o código interno"""
        try:
            url_consulta = "https://esaj.tjsp.jus.br/cpopg/open.do"
            self.driver.get(url_consulta)
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Clicar no radio button de número antigo
            try:
                radio = wait.until(EC.element_to_be_clickable((By.ID, "radioNumeroAntigo")))
                radio.click()
                time.sleep(0.5)
            except:
                pass
            
            # Preencher campo de busca
            try:
                campo = wait.until(EC.visibility_of_element_located((By.ID, "nuProcessoAntigoFormatado")))
            except:
                return None
            
            campo.clear()
            time.sleep(0.2)
            campo.send_keys(numero_processo)
            time.sleep(0.3)
            campo.send_keys(Keys.RETURN)
            
            time.sleep(2.5)
            
            # Extrair código da URL
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                return codigo
            
            return None
            
        except Exception as e:
            return None
    
    def extrair_foro(self, numero_processo):
        """Extrai o foro do número do processo"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def baixar_pdf(self, url_pdf, nome_arquivo):
        """Baixa o PDF usando requests"""
        try:
            # Atualizar cookies da sessão
            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://esaj.tjsp.jus.br/'
            }
            
            response = self.session.get(url_pdf, headers=headers, timeout=30)
            
            if response.status_code == 200 and len(response.content) > 1000:
                caminho = os.path.join(self.pasta_oficios, nome_arquivo)
                
                with open(caminho, 'wb') as f:
                    f.write(response.content)
                
                return True, len(response.content)
            
            return False, 0
            
        except Exception as e:
            return False, 0
    
    def buscar_oficios_processo(self, numero_processo, idx, total):
        """Processa um processo completo: busca código, acessa requisitórios e baixa PDFs"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            # ETAPA 1: Buscar código do processo
            print(f"   🔍 Buscando código...", end=" ", flush=True)
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"❌ Processo não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            print(f"✅ Código: {codigo}")
            
            # ETAPA 2: Extrair foro
            foro = self.extrair_foro(numero_processo)
            
            # ETAPA 3: Acessar página de requisitórios
            url_requisitorios = (
                f"https://esaj.tjsp.jus.br/cpopg/show.do?"
                f"processo.codigo={codigo}&"
                f"processo.foro={foro}&"
                f"processo.numero={numero_processo}&"
                f"consultaDeRequisitorios=true"
            )
            
            print(f"   🎯 Acessando requisitórios...", end=" ", flush=True)
            self.driver.get(url_requisitorios)
            time.sleep(2)
            print(f"✅")
            
            # ETAPA 4: Extrair links de ofícios
            print(f"   🔍 Localizando ofícios...", end=" ", flush=True)
            
            script_busca = """
            let links = [];
            document.querySelectorAll('a').forEach(a => {
                let texto = a.textContent.toLowerCase();
                let href = a.href;
                
                if ((texto.includes('ofício') || texto.includes('requisitório') || 
                     texto.includes('or') || texto.includes('depre')) 
                    && href && href.length > 0 && !href.includes('javascript')) {
                    links.push({
                        url: href,
                        texto: a.textContent.trim()
                    });
                }
            });
            return links;
            """
            
            oficios = self.driver.execute_script(script_busca)
            
            if not oficios or len(oficios) == 0:
                print(f"⚠️  Nenhum ofício encontrado")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(oficios)} ofício(s) encontrado(s)")
            
            # ETAPA 5: Baixar cada ofício
            baixados = 0
            
            for idx_of, oficio in enumerate(oficios, 1):
                nome_limpo = numero_processo.replace('-','').replace('.','')
                nome_arquivo = f"{nome_limpo}_oficio_{idx_of}.pdf"
                
                print(f"   📥 Baixando {idx_of}/{len(oficios)}...", end=" ", flush=True)
                
                sucesso, tamanho = self.baixar_pdf(oficio['url'], nome_arquivo)
                
                if sucesso:
                    kb = tamanho // 1024
                    print(f"✅ {kb} KB")
                    baixados += 1
                    self.total_pdfs += 1
                else:
                    print(f"❌ Falha")
            
            if baixados > 0:
                self.sucessos.append(numero_processo)
                return True
            else:
                self.falhas.append(numero_processo)
                return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            self.falhas.append(numero_processo)
            return False
    
    def carregar_processos_planilha(self):
        """Carrega números de processos da planilha Excel"""
        print(f"\n📊 Carregando planilha: {self.planilha}")
        
        # CORREÇÃO: Usar self.planilha do .env ao invés de caminho hardcoded
        caminho_completo = os.path.join(os.getcwd(), self.planilha)
        
        if not os.path.exists(caminho_completo):
            print(f"❌ Planilha não encontrada: {caminho_completo}")
            return []
        
        wb = openpyxl.load_workbook(caminho_completo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:  # Validar se é processo TJSP
                    processos.append(num)
        
        wb.close()
        
        print(f"✅ {len(processos)} processos carregados")
        return processos
    
    def gerar_relatorio_final(self, inicio):
        """Gera relatório completo da execução"""
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("🎉 EXECUÇÃO CONCLUÍDA!")
        print("="*70)
        
        total = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total processado: {total}")
        print(f"   ✅ Com ofício baixado: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício disponível: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas/Erros: {len(self.falhas)}")
        print(f"   📄 Total de PDFs baixados: {self.total_pdfs}")
        
        if total > 0:
            taxa_sucesso = (len(self.sucessos) / total) * 100
            print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        minutos = int(duracao.total_seconds() / 60)
        segundos = int(duracao.total_seconds() % 60)
        print(f"\n   ⏱️  Tempo total: {minutos}min {segundos}s")
        
        # Verificar PDFs baixados
        pdfs = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"\n📁 Pasta de destino: {os.path.abspath(self.pasta_oficios)}")
        print(f"📄 Total de arquivos PDF: {len(pdfs)}")
        
        # Salvar relatório em arquivo
        self.salvar_relatorio_txt(inicio, fim, total, duracao)
        
        print("="*70)
    
    def salvar_relatorio_txt(self, inicio, fim, total, duracao):
        """Salva relatório em arquivo de texto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_relatorio = f"relatorio_busca_{timestamp}.txt"
        
        with open(nome_relatorio, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("RELATÓRIO DE BUSCA DE OFÍCIOS REQUISITÓRIOS - TJSP\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Data/Hora Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Data/Hora Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Duração: {int(duracao.total_seconds()/60)}min {int(duracao.total_seconds()%60)}s\n\n")
            
            f.write(f"Total de processos: {total}\n")
            f.write(f"✅ Sucessos: {len(self.sucessos)}\n")
            f.write(f"⚠️  Sem ofício: {len(self.sem_oficio)}\n")
            f.write(f"❌ Falhas: {len(self.falhas)}\n")
            f.write(f"📄 PDFs baixados: {self.total_pdfs}\n\n")
            
            if self.sucessos:
                f.write("-"*70 + "\n")
                f.write("PROCESSOS COM OFÍCIOS BAIXADOS:\n")
                f.write("-"*70 + "\n")
                for p in self.sucessos:
                    f.write(f"  ✅ {p}\n")
                f.write("\n")
            
            if self.sem_oficio:
                f.write("-"*70 + "\n")
                f.write("PROCESSOS SEM OFÍCIOS DISPONÍVEIS:\n")
                f.write("-"*70 + "\n")
                for p in self.sem_oficio:
                    f.write(f"  ⚠️  {p}\n")
                f.write("\n")
            
            if self.falhas:
                f.write("-"*70 + "\n")
                f.write("PROCESSOS COM FALHA:\n")
                f.write("-"*70 + "\n")
                for p in self.falhas:
                    f.write(f"  ❌ {p}\n")
        
        print(f"\n📄 Relatório salvo: {nome_relatorio}")
    
    def executar(self):
        """Execução principal do sistema"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print("="*70)
        
        # Validar credenciais
        if not self.usuario or not self.senha:
            print("\n❌ ERRO: Credenciais não configuradas no arquivo .env")
            print("   Configure TJSP_USUARIO e TJSP_SENHA")
            return
        
        # Carregar processos
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            print("\n❌ Nenhum processo encontrado na planilha!")
            return
        
        # Confirmar execução
        print(f"\n📋 Total de processos a processar: {len(processos)}")
        print(f"📁 Destino dos PDFs: {os.path.abspath(self.pasta_oficios)}")
        
        confirma = input(f"\n>>> Iniciar busca de {len(processos)} processos? (s/n): ").lower()
        
        if confirma != 's':
            print("\n⚠️  Execução cancelada pelo usuário")
            return
        
        # Iniciar navegador
        self.iniciar_chrome()
        
        # Fazer login
        if not self.fazer_login():
            print("\n❌ Não foi possível fazer login. Encerrando.")
            self.fechar()
            return
        
        # Processar cada processo
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficios_processo(numero, idx, len(processos))
            
            # Relatório parcial a cada 20 processos
            if idx % 20 == 0:
                self.mostrar_progresso(idx, len(processos), inicio)
            
            # Intervalo entre processos
            time.sleep(self.intervalo)
        
        # Relatório final
        self.gerar_relatorio_final(inicio)
        
        # Manter navegador aberto
        input("\n\n>>> Pressione ENTER para fechar o navegador <<<\n")
    
    def mostrar_progresso(self, atual, total, inicio):
        """Mostra progresso parcial durante execução"""
        print(f"\n{'='*70}")
        print(f"📊 PROGRESSO: {atual}/{total} ({atual/total*100:.1f}%)")
        print(f"{'='*70}")
        print(f"   ✅ Sucessos: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        print(f"   📄 PDFs baixados: {self.total_pdfs}")
        
        decorrido = (datetime.now() - inicio).total_seconds()
        media = decorrido / atual
        restante = (total - atual) * media
        
        print(f"   ⏱️  Decorrido: {int(decorrido/60)}min")
        print(f"   ⏳ Estimativa restante: ~{int(restante/60)}min")
        print(f"{'='*70}\n")
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("\n✅ Navegador fechado")

if __name__ == "__main__":
    buscador = BuscadorRequisitoriosProfissional()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  EXECUÇÃO INTERROMPIDA PELO USUÁRIO")
        buscador.gerar_relatorio_final(datetime.now())
    
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ SISTEMA ENCERRADO\n")
