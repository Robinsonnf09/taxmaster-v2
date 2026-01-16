"""
╔══════════════════════════════════════════════════════════════╗
║    CORREÇÃO AUTOMÁTICA - LOTOFÁCIL ULTIMATE                 ║
║    Sistema de Build Inteligente com Auto-Correção           ║
║                Robinson Tax Master                           ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

class CorrecaoAutomatica:
    """Sistema de correção e build automático"""
    
    def __init__(self):
        self.projeto_dir = Path.cwd()
        self.arquivo_principal = "lotofacil_ultimate_final.py"
        self.backup_dir = self.projeto_dir / "backups"
        # CORRIGIDO: usar barras normais
        self.temp_build = Path("C:/TEMP/lotofacil_build_final")
        self.dest_final = self.projeto_dir / "dist" / "LotofacilULTIMATE"
        
    def print_header(self, texto):
        """Imprime cabeçalho"""
        print("\n" + "="*70)
        print(f"  {texto}")
        print("="*70 + "\n")
    
    def print_step(self, numero, total, descricao):
        """Imprime etapa"""
        print(f"[{numero}/{total}] {descricao}")
    
    def print_success(self, msg):
        """Mensagem de sucesso"""
        print(f"✅ {msg}")
    
    def print_error(self, msg):
        """Mensagem de erro"""
        print(f"❌ {msg}")
    
    def print_info(self, msg):
        """Mensagem informativa"""
        print(f"ℹ️  {msg}")
    
    def criar_backup(self):
        """Cria backup do arquivo original"""
        self.print_step(1, 6, "📦 Criando backup...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{self.arquivo_principal}.backup_{timestamp}"
        
        arquivo_fonte = self.projeto_dir / self.arquivo_principal
        
        if not arquivo_fonte.exists():
            self.print_error(f"Arquivo não encontrado: {self.arquivo_principal}")
            return False
        
        shutil.copy2(arquivo_fonte, backup_file)
        self.print_success(f"Backup criado: {backup_file.name}")
        return True
    
    def corrigir_codigo(self):
        """Corrige o erro no código"""
        self.print_step(2, 6, "🔧 Corrigindo erro de formatação...")
        
        arquivo_path = self.projeto_dir / self.arquivo_principal
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            self.print_info("Arquivo lido com sucesso")
            
            import re
            
            correcoes = [
                (r"\{'':&lt;4\}", "    "),
                (r"\{'':<4\}", "    "),
                (r'\{"":&lt;4\}', "    "),
                (r'\{"":<4\}', "    "),
            ]
            
            total_correcoes = 0
            
            for padrao, substituicao in correcoes:
                matches = re.findall(padrao, codigo)
                if matches:
                    codigo = re.sub(padrao, substituicao, codigo)
                    total_correcoes += len(matches)
                    self.print_info(f"Corrigido {len(matches)} ocorrência(s)")
            
            if total_correcoes == 0:
                self.print_info("Código já está correto")
            else:
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    f.write(codigo)
                
                self.print_success(f"Total de {total_correcoes} correção(ões) aplicada(s)")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro ao corrigir código: {e}")
            return False
    
    def limpar_builds_antigos(self):
        """Limpa builds antigos"""
        self.print_step(3, 6, "🗑️  Limpando builds antigos...")
        
        if self.temp_build.exists():
            try:
                shutil.rmtree(self.temp_build, ignore_errors=True)
                self.print_info("Build temporário limpo")
            except:
                pass
        
        if self.dest_final.exists():
            try:
                shutil.rmtree(self.dest_final, ignore_errors=True)
                self.print_info("Dist local limpo")
            except:
                self.print_info("Dist local em uso")
        
        self.print_success("Limpeza concluída")
        return True
    
    def compilar_executavel(self):
        """Compila o executável"""
        self.print_step(4, 6, "🔨 Compilando executável...")
        self.print_info("Aguarde 2-5 minutos...")
        
        # Caminhos com Path
        dist_path = self.temp_build / "dist"
        build_path = self.temp_build / "build"
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',
            f'--distpath={str(dist_path)}',  # Converter para string
            f'--workpath={str(build_path)}',  # Converter para string
            '--name=LotofacilULTIMATE',
            '--collect-data', 'setuptools',
            '--collect-data', 'scipy',
            '--hidden-import=scipy.special.cython_special',
            '--hidden-import=pkg_resources.extern',
            '--hidden-import=numpy.core._dtype_ctypes',
            self.arquivo_principal
        ]
        
        try:
            inicio = time.time()
            
            resultado = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=600,
                cwd=str(self.projeto_dir)
            )
            
            tempo_decorrido = time.time() - inicio
            
            if resultado.returncode == 0:
                self.print_success(f"Compilação concluída em {tempo_decorrido:.1f}s")
                
                exe_path = dist_path / "LotofacilULTIMATE" / "LotofacilULTIMATE.exe"
                if exe_path.exists():
                    tamanho_mb = exe_path.stat().st_size / (1024 * 1024)
                    self.print_info(f"Executável criado: {tamanho_mb:.1f} MB")
                    return True
                else:
                    self.print_error("Executável não foi criado")
                    return False
            else:
                self.print_error("Erro na compilação")
                
                linhas_erro = resultado.stderr.split('\n')
                print("\n📋 ÚLTIMAS LINHAS DO ERRO:")
                for linha in linhas_erro[-15:]:
                    if linha.strip():
                        print(f"   {linha}")
                
                with open('erro_compilacao.log', 'w', encoding='utf-8') as f:
                    f.write(resultado.stderr)
                self.print_info("Log completo: erro_compilacao.log")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_error("Compilação excedeu 10 minutos")
            return False
        except Exception as e:
            self.print_error(f"Erro inesperado: {e}")
            return False
    
    def copiar_para_projeto(self):
        """Copia build para pasta do projeto"""
        self.print_step(5, 6, "📋 Copiando para pasta do projeto...")
        
        origem = self.temp_build / "dist" / "LotofacilULTIMATE"
        destino = self.dest_final
        
        try:
            if destino.exists():
                shutil.rmtree(destino, ignore_errors=True)
                time.sleep(1)
            
            destino.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copytree(origem, destino)
            
            exe_final = destino / "LotofacilULTIMATE.exe"
            if exe_final.exists():
                self.print_success(f"Copiado para: {destino}")
                return True
            else:
                self.print_error("Cópia falhou")
                return False
                
        except Exception as e:
            self.print_error(f"Erro ao copiar: {e}")
            return False
    
    def criar_atalho(self):
        """Cria atalho na área de trabalho"""
        self.print_step(6, 6, "🔗 Criando atalho...")
        
        exe_path = self.dest_final / "LotofacilULTIMATE.exe"
        
        try:
            ps_script = f'''
            $Desktop = [Environment]::GetFolderPath("Desktop")
            $WS = New-Object -ComObject WScript.Shell
            $SC = $WS.CreateShortcut("$Desktop\Lotofacil ULTIMATE.lnk")
            $SC.TargetPath = "{str(exe_path).replace(chr(92), chr(92)+chr(92))}"
            $SC.WorkingDirectory = "{str(self.dest_final).replace(chr(92), chr(92)+chr(92))}"
            $SC.Description = "Lotofacil QUANTUM ULTIMATE PRO"
            $SC.Save()
            '''
            
            subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                timeout=10
            )
            
            self.print_success("Atalho criado")
            return True
            
        except:
            self.print_info("Atalho não criado (opcional)")
            return True
    
    def testar_executavel(self):
        """Testa o executável"""
        print("\n" + "="*70)
        print("  🧪 TESTE DO EXECUTÁVEL")
        print("="*70 + "\n")
        
        exe_path = self.dest_final / "LotofacilULTIMATE.exe"
        
        try:
            resposta = input("Deseja iniciar o aplicativo agora? (S/n): ").strip().lower()
            
            if resposta != 'n':
                self.print_info("Iniciando aplicação...")
                subprocess.Popen(str(exe_path), shell=True)
                time.sleep(2)
                
                subprocess.Popen(f'explorer "{self.dest_final}"', shell=True)
                
                self.print_success("Aplicação iniciada!")
            else:
                self.print_info(f"Executável: {exe_path}")
                
        except Exception as e:
            self.print_error(f"Erro ao iniciar: {e}")
    
    def executar(self):
        """Executa o processo completo"""
        self.print_header("🚀 CORREÇÃO E BUILD AUTOMÁTICO - LOTOFÁCIL ULTIMATE")
        
        print(f"📁 Projeto: {self.projeto_dir}")
        print(f"📄 Arquivo: {self.arquivo_principal}")
        print(f"🎯 Build temp: {self.temp_build}")
        print(f"📦 Destino: {self.dest_final}\n")
        
        input("Pressione ENTER para iniciar...")
        
        etapas = [
            ("Criar backup", self.criar_backup),
            ("Corrigir código", self.corrigir_codigo),
            ("Limpar builds", self.limpar_builds_antigos),
            ("Compilar", self.compilar_executavel),
            ("Copiar", self.copiar_para_projeto),
            ("Criar atalho", self.criar_atalho),
        ]
        
        for nome, funcao in etapas:
            try:
                resultado = funcao()
                if not resultado:
                    self.print_error(f"Falha em: {nome}")
                    print("\n❌ Processo interrompido!")
                    return False
            except Exception as e:
                self.print_error(f"Erro em {nome}: {e}")
                return False
        
        self.print_header("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        
        print(f"📁 Executável: {self.dest_final / 'LotofacilULTIMATE.exe'}")
        print(f"📦 Backup: {self.backup_dir}\n")
        
        self.testar_executavel()
        
        return True

def main():
    """Função principal"""
    try:
        correcao = CorrecaoAutomatica()
        sucesso = correcao.executar()
        
        if sucesso:
            print("\n🎉 Tudo pronto!")
            input("\nPressione ENTER para sair...")
            sys.exit(0)
        else:
            print("\n❌ Processo falhou.")
            input("\nPressione ENTER para sair...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Cancelado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()