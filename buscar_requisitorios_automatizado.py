"""
BUSCAR REQUISITÓRIOS TJSP - VERSÃO ULTRA-AUTOMATIZADA
Mínima intervenção manual, máxima automação
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

class BuscadorAutomatizado:
    
    def __init__(self):
        self.driver = None
        self.session = None
        self.pasta_oficios = "oficios_requisitorios_tjsp"
        
        if not os.path.exists(self.pasta_oficios):
            os.makedirs(self.pasta_oficios)
        
        self.sucessos = []
        self.falhas = []
        self.sem_oficio = []
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome automatizado...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        prefs = {
            "download.default_directory": os.path.abspath(self.pasta_oficios),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Criar sessão requests com cookies do selenium
        self.session = requests.Session()
        
        print("✅ Chrome iniciado!")
    
    def fazer_login_unico(self):
        print(f"\n🔐 Fazendo login ÚNICO...")
        self.driver.get("https://esaj.tjsp.jus.br")
        time.sleep(3)
        
        print("\n" + "="*70)
        print("⚠️  FAÇA LOGIN AGORA (APENAS 1 VEZ):")
        print("="*70)
        input("\n>>> ENTER após login <<<\n")
        
        # Copiar cookies para requests
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'])
        
        print("✅ Login salvo! Não precisa mais fazer login!")
        return True
    
    def buscar_processo_automatico(self, numero_processo):
        """Busca processo e extrai código AUTOMATICAMENTE"""
        try:
            url_consulta = "https://esaj.tjsp.jus.br/cpopg/open.do"
            self.driver.get(url_consulta)
            time.sleep(1)
            
            # Buscar campo automaticamente
            wait = WebDriverWait(self.driver, 10)
            campo = wait.until(EC.presence_of_element_located(
                (By.ID, "nuProcessoAntigoFormatado")
            ))
            
            campo.clear()
            campo.send_keys(numero_processo)
            campo.send_keys(Keys.RETURN)
            
            time.sleep(2)
            
            # Extrair código da URL
            url_atual = self.driver.current_url
            
            if "processo.codigo=" in url_atual:
                codigo = url_atual.split("processo.codigo=")[1].split("&")[0]
                return codigo
            
            return None
            
        except Exception as e:
            return None
    
    def baixar_pdf_automatico(self, url_pdf, nome_arquivo):
        """Baixa PDF usando requests (mais confiável)"""
        try:
            # Atualizar cookies
            for cookie in self.driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # Baixar
            response = self.session.get(url_pdf, timeout=30)
            
            if response.status_code == 200:
                caminho = os.path.join(self.pasta_oficios, nome_arquivo)
                
                with open(caminho, 'wb') as f:
                    f.write(response.content)
                
                tamanho = len(response.content)
                return True, tamanho
            
            return False, 0
            
        except Exception as e:
            return False, 0
    
    def processar_processo_automatico(self, numero_processo, idx, total):
        """Processa processo COM MÍNIMA INTERVENÇÃO"""
        try:
            print(f"\n{'='*70}")
            print(f"⚡ [{idx}/{total}] {numero_processo}")
            print(f"{'='*70}")
            
            # 1. Buscar código AUTOMATICAMENTE
            print(f"   🔍 Buscando código...", end=" ", flush=True)
            
            codigo = self.buscar_processo_automatico(numero_processo)
            
            if not codigo:
                print(f"❌")
                print(f"   ⚠️  Processo não encontrado ou inacessível")
                self.falhas.append(numero_processo)
                return False
            
            print(f"✅ {codigo}")
            
            # 2. Acessar página de requisitórios
            foro = numero_processo.split(".")[-1]
            
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
            
            # 3. Procurar ofícios AUTOMATICAMENTE
            print(f"   🔍 Procurando ofícios...", end=" ", flush=True)
            
            # Script JavaScript para encontrar links
            script = """
            let links = [];
            document.querySelectorAll('a').forEach(a => {
                let texto = a.textContent.toLowerCase();
                let href = a.href;
                
                if ((texto.includes('ofício') || texto.includes('requisitório') || texto.includes('or')) 
                    && href && href.length > 0) {
                    links.push({
                        url: href,
                        texto: a.textContent.trim()
                    });
                }
            });
            return links;
            """
            
            oficios = self.driver.execute_script(script)
            
            if not oficios:
                print(f"⚠️  Sem ofício")
                self.sem_oficio.append(numero_processo)
                return False
            
            print(f"✅ {len(oficios)} encontrado(s)")
            
            # 4. Baixar TODOS os ofícios AUTOMATICAMENTE
            baixados = 0
            
            for idx_of, oficio in enumerate(oficios, 1):
                nome_arquivo = f"{numero_processo.replace('-','').replace('.','')}_oficio_{idx_of}.pdf"
                
                print(f"   📥 Baixando {idx_of}/{len(oficios)}...", end=" ", flush=True)
                
                sucesso, tamanho = self.baixar_pdf_automatico(
                    oficio['url'], 
                    nome_arquivo
                )
                
                if sucesso:
                    print(f"✅ {tamanho//1024}KB")
                    baixados += 1
                else:
                    print(f"❌")
            
            if baixados > 0:
                print(f"   🎉 {baixados} PDF(s) baixado(s)!")
                self.sucessos.append(numero_processo)
                return True
            else:
                self.falhas.append(numero_processo)
                return False
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:80]}")
            self.falhas.append(numero_processo)
            return False
    
    def processar_planilha_automatico(self, arquivo):
        print(f"\n📊 Carregando: {arquivo}")
        
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                if '.8.26.' in num:
                    processos.append(num)
        
        total = len(processos)
        print(f"✅ {total} processos")
        
        print("\n" + "="*70)
        print("⚡ MODO AUTOMATIZADO:")
        print("="*70)
        print("   - Busca automática")
        print("   - Extração de código automática")
        print("   - Download automático de PDFs")
        print("   - Processamento contínuo")
        print("="*70)
        
        confirma = input(f"\n>>> Processar {total} processos automaticamente? (s/n): ").lower()
        
        if confirma != 's':
            return
        
        inicio = datetime.now()
        
        # LOOP AUTOMÁTICO
        for idx, numero in enumerate(processos, 1):
            self.processar_processo_automatico(numero, idx, total)
            
            # Relatório a cada 20
            if idx % 20 == 0:
                print(f"\n{'='*70}")
                print(f"📊 PROGRESSO: {idx}/{total} ({idx/total*100:.1f}%)")
                print(f"{'='*70}")
                print(f"   ✅ Baixados: {len(self.sucessos)}")
                print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
                print(f"   ❌ Falhas: {len(self.falhas)}")
                
                decorrido = (datetime.now() - inicio).total_seconds()
                media = decorrido / idx
                restante = (total - idx) * media
                
                print(f"   ⏱️  Tempo: {int(decorrido/60)}min")
                print(f"   ⏳ Restante: {int(restante/60)}min")
                print(f"{'='*70}\n")
            
            time.sleep(1)
        
        # RELATÓRIO FINAL
        fim = datetime.now()
        duracao = fim - inicio
        
        print("\n" + "="*70)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("="*70)
        
        total_proc = len(self.sucessos) + len(self.sem_oficio) + len(self.falhas)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total: {total_proc}")
        print(f"   ✅ Com ofício: {len(self.sucessos)}")
        print(f"   ⚠️  Sem ofício: {len(self.sem_oficio)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        
        if total_proc > 0:
            taxa = (len(self.sucessos) / total_proc) * 100
            print(f"   📊 Taxa: {taxa:.1f}%")
        
        print(f"\n   ⏱️  Tempo: {int(duracao.total_seconds()/60)} minutos")
        print(f"   ⚡ Média: {duracao.total_seconds()/total_proc:.1f}s/processo")
        
        print(f"\n📁 Pasta: {os.path.abspath(self.pasta_oficios)}")
        
        # Contar PDFs baixados
        pdfs = [f for f in os.listdir(self.pasta_oficios) if f.endswith('.pdf')]
        print(f"📄 {len(pdfs)} PDF(s) baixado(s)")
        
        if self.sem_oficio:
            print(f"\n⚠️  SEM OFÍCIO ({len(self.sem_oficio)}):")
            for p in self.sem_oficio[:20]:
                print(f"   - {p}")
        
        if self.falhas:
            print(f"\n❌ FALHAS ({len(self.falhas)}):")
            for p in self.falhas[:20]:
                print(f"   - {p}")
        
        print("="*70)
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio = f"relatorio_requisitorios_automatico_{timestamp}.txt"
        
        with open(relatorio, "w", encoding="utf-8") as f:
            f.write("RELATÓRIO - BUSCA AUTOMATIZADA DE REQUISITÓRIOS\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total: {total_proc}\n")
            f.write(f"Com ofício: {len(self.sucessos)}\n")
            f.write(f"Sem ofício: {len(self.sem_oficio)}\n")
            f.write(f"Falhas: {len(self.falhas)}\n\n")
            
            if self.sucessos:
                f.write("COM OFÍCIO:\n")
                for p in self.sucessos:
                    f.write(f"  {p}\n")
                f.write("\n")
            
            if self.sem_oficio:
                f.write("SEM OFÍCIO:\n")
                for p in self.sem_oficio:
                    f.write(f"  {p}\n")
                f.write("\n")
            
            if self.falhas:
                f.write("FALHAS:\n")
                for p in self.falhas:
                    f.write(f"  {p}\n")
        
        print(f"\n📄 Relatório: {relatorio}")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("⚡ BUSCAR REQUISITÓRIOS - ULTRA-AUTOMATIZADO")
    print("="*70)
    
    buscador = BuscadorAutomatizado()
    
    try:
        input("\nENTER para começar...\n")
        
        buscador.iniciar()
        
        if buscador.fazer_login_unico():
            buscador.processar_planilha_automatico("processos_push_20260126_185045.xlsx")
        
        input("\n\nENTER para fechar...\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido")
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        buscador.fechar()
    
    print("\n✅ FIM!")
