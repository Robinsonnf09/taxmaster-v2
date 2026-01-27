"""
PUSH TJSP - DESCOBRIR URL CORRETA
Você navega manualmente, script captura URL e campos
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import openpyxl

class PushTJSPDescobrir:
    
    def __init__(self):
        self.driver = None
        self.url_base = "https://esaj.tjsp.jus.br/push/index.do"
        self.url_formulario = None
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome iniciado!")
    
    def navegacao_manual(self):
        print(f"\n🔐 Acessando sistema...")
        self.driver.get(self.url_base)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("👉 NAVEGAÇÃO MANUAL - SIGA OS PASSOS:")
        print("="*70)
        print("   1. FAÇA LOGIN no sistema")
        print("   2. NAVEGUE até a área de CADASTRO de processos")
        print("   3. Você deve estar vendo:")
        print("      - Campo para digitar número do processo")
        print("      - Botão 'Incluir' ou 'Cadastrar'")
        print("   4. NÃO digite nada ainda!")
        print("   5. Volte aqui e pressione ENTER")
        print("="*70)
        
        input("\n>>> ENTER quando estiver no FORMULÁRIO DE CADASTRO &lt;&lt;&lt;\n")
        
        # Capturar URL correta
        self.url_formulario = self.driver.current_url
        print(f"\n✅ URL capturada: {self.url_formulario}")
        
        # Analisar campos
        self.analisar_formulario()
        
        return True
    
    def analisar_formulario(self):
        print("\n" + "="*70)
        print("🔍 ANALISANDO FORMULÁRIO...")
        print("="*70)
        
        # Tirar screenshot
        screenshot = "tjsp_formulario_cadastro.png"
        self.driver.save_screenshot(screenshot)
        print(f"📸 Screenshot: {screenshot}")
        
        # Salvar HTML
        with open("tjsp_formulario_html.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"📄 HTML: tjsp_formulario_html.html")
        
        # Listar inputs visíveis
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        
        print(f"\n📝 CAMPOS DE INPUT ({len(inputs)} total):")
        campos_texto = []
        
        for idx, inp in enumerate(inputs, 1):
            if inp.is_displayed():
                tipo = inp.get_attribute("type")
                nome = inp.get_attribute("name")
                id_campo = inp.get_attribute("id")
                placeholder = inp.get_attribute("placeholder")
                classe = inp.get_attribute("class")
                
                if tipo == "text":
                    campos_texto.append({
                        "name": nome,
                        "id": id_campo,
                        "placeholder": placeholder
                    })
                
                print(f"\n   Campo {idx}:")
                print(f"      Tipo: {tipo}")
                print(f"      Name: {nome}")
                print(f"      ID: {id_campo}")
                print(f"      Placeholder: {placeholder}")
                print(f"      Class: {classe}")
        
        # Listar botões
        botoes = self.driver.find_elements(By.TAG_NAME, "button")
        inputs_submit = self.driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button']")
        
        print(f"\n🔘 BOTÕES ({len(botoes) + len(inputs_submit)} total):")
        
        for idx, btn in enumerate(botoes, 1):
            if btn.is_displayed():
                texto = btn.text
                nome = btn.get_attribute("name")
                id_btn = btn.get_attribute("id")
                
                print(f"\n   Botão {idx}:")
                print(f"      Texto: '{texto}'")
                print(f"      Name: {nome}")
                print(f"      ID: {id_btn}")
        
        for idx, sub in enumerate(inputs_submit, 1):
            if sub.is_displayed():
                value = sub.get_attribute("value")
                nome = sub.get_attribute("name")
                id_sub = sub.get_attribute("id")
                
                print(f"\n   Submit {idx}:")
                print(f"      Value: '{value}'")
                print(f"      Name: {nome}")
                print(f"      ID: {id_sub}")
        
        print("\n" + "="*70)
        print("✅ ANÁLISE COMPLETA!")
        print("="*70)
        
        # Sugerir seletores
        if campos_texto:
            print("\n💡 SELETORES SUGERIDOS PARA CAMPO DE PROCESSO:")
            for c in campos_texto[:3]:
                if c["id"]:
                    print(f"   - By.ID: '{c['id']}'")
                if c["name"]:
                    print(f"   - By.NAME: '{c['name']}'")
        
        return True
    
    def cadastrar_processo(self, numero):
        try:
            print(f"\n📝 Testando cadastro: {numero}")
            
            # Tentar múltiplos seletores
            campo = None
            
            seletores = [
                (By.ID, "numeroProcesso"),
                (By.NAME, "numeroProcesso"),
                (By.ID, "processo"),
                (By.NAME, "processo"),
                (By.XPATH, "//input[@type='text'][1]")
            ]
            
            for metodo, valor in seletores:
                try:
                    campo = self.driver.find_element(metodo, valor)
                    if campo.is_displayed():
                        print(f"   ✅ Campo encontrado: {metodo} = '{valor}'")
                        break
                except:
                    continue
            
            if not campo:
                print(f"   ⚠️  Campo não encontrado automaticamente")
                print(f"   💡 Digite manualmente: {numero}")
                input(f"   >>> ENTER após digitar &lt;&lt;&lt;\n")
                return None
            
            # Preencher
            campo.clear()
            campo.send_keys(numero)
            print(f"   ✅ Número digitado")
            time.sleep(0.5)
            
            # Tentar clicar no botão
            btn = None
            
            botoes_seletores = [
                (By.XPATH, "//button[contains(text(), 'Incluir')]"),
                (By.XPATH, "//input[@value='Incluir']"),
                (By.XPATH, "//button[contains(text(), 'Cadastrar')]"),
                (By.XPATH, "//input[@type='submit']")
            ]
            
            for metodo, valor in botoes_seletores:
                try:
                    btn = self.driver.find_element(metodo, valor)
                    if btn.is_displayed():
                        print(f"   ✅ Botão encontrado")
                        break
                except:
                    continue
            
            if not btn:
                print(f"   ⚠️  Botão não encontrado")
                input(f"   >>> Clique em INCLUIR manualmente &lt;&lt;&lt;\n")
            else:
                btn.click()
                print(f"   ⏳ Aguardando...")
                time.sleep(3)
            
            # Verificar resultado
            page = self.driver.page_source.lower()
            
            if 'sucesso' in page or 'incluído' in page:
                print(f"   ✅ CADASTRADO!")
                return True
            elif 'já cadastrado' in page or 'já existe' in page:
                print(f"   ⚠️  Já estava cadastrado")
                return True
            else:
                opcao = input(f"   >>> Cadastrou com sucesso? (s/n): ").lower()
                return opcao == 's'
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:100]}")
            return False
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔍 PUSH TJSP - DESCOBRIR URL E CAMPOS")
    print("="*70)
    
    push = PushTJSPDescobrir()
    
    try:
        input("\nENTER para começar...\n")
        
        push.iniciar()
        
        if push.navegacao_manual():
            
            print("\n💡 MODO:")
            print("   1. Teste com 1 processo")
            print("   2. Apenas analisar (não cadastrar)")
            
            modo = input("\nDigite: ").strip()
            
            if modo == "1":
                num = input("\nNúmero do processo: ").strip()
                push.cadastrar_processo(num)
            
            print("\n📁 ARQUIVOS GERADOS:")
            print(f"   📸 tjsp_formulario_cadastro.png")
            print(f"   📄 tjsp_formulario_html.html")
            print(f"\n🔗 URL do formulário: {push.url_formulario}")
        
        input("\n\nENTER para fechar...\n")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    
    finally:
        push.fechar()
    
    print("\n✅ FIM!")
