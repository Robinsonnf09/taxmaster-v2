import os

pasta = "oficios_requisitorios_tjsp"
arquivos = [f for f in os.listdir(pasta) if f.endswith('.pdf')][:3]

print(f"\n🔍 ANALISANDO {len(arquivos)} PRIMEIROS PDFs:\n")

for arquivo in arquivos:
    caminho = os.path.join(pasta, arquivo)
    
    with open(caminho, 'rb') as f:
        primeiros_bytes = f.read(100)
    
    print(f"📄 {arquivo}")
    print(f"   Tamanho: {os.path.getsize(caminho)} bytes")
    print(f"   Primeiros bytes: {primeiros_bytes[:50]}")
    
    # Verificar se é HTML (erro)
    if b'<html' in primeiros_bytes.lower() or b'<!doctype' in primeiros_bytes.lower():
        print(f"   ❌ ARQUIVO É HTML (ERRO DE AUTENTICAÇÃO/SESSÃO)")
    elif primeiros_bytes.startswith(b'%PDF'):
        print(f"   ✅ É UM PDF VÁLIDO")
    else:
        print(f"   ⚠️  FORMATO DESCONHECIDO")
    
    print()
