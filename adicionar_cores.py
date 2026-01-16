"""
Script Automático - Adicionar Cores ao Dashboard
"""
import re
import os

print("="*70)
print("  🎨 ADICIONAR CORES AO RANKING - AUTOMÁTICO")
print("="*70 + "\n")

# Função colorida completa
nova_funcao = '''def exibir_dashboard_simples(scores):
    """Dashboard simplificado com CORES"""
    janela = tk.Toplevel(root)
    janela.title("🏆 Ranking ULTIMATE")
    janela.geometry("800x600")
    janela.configure(bg="#1a1a2e")
    
    tk.Label(janela, text="🏆 RANKING DE DEZENAS", 
             font=("Arial", 14, "bold"), 
             bg="#1a1a2e", fg="#FFD700").pack(pady=10)
    
    text = scrolledtext.ScrolledText(janela, 
                                     font=("Courier", 10), 
                                     bg="#0f0f1e", 
                                     fg="#FFFFFF",
                                     insertbackground="#FFD700")
    text.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Configurar tags de cores
    text.tag_config("header", foreground="#FFD700", font=("Courier", 10, "bold"))
    text.tag_config("ultra", foreground="#FF4444", font=("Courier", 10, "bold"))
    text.tag_config("quente", foreground="#FF9500", font=("Courier", 10, "bold"))
    text.tag_config("neutro", foreground="#FFC107", font=("Courier", 10))
    text.tag_config("frio", foreground="#03A9F4", font=("Courier", 10))
    
    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Cabeçalho com cor
    text.insert("end", f"{'#':<4} {'DEZ':<6} {'SCORE':<10} {'VISUAL':<30} {'STATUS'}\\n", "header")
    text.insert("end", "="*70 + "\\n\\n", "header")
    
    for idx, (dez, score) in enumerate(ranking, 1):
        barra = "█" * int((score / 100) * 25)
        
        # Determinar status e cor
        if score >= 80:
            status = "🔥 ULTRA"
            tag = "ultra"
        elif score >= 70:
            status = "🌡️ QUENTE"
            tag = "quente"
        elif score >= 50:
            status = "➡️ NEUTRO"
            tag = "neutro"
        else:
            status = "❄️ FRIO"
            tag = "frio"
        
        # Inserir linha com cor
        linha = f"{idx:<4} {dez:02d}     {score:<10.1f} {barra:<30} {status}\\n"
        text.insert("end", linha, tag)
    
    text.config(state="disabled")
    
    # Botões com cores
    frame_btn = tk.Frame(janela, bg="#1a1a2e")
    frame_btn.pack(pady=10)
    
    tk.Button(frame_btn, text="🎯 Usar Top 10", 
              command=lambda: usar_top([d for d, s in ranking[:10]]), 
              bg="#4CAF50", fg="white", 
              font=("Arial", 10, "bold"), 
              padx=15, pady=8).pack(side="left", padx=5)
    
    tk.Button(frame_btn, text="❌ Fechar", 
              command=janela.destroy, 
              bg="#FF5722", fg="white", 
              font=("Arial", 10, "bold"),
              padx=15, pady=8).pack(side="left", padx=5)'''

arquivo = "lotofacil_ultimate_final.py"

if not os.path.exists(arquivo):
    print(f"❌ Arquivo não encontrado: {arquivo}")
    input("Pressione ENTER para sair...")
    exit(1)

print("📖 Lendo arquivo...")

# Ler arquivo
with open(arquivo, 'r', encoding='utf-8') as f:
    codigo = f.read()

print("✅ Arquivo lido com sucesso")

# Encontrar a função antiga usando regex
padrao = r'def exibir_dashboard_simples\(scores\):.*?(?=\ndef [a-z_]+\(|$)'

match = re.search(padrao, codigo, re.DOTALL)

if not match:
    print("❌ Função exibir_dashboard_simples não encontrada")
    input("Pressione ENTER para sair...")
    exit(1)

print("🔍 Função encontrada!")
print(f"   Posição: caractere {match.start()} até {match.end()}")
print(f"   Tamanho: {match.end() - match.start()} caracteres")

# Substituir
codigo_novo = codigo[:match.start()] + nova_funcao + codigo[match.end():]

print("\n🔄 Substituindo função...")

# Criar backup
import shutil
from datetime import datetime

backup_nome = f"lotofacil_ultimate_final.py.backup_cores_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(arquivo, backup_nome)
print(f"📦 Backup criado: {backup_nome}")

# Salvar
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(codigo_novo)

print("✅ Arquivo atualizado com sucesso!")
print("\n" + "="*70)
print("  🎨 CORES ADICIONADAS COM SUCESSO!")
print("="*70 + "\n")

print("🧪 Testando o aplicativo...\n")

# Perguntar se quer testar
resposta = input("Deseja testar agora? (S/n): ").strip().lower()

if resposta != 'n':
    import subprocess
    print("\n🚀 Iniciando aplicativo...\n")
    subprocess.Popen(['python', arquivo])
    print("✅ Aplicativo iniciado!")
    print("\n📋 Próximos passos:")
    print("   1. Teste o módulo 'Análise ULTIMATE'")
    print("   2. Verifique se as cores aparecem")
    print("   3. Se estiver OK, recompile com: python correcao_automatica.py")
else:
    print("\n📋 Para testar, execute: python lotofacil_ultimate_final.py")
    print("📋 Para recompilar, execute: python correcao_automatica.py")

print("\n✅ Processo concluído!")
input("\nPressione ENTER para sair...")