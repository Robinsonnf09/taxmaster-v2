import ast
import os
import subprocess
import sys
import shutil

class CalculadoraFixer:
    def __init__(self):
        self.app_path = "app.py"
        self.backup_path = "app.py.backup"
        self.issues = []
        self.fixed = False
        
    def run(self):
        print("\n" + "="*70)
        print("FERRAMENTA AVANCADA DE CORRECAO - TAX MASTER")
        print("="*70)
        
        # 1. Ler app.py
        print("\n[1/8] Lendo app.py...")
        with open(self.app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print("   OK - {} linhas lidas".format(len(lines)))
        
        # 2. Procurar rota
        print("\n[2/8] Procurando rota /calculadora...")
        func_start = -1
        for i, line in enumerate(lines):
            if "@app.route('/calculadora')" in line:
                func_start = i
                print("   OK - Rota encontrada na linha {}".format(i+1))
                break
        
        if func_start == -1:
            print("   ERRO - Rota nao encontrada!")
            return False
        
        # 3. Extrair funcao completa
        print("\n[3/8] Extraindo funcao...")
        func_end = func_start
        for i in range(func_start + 1, len(lines)):
            if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                func_end = i - 1
                break
            if i == len(lines) - 1:
                func_end = i
        
        print("   Funcao atual (linhas {} a {}):".format(func_start+1, func_end+1))
        for i in range(func_start, min(func_end+1, func_start+10)):
            print("   {}".format(lines[i].rstrip()))
        
        # 4. Verificar try-except
        print("\n[4/8] Verificando try-except...")
        func_text = ''.join(lines[func_start:func_end+1])
        has_try = 'try:' in func_text
        has_except = 'except' in func_text
        
        print("   Bloco try: {}".format("OK" if has_try else "NAO ENCONTRADO"))
        print("   Bloco except: {}".format("OK" if has_except else "NAO ENCONTRADO"))
        
        if has_try and has_except:
            print("\n   Codigo ja esta correto! Nenhuma acao necessaria.")
            return True
        
        if not has_try or not has_except:
            self.issues.append("try-except incompleto")
        
        # 5. Criar backup
        print("\n[5/8] Criando backup...")
        shutil.copy2(self.app_path, self.backup_path)
        print("   OK - Backup: {}".format(self.backup_path))
        
        # 6. Aplicar correcao
        print("\n[6/8] Aplicando correcao...")
        
        new_function = '''@app.route('/calculadora')
def calculadora_page():
    \"\"\"Pagina da calculadora de atualizacao de precatorios\"\"\"
    try:
        with open('calculadora.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Erro: calculadora.html nao encontrado", 404
    except Exception as e:
        print(f"Erro ao carregar calculadora: {e}")
        return f"Erro ao carregar calculadora: {str(e)}", 500

'''
        
        # Substituir
        new_lines = lines[:func_start] + [new_function] + lines[func_end+1:]
        
        with open(self.app_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("   OK - Correcao aplicada!")
        self.fixed = True
        
        # 7. Testar sintaxe
        print("\n[7/8] Testando sintaxe...")
        result = subprocess.run([sys.executable, '-m', 'py_compile', self.app_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   OK - Sintaxe valida!")
        else:
            print("   ERRO - Sintaxe invalida!")
            print(result.stderr)
            print("\n   Restaurando backup...")
            shutil.copy2(self.backup_path, self.app_path)
            return False
        
        # 8. Git
        print("\n[8/8] Git commit e push...")
        try:
            subprocess.run(['git', 'add', 'app.py'], check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Fix: Corrigir rota /calculadora com try-except completo'], 
                         check=True, capture_output=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
            print("   OK - Alteracoes enviadas!")
        except subprocess.CalledProcessError as e:
            print("   AVISO - Erro no Git: {}".format(e))
        
        # Resumo
        print("\n" + "="*70)
        print("MODULO CALCULADORA CORRIGIDO COM SUCESSO!")
        print("="*70)
        
        if self.issues:
            print("\nProblemas corrigidos:")
            for issue in self.issues:
                print("  - {}".format(issue))
        
        print("\nPROXIMOS PASSOS:")
        print("  1. Pare o Flask (Ctrl+C)")
        print("  2. Reinicie: python app.py")
        print("  3. Acesse: http://localhost:8080/calculadora")
        print("  4. Railway vai redeployar automaticamente!\n")
        
        return True

if __name__ == "__main__":
    fixer = CalculadoraFixer()
    success = fixer.run()
    sys.exit(0 if success else 1)
