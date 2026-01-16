"""
╔══════════════════════════════════════════════════════════════╗
║    DEPLOY PARA PRODUÇÃO - LOTOFÁCIL ULTIMATE                ║
║    Compilação Final + Empacotamento Profissional            ║
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
import zipfile

class DeployProducao:
    """Sistema completo de deploy para produção"""
    
    def __init__(self):
        self.projeto_dir = Path.cwd()
        self.arquivo_principal = "lotofacil_ultimate_final.py"
        self.nome_app = "LotofacilULTIMATE"
        self.versao = "6.0"
        
        # Diretórios
        self.temp_build = Path("C:/TEMP/lotofacil_build_final")
        self.dist_dir = self.projeto_dir / "dist" / self.nome_app
        self.producao_dir = self.projeto_dir / "PRODUCAO"
        self.release_dir = self.producao_dir / f"Release_v{self.versao}_{datetime.now().strftime('%Y%m%d')}"
        
    def print_header(self, texto):
        print("\n" + "="*70)
        print(f"  {texto}")
        print("="*70 + "\n")
    
    def print_step(self, numero, total, descricao):
        print(f"[{numero}/{total}] {descricao}")
    
    def print_success(self, msg):
        print(f"✅ {msg}")
    
    def print_error(self, msg):
        print(f"❌ {msg}")
    
    def print_info(self, msg):
        print(f"ℹ️  {msg}")
    
    def verificar_ambiente(self):
        """Verifica se o ambiente está pronto"""
        self.print_step(1, 8, "🔍 Verificando ambiente...")
        
        # Verificar arquivo principal
        if not (self.projeto_dir / self.arquivo_principal).exists():
            self.print_error(f"Arquivo não encontrado: {self.arquivo_principal}")
            return False
        
        # Verificar PyInstaller
        try:
            subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                          capture_output=True, check=True)
            self.print_info("PyInstaller instalado")
        except:
            self.print_error("PyInstaller não instalado")
            return False
        
        self.print_success("Ambiente OK")
        return True
    
    def limpar_builds_antigos(self):
        """Limpa builds antigos"""
        self.print_step(2, 8, "🗑️  Limpando builds antigos...")
        
        # Limpar TEMP
        if self.temp_build.exists():
            try:
                shutil.rmtree(self.temp_build, ignore_errors=True)
                self.print_info("Build temporário limpo")
            except:
                pass
        
        # Limpar dist local
        if self.dist_dir.exists():
            try:
                shutil.rmtree(self.dist_dir, ignore_errors=True)
                self.print_info("Dist local limpo")
            except:
                pass
        
        self.print_success("Limpeza concluída")
        return True
    
    def compilar_producao(self):
        """Compila versão de produção"""
        self.print_step(3, 8, "🔨 Compilando versão de PRODUÇÃO...")
        self.print_info("Aguarde 2-5 minutos...")
        
        dist_path = self.temp_build / "dist"
        build_path = self.temp_build / "build"
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',
            '--onedir',
            f'--distpath={str(dist_path)}',
            f'--workpath={str(build_path)}',
            f'--name={self.nome_app}',
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
                
                exe_path = dist_path / self.nome_app / f"{self.nome_app}.exe"
                if exe_path.exists():
                    tamanho_mb = exe_path.stat().st_size / (1024 * 1024)
                    self.print_info(f"Executável criado: {tamanho_mb:.1f} MB")
                    return True
                else:
                    self.print_error("Executável não foi criado")
                    return False
            else:
                self.print_error("Erro na compilação")
                return False
                
        except Exception as e:
            self.print_error(f"Erro: {e}")
            return False
    
    def copiar_para_dist(self):
        """Copia para pasta dist do projeto"""
        self.print_step(4, 8, "📋 Copiando para dist...")
        
        origem = self.temp_build / "dist" / self.nome_app
        destino = self.dist_dir
        
        try:
            if destino.exists():
                shutil.rmtree(destino, ignore_errors=True)
                time.sleep(1)
            
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(origem, destino)
            
            self.print_success(f"Copiado para: {destino}")
            return True
                
        except Exception as e:
            self.print_error(f"Erro ao copiar: {e}")
            return False
    
    def criar_estrutura_producao(self):
        """Cria estrutura de produção profissional"""
        self.print_step(5, 8, "📦 Criando estrutura de produção...")
        
        try:
            # Criar diretórios
            self.release_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar aplicativo
            app_dest = self.release_dir / self.nome_app
            if app_dest.exists():
                shutil.rmtree(app_dest)
            shutil.copytree(self.dist_dir, app_dest)
            
            self.print_success("Estrutura criada")
            return True
            
        except Exception as e:
            self.print_error(f"Erro: {e}")
            return False
    
    def criar_documentacao(self):
        """Cria documentação básica"""
        self.print_step(6, 8, "📄 Criando documentação...")
        
        try:
            # README
            readme = self.release_dir / "LEIA-ME.txt"
            with open(readme, 'w', encoding='utf-8') as f:
                f.write(f"""
╔══════════════════════════════════════════════════════════════╗
║    LOTOFÁCIL QUANTUM ULTIMATE v{self.versao}                        ║
║    Sistema Profissional de Análise Estatística              ║
╚══════════════════════════════════════════════════════════════╝

📋 INSTALAÇÃO:
   1. Copie a pasta "{self.nome_app}" para C:\Program Files\ ou local desejado
   2. Execute {self.nome_app}.exe
   3. Pronto para usar!

🚀 COMO USAR:
   1. Clique em "🔬 Análise ULTIMATE" para baixar dados da Caixa
   2. Aguarde 1-2 minutos (carrega 100 concursos)
   3. Veja o ranking de números (quentes/frios/neutros)
   4. Configure tipo de jogo e quantidade
   5. Clique em "🎲 Gerar Jogos"
   6. Salve em Excel ou PDF

⚙️ REQUISITOS:
   - Windows 10/11
   - Conexão com internet (para baixar dados da Caixa)
   - 100 MB de espaço em disco

🔬 TECNOLOGIA:
   ✅ Dados REAIS da API oficial da Caixa Econômica Federal
   ✅ 6 algoritmos estatísticos combinados
   ✅ Machine Learning para detecção de padrões
   ✅ Cálculo de ROI e Expected Value
   ✅ Gap Analysis (técnica avançada)

⚠️ AVISO LEGAL:
   Este sistema realiza análise estatística de dados históricos.
   NÃO garante resultados futuros ou vitórias.
   Cada sorteio da Lotofácil é independente e aleatório.
   Jogue com responsabilidade.

📧 SUPORTE:
   Data de Release: {datetime.now().strftime('%d/%m/%Y')}
   Versão: {self.versao}
   
© {datetime.now().year} - Uso Profissional
""")
            
            self.print_info("README criado")
            
            # Notas de versão
            changelog = self.release_dir / "CHANGELOG.txt"
            with open(changelog, 'w', encoding='utf-8') as f:
                f.write(f"""
CHANGELOG - LOTOFÁCIL ULTIMATE

v{self.versao} ({datetime.now().strftime('%d/%m/%Y')}):
  ✅ Interface colorida (números quentes/frios)
  ✅ Correção de formatação de texto
  ✅ Sistema de análise ULTIMATE funcionando
  ✅ Conexão estável com API da Caixa
  ✅ Geração de jogos otimizada
  ✅ Export para Excel e PDF
  
Melhorias Técnicas:
  - Algoritmo de 6 fatores estatísticos
  - Machine Learning para padrões
  - Gap Analysis avançada
  - Cálculo de ROI e Expected Value
  - Sistema de retry robusto
  - Interface profissional
""")
            
            self.print_success("Documentação criada")
            return True
            
        except Exception as e:
            self.print_error(f"Erro: {e}")
            return False
    
    def criar_atalho_desktop(self):
        """Cria atalho na área de trabalho"""
        self.print_step(7, 8, "🔗 Criando atalho...")
        
        exe_path = self.dist_dir / f"{self.nome_app}.exe"
        
        try:
            ps_script = f'''
            $Desktop = [Environment]::GetFolderPath("Desktop")
            $WS = New-Object -ComObject WScript.Shell
            $SC = $WS.CreateShortcut("$Desktop\Lotofacil ULTIMATE v{self.versao}.lnk")
            $SC.TargetPath = "{str(exe_path).replace(chr(92), chr(92)+chr(92))}"
            $SC.WorkingDirectory = "{str(self.dist_dir).replace(chr(92), chr(92)+chr(92))}"
            $SC.Description = "Lotofacil QUANTUM ULTIMATE v{self.versao}"
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
    
    def criar_pacote_zip(self):
        """Cria pacote ZIP para distribuição"""
        self.print_step(8, 8, "📦 Criando pacote de distribuição...")
        
        try:
            zip_nome = f"LotofacilULTIMATE_v{self.versao}_{datetime.now().strftime('%Y%m%d')}.zip"
            zip_path = self.producao_dir / zip_nome
            
            self.print_info("Compactando...")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adicionar aplicativo
                for root, dirs, files in os.walk(self.release_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.release_dir.parent)
                        zipf.write(file_path, arcname)
            
            tamanho_mb = zip_path.stat().st_size / (1024 * 1024)
            self.print_success(f"Pacote criado: {zip_nome} ({tamanho_mb:.1f} MB)")
            self.print_info(f"Local: {zip_path}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Erro ao criar ZIP: {e}")
            return False
    
    def testar_executavel(self):
        """Testa o executável"""
        self.print_header("🧪 TESTE FINAL")
        
        exe_path = self.dist_dir / f"{self.nome_app}.exe"
        
        print(f"📁 Executável: {exe_path}")
        print(f"📦 Pacote: {self.producao_dir}")
        print(f"📋 Documentação: {self.release_dir}\n")
        
        resposta = input("Deseja testar o executável agora? (S/n): ").strip().lower()
        
        if resposta != 'n':
            try:
                self.print_info("Iniciando aplicação...")
                subprocess.Popen(str(exe_path), shell=True)
                time.sleep(2)
                
                # Abrir pasta de produção
                subprocess.Popen(f'explorer "{self.producao_dir}"', shell=True)
                
                self.print_success("Aplicação iniciada!")
            except Exception as e:
                self.print_error(f"Erro ao iniciar: {e}")
    
    def executar(self):
        """Executa o processo completo de deploy"""
        self.print_header("🚀 DEPLOY PARA PRODUÇÃO - LOTOFÁCIL ULTIMATE")
        
        print(f"📁 Projeto: {self.projeto_dir}")
        print(f"📄 Arquivo: {self.arquivo_principal}")
        print(f"📦 Produção: {self.release_dir}")
        print(f"🎯 Versão: {self.versao}\n")
        
        input("Pressione ENTER para iniciar o deploy...")
        
        # Executar etapas
        etapas = [
            ("Verificar ambiente", self.verificar_ambiente),
            ("Limpar builds", self.limpar_builds_antigos),
            ("Compilar produção", self.compilar_producao),
            ("Copiar para dist", self.copiar_para_dist),
            ("Criar estrutura", self.criar_estrutura_producao),
            ("Criar documentação", self.criar_documentacao),
            ("Criar atalho", self.criar_atalho_desktop),
            ("Criar pacote ZIP", self.criar_pacote_zip),
        ]
        
        for nome, funcao in etapas:
            try:
                resultado = funcao()
                if not resultado:
                    self.print_error(f"Falha em: {nome}")
                    print("\n❌ Deploy interrompido!")
                    return False
            except Exception as e:
                self.print_error(f"Erro em {nome}: {e}")
                return False
        
        # Sucesso!
        self.print_header("✅ DEPLOY CONCLUÍDO COM SUCESSO!")
        
        print(f"📁 Executável: {self.dist_dir / f'{self.nome_app}.exe'}")
        print(f"📦 Pacote ZIP: {self.producao_dir}")
        print(f"📋 Documentação: {self.release_dir}")
        print(f"🔗 Atalho: Área de Trabalho\n")
        
        # Testar
        self.testar_executavel()
        
        print("\n" + "="*70)
        print("  🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("="*70)
        print(f"\n📦 Distribua o arquivo ZIP localizado em:")
        print(f"   {self.producao_dir}\n")
        
        return True

def main():
    """Função principal"""
    try:
        deploy = DeployProducao()
        sucesso = deploy.executar()
        
        if sucesso:
            print("\n🎉 Deploy finalizado! Sistema em produção!")
            input("\nPressione ENTER para sair...")
            sys.exit(0)
        else:
            print("\n❌ Deploy falhou. Verifique os erros acima.")
            input("\nPressione ENTER para sair...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Deploy cancelado.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()