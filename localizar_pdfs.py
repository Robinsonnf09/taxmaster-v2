"""
LOCALIZAR E ORGANIZAR OFÍCIOS
Encontra automaticamente a pasta com PDFs
"""

import os
from collections import defaultdict

def encontrar_pasta_pdfs():
    """Encontra pasta com mais PDFs"""
    
    print("\n🔍 Procurando PDFs...")
    
    pastas_candidatas = []
    
    # Procurar na pasta atual e subpastas
    for root, dirs, files in os.walk('.'):
        pdfs = [f for f in files if f.endswith('.pdf')]
        
        if len(pdfs) > 100:  # Só pastas com muitos PDFs
            pastas_candidatas.append({
                'caminho': root,
                'quantidade': len(pdfs)
            })
            print(f"   ✅ {root}: {len(pdfs)} PDFs")
    
    if not pastas_candidatas:
        print("\n❌ Nenhuma pasta com PDFs encontrada!")
        return None
    
    # Pegar a pasta com mais PDFs
    pasta_maior = max(pastas_candidatas, key=lambda x: x['quantidade'])
    
    print(f"\n📁 Pasta com mais PDFs:")
    print(f"   {pasta_maior['caminho']}")
    print(f"   {pasta_maior['quantidade']} PDFs")
    
    return pasta_maior['caminho']

if __name__ == "__main__":
    print("="*70)
    print("🔍 LOCALIZADOR DE OFÍCIOS")
    print("="*70)
    
    pasta = encontrar_pasta_pdfs()
    
    if pasta:
        print(f"\n✅ Pasta encontrada!")
        print(f"\n📝 Use este caminho no script:")
        print(f"   pasta_origem = \"{pasta}\"")
    
    input("\n\nENTER...")
