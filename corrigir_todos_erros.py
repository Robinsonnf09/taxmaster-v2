"""
Correção COMPLETA de todos os erros de formatação
"""
import re

# Ler arquivo
with open('lotofacil_ultimate_final.py', 'r', encoding='utf-8') as f:
    codigo = f.read()

print("🔍 Procurando erros de formatação...")

# Todos os padrões problemáticos
padroes_erro = [
    (r"\{'':<\d+\}", "    "),  # {'':&lt;número}
    (r'\{"":<\d+\}', "    "),  # {"":&lt;número}
    (r"\{'':&lt;\d+\}", "    "),  # Versão HTML entity
    (r'\{"":&lt;\d+\}', "    "),  # Versão HTML entity
]

total_correcoes = 0
linhas_corrigidas = []

# Dividir em linhas para encontrar os números
linhas = codigo.split('\n')

for i, linha in enumerate(linhas, 1):
    linha_original = linha
    linha_corrigida = linha
    
    # Aplicar todos os padrões
    for padrao, substituicao in padroes_erro:
        if re.search(padrao, linha_corrigida):
            linha_corrigida = re.sub(padrao, substituicao, linha_corrigida)
    
    # Se mudou, registrar
    if linha_original != linha_corrigida:
        total_correcoes += 1
        linhas_corrigidas.append(i)
        print(f"✅ Linha {i}: {linha_original.strip()[:60]}")

# Reconstruir código
codigo_corrigido = '\n'.join(
    re.sub(padrao, substituicao, linha)
    for linha in linhas
    for padrao, substituicao in padroes_erro
)

# Aplicar correções
for padrao, substituicao in padroes_erro:
    codigo_corrigido = re.sub(padrao, substituicao, codigo)

if total_correcoes > 0:
    # Salvar
    with open('lotofacil_ultimate_final.py', 'w', encoding='utf-8') as f:
        f.write(codigo_corrigido)
    
    print(f"\n🎉 {total_correcoes} erro(s) corrigido(s)!")
    print(f"📋 Linhas afetadas: {linhas_corrigidas}")
else:
    print("\n✅ Nenhum erro encontrado (código já está correto)")