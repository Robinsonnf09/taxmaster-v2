"""
REPARADOR ROBUSTO DE PDFs - Múltiplas Estratégias
Usa PyPDF2 + pikepdf + pdfplumber para corrigir PDFs corrompidos
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import PyPDF2
import pdfplumber

try:
    import pikepdf
    PIKEPDF_DISPONIVEL = True
except:
    PIKEPDF_DISPONIVEL = False
    print("⚠️  pikepdf não instalado (opcional)")

class ReparadorRobusto:
    
    def __init__(self, pasta_origem):
        self.pasta_origem = pasta_origem
        self.pasta_backup = f"{pasta_origem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.pasta_reparados = f"{pasta_origem}_reparados"
        
        self.sucessos = 0
        self.falhas = 0
        self.erros = []
        
    def criar_backup(self):
        """Cria backup antes de reparar"""
        
        print(f"\n💾 Criando backup...")
        
        if not os.path.exists(self.pasta_backup):
            shutil.copytree(self.pasta_origem, self.pasta_backup)
            print(f"   ✅ Backup: {self.pasta_backup}")
        
    def reparar_com_pypdf2(self, pdf_path):
        """Tenta reparar com PyPDF2"""
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file, strict=False)
                
                # Criar novo PDF
                writer = PyPDF2.PdfWriter()
                
                for page in reader.pages:
                    writer.add_page(page)
                
                # Salvar reparado
                nome = os.path.basename(pdf_path)
                destino = os.path.join(self.pasta_reparados, nome)
                
                with open(destino, 'wb') as output:
                    writer.write(output)
                
                return True, "PyPDF2"
                
        except Exception as e:
            return False, str(e)
    
    def reparar_com_pikepdf(self, pdf_path):
        """Tenta reparar com pikepdf"""
        
        if not PIKEPDF_DISPONIVEL:
            return False, "pikepdf não disponível"
        
        try:
            nome = os.path.basename(pdf_path)
            destino = os.path.join(self.pasta_reparados, nome)
            
            with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                pdf.save(destino)
            
            return True, "pikepdf"
            
        except Exception as e:
            return False, str(e)
    
    def reparar_com_pdfplumber(self, pdf_path):
        """Tenta validar/copiar com pdfplumber"""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Se conseguir abrir, apenas copiar
                nome = os.path.basename(pdf_path)
                destino = os.path.join(self.pasta_reparados, nome)
                shutil.copy2(pdf_path, destino)
                
                return True, "pdfplumber (cópia)"
                
        except Exception as e:
            return False, str(e)
    
    def reparar_pdf(self, pdf_path):
        """Tenta reparar PDF com múltiplas estratégias"""
        
        nome = os.path.basename(pdf_path)
        
        # Estratégia 1: PyPDF2
        sucesso, metodo = self.reparar_com_pypdf2(pdf_path)
        if sucesso:
            return True, metodo
        
        # Estratégia 2: pikepdf
        sucesso, metodo = self.reparar_com_pikepdf(pdf_path)
        if sucesso:
            return True, metodo
        
        # Estratégia 3: pdfplumber (apenas validação)
        sucesso, metodo = self.reparar_com_pdfplumber(pdf_path)
        if sucesso:
            return True, metodo
        
        return False, "Todas as estratégias falharam"
    
    def processar_todos(self):
        """Processa todos os PDFs"""
        
        print(f"\n🔍 Procurando PDFs em: {self.pasta_origem}")
        
        pdfs = [f for f in os.listdir(self.pasta_origem) if f.endswith('.pdf')]
        total = len(pdfs)
        
        if total == 0:
            print(f"\n❌ Nenhum PDF encontrado!")
            return
        
        print(f"\n📊 Total: {total} PDFs")
        
        # Criar pasta de reparados
        if not os.path.exists(self.pasta_reparados):
            os.makedirs(self.pasta_reparados)
        
        print(f"\n🔧 Reparando...")
        
        for idx, pdf in enumerate(pdfs, 1):
            if idx % 50 == 0 or idx == 1:
                print(f"   📋 {idx}/{total} ({idx/total*100:.1f}%) - ✅ {self.sucessos} | ❌ {self.falhas}", end="\r")
            
            pdf_path = os.path.join(self.pasta_origem, pdf)
            
            try:
                sucesso, metodo = self.reparar_pdf(pdf_path)
                
                if sucesso:
                    self.sucessos += 1
                else:
                    self.falhas += 1
                    self.erros.append({
                        'arquivo': pdf,
                        'erro': metodo
                    })
                    
            except Exception as e:
                self.falhas += 1
                self.erros.append({
                    'arquivo': pdf,
                    'erro': str(e)
                })
        
        print(f"\n   ✅ {total} PDFs processados!")
    
    def gerar_relatorio(self):
        """Gera relatório"""
        
        print(f"\n" + "="*70)
        print(f"📊 RELATÓRIO DE REPARO")
        print("="*70)
        
        total = self.sucessos + self.falhas
        taxa_sucesso = (self.sucessos / total * 100) if total > 0 else 0
        
        print(f"\n   📊 Total processado: {total}")
        print(f"   ✅ Reparados com sucesso: {self.sucessos} ({taxa_sucesso:.1f}%)")
        print(f"   ❌ Falhas: {self.falhas}")
        
        if self.falhas > 0:
            print(f"\n   ⚠️  PDFs que não puderam ser reparados:")
            for erro in self.erros[:10]:
                print(f"      • {erro['arquivo']}")
            
            if len(self.erros) > 10:
                print(f"      ... e mais {len(self.erros) - 10}")
        
        print(f"\n   📁 PDFs reparados em: {self.pasta_reparados}")
        print(f"   💾 Backup em: {self.pasta_backup}")

if __name__ == "__main__":
    print("="*70)
    print("🔧 REPARADOR ROBUSTO DE PDFs")
    print("="*70)
    
    pasta = "oficios_requisitorios_tjsp"
    
    if not os.path.exists(pasta):
        print(f"\n❌ Pasta não encontrada: {pasta}")
        input("\nENTER...")
        exit()
    
    pdfs = [f for f in os.listdir(pasta) if f.endswith('.pdf')]
    print(f"\n📊 Encontrados: {len(pdfs)} PDFs")
    
    print(f"\n💾 BACKUP será criado automaticamente")
    print(f"📁 Reparados serão salvos em: {pasta}_reparados")
    
    confirma = input(f"\nReparar {len(pdfs)} PDFs? (s/n): ").lower()
    
    if confirma != 's':
        print("\n❌ Cancelado")
        exit()
    
    try:
        inicio = datetime.now()
        
        reparador = ReparadorRobusto(pasta)
        
        reparador.criar_backup()
        reparador.processar_todos()
        reparador.gerar_relatorio()
        
        fim = datetime.now()
        duracao = int((fim - inicio).total_seconds() / 60)
        
        print(f"\n⏱️  Tempo: {duracao} minutos")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n\nENTER...\n")
    
    print("\n✅ FIM!")
