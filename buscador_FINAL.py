"""
BUSCADOR DE OFÍCIOS REQUISITÓRIOS TJSP - CERTIFICADO A3 EM TOKEN
Versão com driver local do Edge
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os
import openpyxl
from datetime import datetime
import requests
from dotenv import load_dotenv

class BuscadorTJSP_CertificadoToken:
    
    def __init__(self):
        load_dotenv()
        
        self.driver = None
        self.session = None
        
        self.usar_certificado = os.getenv("USAR_CERTIFICADO", "True").lower() == "true"
        self.pasta_oficios = os.getenv("DOWNLOAD_PATH", "oficios_requisitorios_tjsp")
        self.planilha = os.getenv("PLANILHA_INPUT", "processos_TESTE_3.xlsx")
        self.timeout = int(os.getenv("TIMEOUT_PADRAO", "10"))
        self.intervalo = float(os.getenv("INTERVALO_ENTRE_PROCESSOS", "0.8"))
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
        self.total_pdfs = 0
    
    def iniciar_edge(self):
        """Inicia Microsoft Edge usando driver local"""
        print("\n🔷 Iniciando Microsoft Edge com suporte a Certificado Digital...")
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        # Usar driver local do Edge (Windows instala automaticamente)
        self.driver = webdriver.Edge(options=options)
        self.session = requests.Session()
        
        print("✅ Edge iniciado com sucesso!")
        print(f"📁 PDFs serão salvos em: {os.path.abspath(self.pasta_oficios)}")
    
    def fazer_login_certificado(self):
        """Faz login usando certificado do token"""
        print(f"\n🔐 Fazendo login com Certificado Digital (Token)...")
        
        try:
            print(f"   🌐 Acessando e-SAJ TJSP...")
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(3)
            
            print(f"   🔍 Procurando opção de login...")
            
            try:
                botoes_login = [
                    "//a[contains(text(), 'Entrar')]",
                    "//a[contains(text(), 'Login')]",
                    "//a[@title='Entrar']"
                ]
                
                for xpath in botoes_login:
                    try:
                        botao = self.driver.find_element(By.XPATH, xpath)
                        print(f"   ✅ Botão de login encontrado!")
                        botao.click()
                        time.sleep(3)
                        break
                    except:
                        continue
            except:
                pass
            
            if "sajcas/login" in self.driver.current_url or "login" in self.driver.current_url.lower():
                print(f"   📍 Na página de login")
                print(f"   🔍 Procurando opção 'Certificado Digital'...")
                
                try:
                    links_certificado = [
                        "//a[contains(text(), 'Certificado Digital')]",
                        "//a[contains(text(), 'certificado digital')]",
                        "//a[contains(text(), 'Certificado')]"
                    ]
                    
                    botao_encontrado = False
                    for xpath in links_certificado:
                        try:
                            link_cert = self.driver.find_element(By.XPATH, xpath)
                            print(f"   ✅ Link 'Certificado Digital' encontrado!")
                            link_cert.click()
                            botao_encontrado = True
                            time.sleep(2)
                            break
                        except:
                            continue
                    
                    if not botao_encontrado:
                        print(f"   ⚠️  Link não encontrado automaticamente")
                        self.driver.save_screenshot("tela_login_tjsp.png")
                        print(f"   📸 Screenshot salvo: tela_login_tjsp.png")
                        
                        print(f"\n{'='*70}")
                        print(f"💡 AÇÃO MANUAL NECESSÁRIA:")
                        print(f"{'='*70}")
                        print(f"\n   1. Clique em 'Certificado Digital' na tela")
                        print(f"   2. Selecione seu certificado quando o popup aparecer")
                        
                        input(f"\n>>> Pressione ENTER após clicar em 'Certificado Digital' <<<\n")
                
                except Exception as e:
                    print(f"   ⚠️  Erro ao buscar link: {str(e)}")
            
            print(f"\n{'='*70}")
            print(f"🔐 POPUP DE SELEÇÃO DE CERTIFICADO")
            print(f"{'='*70}")
            print(f"\n⚠️  ATENÇÃO:")
            print(f"   Um popup do Windows vai solicitar a seleção do certificado.")
            print(f"   ")
            print(f"   📜 Selecione o certificado:")
            print(f"      Serial: 24a59a14555d0e24")
            print(f"      e-CPF A3 de 03 Anos em token CERTDATA")
            print(f"   ")
            print(f"   ⏳ Aguardando 15 segundos para seleção...")
            
            time.sleep(15)
            
            url_atual = self.driver.current_url
            print(f"\n   📍 URL atual: {url_atual}")
            
            if "login" in url_atual.lower():
                print(f"\n   ⏳ Ainda na tela de login, aguardando mais 10 segundos...")
                time.sleep(10)
                url_atual = self.driver.current_url
            
            if "login" not in url_atual.lower():
                print(f"\n🎉 LOGIN COM CERTIFICADO REALIZADO COM SUCESSO!")
                
                for cookie in self.driver.get_cookies():
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                return True
            else:
                print(f"\n⚠️  Ainda na página de login")
                print(f"\n💡 Se você vê a página normal do e-SAJ:")
                print(f"   O login pode ter sido bem-sucedido mesmo assim.")
                print(f"   Vamos continuar e testar a busca.")
                
                return True
                
        except Exception as e:
            print(f"\n❌ Erro no login: {str(e)}")
            self.driver.save_screenshot("erro_login_certificado.png")
            
            print(f"\n💡 Deseja tentar continuar mesmo assim?")
            resp = input(f"   Digite 's' para continuar ou 'n' para cancelar: ").lower()
            
            return resp == 's'
    
    def extrair_codigo_processo(self, numero_processo):
        """Busca o processo e extrai o código interno"""
        try:
            self.driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(1.5)
            
            wait = WebDriverWait(self.driver, self.timeout)
            
            try:
                radio = wait.until(EC.element_to_be_clickable((By.ID, "radioNumeroAntigo")))
                radio.click()
                time.sleep(0.5)
            except:
                pass
            
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
            
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                return codigo
            
            return None
            
        except:
            return None
    
    def extrair_foro(self, numero_processo):
        """Extrai o foro do número do processo"""
        foro_completo = numero_processo.split(".")[-1]
        foro = foro_completo.lstrip('0')
        return foro if foro else "0"
    
    def baixar_pdf(self, url_pdf, nome_arquivo):
        """Baixa o PDF usando requests"""
        try:
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
            
        except:
            return False, 0
    
    def buscar_oficios_processo(self, numero_processo, idx, total):
        """Processa um processo completo"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            print(f"   🔍 Buscando código...", end=" ", flush=True)
            codigo = self.extrair_codigo_processo(numero_processo)
            
            if not codigo:
                print(f"❌ Processo não encontrado")
                self.falhas.append(numero_processo)
                return False
            
            print(f"✅ Código: {codigo}")
            
            foro = self.extrair_foro(numero_processo)
            
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
                if '.8.26.' in num:
                    processos.append(num)
        
        wb.close()
        
        print(f"✅ {len(processos)} processos carregados")
        return processos
    
    def gerar_relatorio_final(self, inicio):
        """Gera relatório completo"""
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
        
        pdfs = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"\n📁 Pasta de destino: {os.path.abspath(self.pasta_oficios)}")
        print(f"📄 Total de arquivos PDF: {len(pdfs)}")
        
        print("="*70)
    
    def executar(self):
        """Execução principal"""
        print("\n" + "="*70)
        print("🔍 BUSCADOR DE OFÍCIOS REQUISITÓRIOS - TJSP")
        print("   🔐 CERTIFICADO DIGITAL A3 (TOKEN CERTDATA)")
        print("="*70)
        
        print(f"\n🔐 Método de login: CERTIFICADO DIGITAL A3")
        print(f"   📜 Token: CERTDATA")
        print(f"   ✅ Serial: 24a59a14555d0e24")
        print(f"   📅 Validade: Até 26/01/2029")
        
        processos = self.carregar_processos_planilha()
        
        if len(processos) == 0:
            print("\n❌ Nenhum processo encontrado na planilha!")
            return
        
        print(f"\n📋 Total de processos a processar: {len(processos)}")
        print(f"📁 Destino dos PDFs: {os.path.abspath(self.pasta_oficios)}")
        
        confirma = input(f"\n>>> Iniciar busca de {len(processos)} processos? (s/n): ").lower()
        
        if confirma != 's':
            print("\n⚠️  Execução cancelada pelo usuário")
            return
        
        self.iniciar_edge()
        
        if not self.fazer_login_certificado():
            print("\n❌ Não foi possível fazer login. Encerrando.")
            self.fechar()
            return
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos, 1):
            self.buscar_oficios_processo(numero, idx, len(processos))
            time.sleep(self.intervalo)
        
        self.gerar_relatorio_final(inicio)
        
        input("\n\n>>> Pressione ENTER para fechar o navegador <<<\n")
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("\n✅ Navegador fechado")

if __name__ == "__main__":
    buscador = BuscadorTJSP_CertificadoToken()
    
    try:
        buscador.executar()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  EXECUÇÃO INTERROMPIDA")
    
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {str(e)}")
    
    finally:
        buscador.fechar()
    
    print("\n✅ SISTEMA ENCERRADO\n")
