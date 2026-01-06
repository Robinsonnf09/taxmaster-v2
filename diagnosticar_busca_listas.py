"""
Script para corrigir automaticamente o erro em /buscar-listas-precatorios
"""

import sys
import os

def verificar_e_corrigir():
    """Verifica e corrige problemas comuns"""
    
    print("\n" + "="*70)
    print("DIAGNOSTICANDO ERRO EM /buscar-listas-precatorios")
    print("="*70)
    
    problemas = []
    
    # 1. Verificar se app.py existe
    print("\n[1/5] Verificando app.py...")
    if not os.path.exists("app.py"):
        print("   [ERRO] app.py não encontrado!")
        problemas.append("app.py não encontrado")
    else:
        print("   [OK] app.py encontrado")
        
        # Verificar se rota existe
        with open("app.py", "r", encoding="utf-8") as f:
            conteudo = f.read()
            
        if "buscar-listas-precatorios" in conteudo:
            print("   [OK] Rota buscar-listas-precatorios encontrada")
        else:
            print("   [ERRO] Rota buscar-listas-precatorios NÃO encontrada")
            problemas.append("Rota não adicionada ao app.py")
    
    # 2. Verificar templates
    print("\n[2/5] Verificando templates...")
    templates = [
        "templates/buscar_listas_precatorios.html",
        "templates/resultados_busca_listas.html"
    ]
    
    for template in templates:
        if os.path.exists(template):
            print(f"   [OK] {template} existe")
        else:
            print(f"   [ERRO] {template} NÃO encontrado")
            problemas.append(f"Template {template} faltando")
    
    # 3. Verificar imports
    print("\n[3/5] Verificando imports no app.py...")
    if os.path.exists("app.py"):
        with open("app.py", "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        imports_necessarios = [
            "from flask import",
            "render_template",
            "request",
            "redirect",
            "url_for",
            "flash"
        ]
        
        for imp in imports_necessarios:
            if imp in conteudo:
                print(f"   [OK] {imp} encontrado")
            else:
                print(f"   [AVISO] {imp} pode estar faltando")
    
    # 4. Verificar servidor
    print("\n[4/5] Verificando servidor...")
    print("   [INFO] Certifique-se de que o servidor está rodando")
    print("   [INFO] Execute: python app.py")
    
    # 5. Resumo
    print("\n[5/5] Resumo...")
    if problemas:
        print("\n   [PROBLEMAS ENCONTRADOS]")
        for i, problema in enumerate(problemas, 1):
            print(f"   {i}. {problema}")
    else:
        print("   [OK] Nenhum problema encontrado")
    
    print("\n" + "="*70)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("="*70)
    
    # Soluções
    print("\nSOLUÇÕES:")
    
    if "Rota não adicionada ao app.py" in problemas:
        print("\n1. ADICIONAR ROTAS:")
        print("   - Abra: rotas_busca_listas_CORRIGIDO.txt")
        print("   - Copie todo o conteúdo")
        print("   - Cole no app.py (antes do 'if __name__')")
        print("   - Salve o arquivo")
    
    if any("Template" in p for p in problemas):
        print("\n2. CRIAR TEMPLATES:")
        print("   - Execute o script que cria os templates")
        print("   - Ou copie os templates de backup")
    
    print("\n3. REINICIAR SERVIDOR:")
    print("   - Pare o servidor (Ctrl+C)")
    print("   - Inicie novamente: python app.py")
    print("   - Acesse: http://localhost:8080/buscar-listas-precatorios")
    
    return len(problemas) == 0

if __name__ == "__main__":
    sucesso = verificar_e_corrigir()
    
    if sucesso:
        print("\n✅ Sistema OK! Reinicie o servidor e teste.")
    else:
        print("\n⚠️ Problemas encontrados. Siga as soluções acima.")
