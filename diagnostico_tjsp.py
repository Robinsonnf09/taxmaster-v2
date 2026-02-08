"""
DIAGNÓSTICO - Descobrir por que campo não é encontrado
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class DiagnosticoTJSP:
    
    def __init__(self):
        self.driver = None
    
    def iniciar(self):
        print("\n🌐 Iniciando Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome iniciado!")
    
    def fazer_login(self):
        print(f"\n🔐 Fazendo login...")
        self.driver.get("https://esaj.tjsp.jus.br")
        time.sleep(3)
        
        print("\n" + "="*70)
        print("FAÇA LOGIN:")
        print("="*70)
        input("\n>>> ENTER após login <<<\n")
        
        return True
    
    def diagnosticar_consulta(self):
        print(f"\n🔍 Acessando consulta processual...")
        
        url_consulta = "https://esaj.tjsp.jus.br/cpopg/open.do"
        self.driver.get(url_consulta)
        time.sleep(3)
        
        print("\n" + "="*70)
        print("DIAGNÓSTICO DA PÁGINA:")
        print("="*70)
        
        # 1. Tirar screenshot
        screenshot = "diagnostico_consulta_tjsp.png"
        self.driver.save_screenshot(screenshot)
        print(f"\n📸 Screenshot: {screenshot}")
        
        # 2. Salvar HTML
        with open("diagnostico_consulta_tjsp.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"📄 HTML: diagnostico_consulta_tjsp.html")
        
        # 3. Verificar título
        print(f"\n📋 Título da página: {self.driver.title}")
        
        # 4. Verificar URL
        print(f"🔗 URL atual: {self.driver.current_url}")
        
        # 5. Procurar TODOS os inputs
        print(f"\n🔍 PROCURANDO CAMPOS DE INPUT...")
        
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        
        print(f"\n📝 Total de inputs encontrados: {len(inputs)}")
        
        if len(inputs) > 0:
            print(f"\n📋 LISTA DE INPUTS VISÍVEIS:")
            
            for idx, inp in enumerate(inputs, 1):
                try:
                    if inp.is_displayed():
                        tipo = inp.get_attribute("type")
                        nome = inp.get_attribute("name")
                        id_campo = inp.get_attribute("id")
                        placeholder = inp.get_attribute("placeholder")
                        classe = inp.get_attribute("class")
                        
                        print(f"\n   Input {idx}:")
                        print(f"      Tipo: {tipo}")
                        print(f"      Name: {nome}")
                        print(f"      ID: {id_campo}")
                        print(f"      Placeholder: {placeholder}")
                        print(f"      Class: {classe[:50] if classe else ''}")
                except:
                    pass
        
        # 6. Verificar se há mensagem de erro
        page = self.driver.page_source.lower()
        
        if 'erro' in page:
            print(f"\n⚠️  Palavra 'erro' encontrada na página")
        
        if 'login' in page or 'entrar' in page:
            print(f"\n⚠️  Parece que NÃO está logado (palavras 'login'/'entrar' encontradas)")
        
        if 'certificado' in page:
            print(f"\n⚠️  Palavra 'certificado' encontrada")
        
        # 7. Procurar campo específico
        print(f"\n🔍 TENTANDO LOCALIZAR CAMPO DE PROCESSO...")
        
        seletores = [
            ("ID", "nuProcessoAntigoFormatado"),
            ("NAME", "nuProcessoAntigoFormatado"),
            ("ID", "numeroProcesso"),
            ("NAME", "numeroProcesso"),
            ("ID", "processo"),
            ("NAME", "processo"),
        ]
        
        for metodo, valor in seletores:
            try:
                if metodo == "ID":
                    campo = self.driver.find_element(By.ID, valor)
                else:
                    campo = self.driver.find_element(By.NAME, valor)
                
                if campo.is_displayed():
                    print(f"   ✅ ENCONTRADO! {metodo}='{valor}'")
                else:
                    print(f"   ⚠️  Existe mas não está visível: {metodo}='{valor}'")
            except:
                print(f"   ❌ Não encontrado: {metodo}='{valor}'")
        
        print("\n" + "="*70)
        print("✅ DIAGNÓSTICO COMPLETO!")
        print("="*70)
        
        print(f"\n📁 ARQUIVOS GERADOS:")
        print(f"   📸 diagnostico_consulta_tjsp.png")
        print(f"   📄 diagnostico_consulta_tjsp.html")
        
        print(f"\n💡 PRÓXIMOS PASSOS:")
        print(f"   1. Abra a imagem PNG")
        print(f"   2. Veja o que aparece na tela")
        print(f"   3. Me envie a imagem OU descreva o que vê")
        
        input(f"\n>>> ENTER para fechar <<<\n")
    
    def fechar(self):
        if self.driver:
            self.driver.quit()

# MAIN
if __name__ == "__main__":
    print("="*70)
    print("🔍 DIAGNÓSTICO - CONSULTA TJSP")
    print("="*70)
    
    diag = DiagnosticoTJSP()
    
    try:
        input("\nENTER para começar...\n")
        
        diag.iniciar()
        
        if diag.fazer_login():
            diag.diagnosticar_consulta()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        diag.fechar()
    
    print("\n✅ FIM!")
