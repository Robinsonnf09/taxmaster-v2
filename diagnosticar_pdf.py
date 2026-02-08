"""
DIAGNÓSTICO DE PDF - Testar extração
"""

import os
import PyPDF2
import sys

def diagnosticar_pdf(caminho_pdf):
    """Diagnostica um PDF específico"""
    
    print(f"\n📄 Analisando: {os.path.basename(caminho_pdf)}")
    print("="*70)
    
    try:
        with open(caminho_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            print(f"\n📊 INFORMAÇÕES:")
            print(f"   Páginas: {len(reader.pages)}")
            
            # Verificar se é protegido
            if reader.is_encrypted:
                print(f"   🔒 PDF PROTEGIDO/CRIPTOGRAFADO")
                return
            
            print(f"   🔓 PDF não protegido")
            
            # Tentar extrair texto da primeira página
            print(f"\n📖 TENTANDO EXTRAIR TEXTO DA PÁGINA 1:")
            print("-"*70)
            
            try:
                texto = reader.pages[0].extract_text()
                
                if texto and len(texto.strip()) > 0:
                    print(f"\n✅ TEXTO EXTRAÍDO ({len(texto)} caracteres):")
                    print("-"*70)
                    # Mostrar primeiros 500 caracteres
                    print(texto[:500])
                    print("-"*70)
                    
                    # Procurar palavras-chave
                    print(f"\n🔍 PALAVRAS-CHAVE ENCONTRADAS:")
                    palavras = ['estado', 'município', 'fazenda', 'requisitório', 
                               'devedor', 'precatório', 'são paulo', 'educação', 
                               'saúde', 'ipesp', 'spprev']
                    
                    for palavra in palavras:
                        if palavra.lower() in texto.lower():
                            print(f"   ✅ '{palavra}'")
                else:
                    print(f"\n❌ NENHUM TEXTO EXTRAÍDO")
                    print(f"   Possível causa: PDF é imagem digitalizada (precisa OCR)")
                    
            except Exception as e:
                print(f"\n❌ ERRO NA EXTRAÇÃO: {e}")
            
            # Tentar segunda página
            if len(reader.pages) > 1:
                print(f"\n📖 TENTANDO PÁGINA 2:")
                print("-"*70)
                try:
                    texto2 = reader.pages[1].extract_text()
                    if texto2 and len(texto2.strip()) > 0:
                        print(f"✅ Texto extraído ({len(texto2)} caracteres)")
                        print(texto2[:300])
                    else:
                        print(f"❌ Nenhum texto")
                except Exception as e:
                    print(f"❌ Erro: {e}")
                    
    except Exception as e:
        print(f"\n❌ ERRO AO ABRIR PDF: {e}")

if __name__ == "__main__":
    print("="*70)
    print("🔍 DIAGNÓSTICO DE PDF")
    print("="*70)
    
    pasta = r"oficios_organizados\Erro na Leitura"
    
    if not os.path.exists(pasta):
        print(f"\n❌ Pasta não encontrada: {pasta}")
        input("\nENTER...")
        sys.exit()
    
    # Pegar primeiro PDF
    pdfs = [f for f in os.listdir(pasta) if f.endswith('.pdf')]
    
    if not pdfs:
        print(f"\n❌ Nenhum PDF encontrado!")
        input("\nENTER...")
        sys.exit()
    
    print(f"\n📁 Pasta: {pasta}")
    print(f"📄 Total PDFs: {len(pdfs)}")
    
    # Testar 3 PDFs diferentes
    amostras = min(3, len(pdfs))
    
    print(f"\n🔬 Testando {amostras} PDFs:")
    
    for i in range(amostras):
        pdf_path = os.path.join(pasta, pdfs[i])
        diagnosticar_pdf(pdf_path)
        print("\n" + "="*70)
    
    input("\n\nENTER...")
    
    print("\n✅ FIM!")
