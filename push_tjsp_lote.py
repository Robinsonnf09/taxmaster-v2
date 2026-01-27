"""
PUSH TJSP - PROCESSAMENTO EM LOTE COMPLETO
Processa todos os processos do TJSP da planilha automaticamente
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import openpyxl
from datetime import datetime
import os
import json

class PushTJSPLote:
    
    def __init__(self):
        self.driver = None
        self.url_push = "https://esaj.tjsp.jus.br/push/index.do"
        self.sucessos = []
        self.falhas = []
        self.ja_cadastrados = []
        self.processados = []
        
        # Arquivo de checkpoint
        self.checkpoint_file = "checkpoint_push_tjsp.json"
        self.carregar_checkpoint()
    
    def carregar_checkpoint(self):
        """Carrega processos já processados para continuar de onde parou"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    self.processados = data.get('processados', [])
                    print(f"✅ Checkpoint carregado: {len(self.processados)} já processados")
            except:
                self.processados = []
    
    def salvar_checkpoint(self, numero):
        """Salva progresso para poder retomar"""
        self.processados.append(numero)
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({'processados': self.processados}, f)
        except:
            pass
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def login_manual(self):
        print(f"\n🔐 Acessando PUSH TJSP...")
        self.driver.get(self.url_push)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("👉 FAÇA LOGIN AGORA:")
        print("="*70)
        print("   1. Use login/senha (ou certificado se Web Signer instalado)")
        print("   2. Se pedir Web Signer, clique CANCELAR e use login/senha")
        print("   3. NAVEGUE até a tela de CADASTRO de processos")
        print("   4. Deve ver campo de número + botão Incluir")
        print("="*70)
        
        input("\n>>> ENTER quando estiver na tela de CADASTRO <<<\n")
        
        print("✅ Pronto para processar em lote!")
        return True
    
    def cadastrar_processo(self, numero, idx, total):
        """Cadastra um processo com tratamento de erros robusto"""
        try:
            print(f"\n{'='*70}")
            print(f"📝 [{idx}/{total}] {numero}")
            print(f"{'='*70}")
            
            # Verificar se já foi processado
            if numero in self.processados:
                print(f"   ⏭️  Já processado anteriormente (pulando)")
                return True
            
            wait = WebDriverWait(self.driver, 8)
            
            # CAMPO DE PROCESSO
            try:
                campo = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='text'][1]")
                ))
                
                if campo.is_displayed():
                    campo.clear()
                    time.sleep(0.2)
                    campo.send_keys(numero)
                    time.sleep(0.3)
                    print(f"   ✅ Digitado")
                else:
                    raise Exception("Campo não visível")
                
            except Exception as e:
                print(f"   ⚠️  Campo não encontrado: {str(e)[:50]}")
                print(f"   💡 Digite manualmente: {numero}")
                input(f"   >>> ENTER após digitar <<<\n")
            
            # BOTÃO INCLUIR
            try:
                botoes_xpath = [
                    "//button[contains(text(), 'Incluir')]",
                    "//input[@value='Incluir']",
                    "//button[@type='submit']",
                    "//input[@type='submit']"
                ]
                
                btn = None
                for xpath in botoes_xpath:
                    try:
                        btn = self.driver.find_element(By.XPATH, xpath)
                        if btn.is_displayed():
                            break
                    except:
                        continue
                
                if btn:
                    btn.click()
                    time.sleep(2)
                else:
                    print(f"   ⚠️  Botão não encontrado")
                    input(f"   >>> Clique em INCLUIR <<<\n")
                
            except Exception as e:
                print(f"   ⚠️  Erro ao clicar: {str(e)[:50]}")
                input(f"   >>> Clique manualmente <<<\n")
            
            # VERIFICAR RESULTADO
            time.sleep(1)
            page = self.driver.page_source.lower()
            
            resultado = None
            
            if any(x in page for x in ['sucesso', 'incluído', 'cadastrado', 'adicionado']):
                print(f"   ✅ CADASTRADO!")
                self.sucessos.append(numero)
                resultado = True
                
            elif any(x in page for x in ['já cadastrado', 'já existe', 'duplicado']):
                print(f"   ⚠️  Já cadastrado")
                self.ja_cadastrados.append(numero)
                resultado = True
                
            elif any(x in page for x in ['erro', 'inválido', 'não encontrado']):
                print(f"   ❌ Erro no cadastro")
                self.falhas.append(numero)
                resultado = False
                
            else:
                print(f"   ⚠️  Status desconhecido - verificando...")
                # Verificar se campo foi limpo (indica sucesso)
                try:
                    campo_apos = self.driver.find_element(By.XPATH, "//input[@type='text'][1]")
                    if campo_apos.get_attribute('value') == '':
                        print(f"   ✅ CADASTRADO (campo limpo)")
                        self.sucessos.append(numero)
                        resultado = True
                    else:
                        print(f"   ⚠️  Status ambíguo")
                        self.falhas.append(numero)
                        resultado = False
                except:
                    self.falhas.append(numero)
                    resultado = False
            
            # Salvar checkpoint
            self.salvar_checkpoint(numero)
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)[:100]}")
            self.falhas.append(numero)
            self.salvar_checkpoint(numero)
            return False
    
    def processar_planilha_completa(self, arquivo):
        """Processa TODOS os processos do TJSP da planilha"""
        print(f"\n📊 Carregando planilha: {arquivo}")
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado!")
            return
        
        # Carregar processos
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        
        processos_tjsp = []
        todos_processos = []
        
        print(f"\n🔍 Analisando planilha...")
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                num = str(row[0]).strip()
                todos_processos.append(num)
                
                # Filtrar TJSP (.8.26.)
                if '.8.26.' in num:
                    processos_tjsp.append(num)
        
        total_geral = len(todos_processos)
        total_tjsp = len(processos_tjsp)
        outros = total_geral - total_tjsp
        
        print(f"\n📋 ANÁLISE DA PLANILHA:")
        print(f"   Total de processos: {total_geral}")
        print(f"   TJSP (.8.26.): {total_tjsp}")
        print(f"   Outros tribunais: {outros}")
        
        if len(self.processados) > 0:
            restantes = [p for p in processos_tjsp if p not in self.processados]
            print(f"\n⏭️  Já processados: {len(self.processados)}")
            print(f"   Restantes: {len(restantes)}")
            processos_tjsp = restantes
        
        print(f"\n🎯 Vamos processar: {len(processos_tjsp)} processos")
        
        confirma = input("\n>>> Confirmar processamento em lote? (s/n): ").lower()
        
        if confirma != 's':
            print("❌ Cancelado pelo usuário")
            return
        
        # PROCESSAR EM LOTE
        print(f"\n{'='*70}")
        print("🚀 INICIANDO PROCESSAMENTO EM LOTE")
        print(f"{'='*70}\n")
        
        inicio = datetime.now()
        
        for idx, numero in enumerate(processos_tjsp, 1):
            self.cadastrar_processo(numero, idx, len(processos_tjsp))
            
            # Intervalo entre processos
            if idx < len(processos_tjsp):
                time.sleep(1.2)
            
            # Relatório parcial a cada 20
            if idx % 20 == 0:
                self.relatorio_parcial(idx, len(processos_tjsp), inicio)
        
        # RELATÓRIO FINAL
        fim = datetime.now()
        duracao = fim - inicio
        
        self.gerar_relatorio_final(duracao)
    
    def relatorio_parcial(self, atual, total, inicio):
        """Mostra progresso a cada 20 processos"""
        print(f"\n{'='*70}")
        print(f"📊 PROGRESSO: {atual}/{total} ({(atual/total*100):.1f}%)")
        print(f"{'='*70}")
        print(f"   ✅ Cadastrados: {len(self.sucessos)}")
        print(f"   ⚠️  Já existiam: {len(self.ja_cadastrados)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        
        decorrido = datetime.now() - inicio
        media_por_processo = decorrido.total_seconds() / atual
        restantes = total - atual
        tempo_estimado = restantes * media_por_processo
        
        print(f"   ⏱️  Tempo: {int(decorrido.total_seconds()/60)}min")
        print(f"   ⏳ Estimativa restante: {int(tempo_estimado/60)}min")
        print(f"{'='*70}\n")
    
    def gerar_relatorio_final(self, duracao):
        """Gera relatório completo final"""
        print("\n" + "="*70)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("="*70)
        
        total = len(self.sucessos) + len(self.ja_cadastrados) + len(self.falhas)
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total processado: {total}")
        print(f"   ✅ Cadastrados: {len(self.sucessos)}")
        print(f"   ⚠️  Já cadastrados: {len(self.ja_cadastrados)}")
        print(f"   ❌ Falhas: {len(self.falhas)}")
        
        if total > 0:
            taxa = ((len(self.sucessos) + len(self.ja_cadastrados)) / total) * 100
            print(f"\n   📊 Taxa de sucesso: {taxa:.1f}%")
        
        print(f"\n   ⏱️  Tempo total: {int(duracao.total_seconds()/60)} minutos")
        print(f"   ⚡ Média: {duracao.total_seconds()/total:.1f}s por processo")
        
        # Detalhes das falhas
        if self.falhas:
            print(f"\n❌ PROCESSOS COM FALHA ({len(self.falhas)}):")
            for p in self.falhas[:20]:
                print(f"   - {p}")
            if len(self.falhas) > 20:
                print(f"   ... e mais {len(self.falhas) - 20}")
        
        print("\n" + "="*70)
        
        # SALVAR RELATÓRIO DETALHADO
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"relatorio_push_tjsp_lote_{timestamp}.txt"
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write("="*70 + "\n")
            f.write("RELATÓRIO - CADASTRO EM LOTE PUSH TJSP\n")
            f.write("="*70 + "\n\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Duração: {int(duracao.total_seconds()/60)} minutos\n\n")
            
            f.write(f"Total processado: {total}\n")
            f.write(f"Cadastrados: {len(self.sucessos)}\n")
            f.write(f"Já cadastrados: {len(self.ja_cadastrados)}\n")
            f.write(f"Falhas: {len(self.falhas)}\n")
            
            if total > 0:
                taxa = ((len(self.sucessos) + len(self.ja_cadastrados)) / total) * 100
                f.write(f"Taxa de sucesso: {taxa:.1f}%\n\n")
            
            if self.sucessos:
                f.write("="*70 + "\n")
                f.write("CADASTRADOS COM SUCESSO:\n")
                f.write("="*70 + "\n")
                for p in self.sucessos:
                    f.write(f"{p}\n")
                f.write("\n")
            
            if self.ja_cadastrados:
                f.write("="*70 + "\n")
                f.write("JÁ CADASTRADOS:\n")
                f.write("="*70 + "\n")
                for p in self.ja_cadastrados:
                    f.write(f"{p}\n")
                f.write("\n")
            
            if self.falhas:
                f.write("="*70 + "\n")
                f.write("FALHAS:\n")
                f.write("="*70 + "\n")
                for p in self.falhas:
                    f.write(f"{p}\n")
        
        print(f"📄 Relatório salvo: {arquivo}")
        
        # Limpar checkpoint após conclusão
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print(f"✅ Checkpoint limpo")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("\n🔒 Navegador fechado")

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔔 PUSH TJSP - PROCESSAMENTO EM LOTE")
    print("="*70)
    print("\n🎯 Este script vai processar TODOS os processos do TJSP")
    print("📁 Planilha: processos_push_20260126_185045.xlsx")
    
    push = PushTJSPLote()
    
    try:
        input("\n⚠️  Certifique-se que o token A3 está conectado!\n\nENTER para começar...\n")
        
        push.iniciar()
        
        if push.login_manual():
            push.processar_planilha_completa("processos_push_20260126_185045.xlsx")
        
        input("\n\n>>> ENTER para fechar <<<\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processamento interrompido pelo usuário")
        print(f"✅ Progresso salvo! {len(push.processados)} processados")
        print(f"💡 Execute novamente para continuar de onde parou")
        push.gerar_relatorio_final(datetime.now() - datetime.now())
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        push.fechar()
    
    print("\n✅ CONCLUÍDO!")
