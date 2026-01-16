"""
╔══════════════════════════════════════════════════════════════╗
║    LOTOFÁCIL QUANTUM - BUILD MANAGER ULTIMATE v2.0          ║
║              Sistema de Build Inteligente                    ║
║                Robinson Tax Master                           ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import psutil
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

class BuildManager:
    """Gerenciador inteligente de build"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dist_path = self.project_root / "dist" / "LotofacilULTIMATE"
        self.build_path = self.project_root / "build"
        self.main_file = "lotofacil_ultimate_final.py"
        self.exe_name = "LotofacilULTIMATE"
        self.log_file = f"build_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
    def print_header(self, text, style="="):
        """Imprime cabeçalho estilizado"""
        width = 70
        print(f"\n{Fore.CYAN}{style * width}")
        print(f"{Fore.YELLOW}{text.center(width)}")
        print(f"{Fore.CYAN}{style * width}\n")
    
    def print_step(self, step_num, total_steps, description):
        """Imprime passo do processo"""
        print(f"{Fore.GREEN}[{step_num}/{total_steps}] {Fore.WHITE}{description}")
    
    def print_success(self, message):
        """Imprime mensagem de sucesso"""
        print(f"{Fore.GREEN}✅ {message}")
    
    def print_error(self, message):
        """Imprime mensagem de erro"""
        print(f"{Fore.RED}❌ {message}")
    
    def print_warning(self, message):
        """Imprime mensagem de aviso"""
        print(f"{Fore.YELLOW}⚠️  {message}")
    
    def print_info(self, message):
        """Imprime mensagem informativa"""
        print(f"{Fore.CYAN}ℹ️  {message}")
    
    def log(self, message):
        """Salva log em arquivo"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    
    def find_process_by_name(self, process_name):
        """Encontra processos pelo nome"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def kill_processes(self):
        """Mata todos os processos relacionados"""
        self.print_step(1, 8, "🔫 Encerrando processos...")
        
        process_names = ["LotofacilULTIMATE", "python", "pythonw"]
        killed_count = 0
        
        for proc_name in process_names:
            processes = self.find_process_by_name(proc_name)
            for proc in processes:
                try:
                    self.print_info(f"Matando processo: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
                    proc.wait(timeout=5)
                    killed_count += 1
                    self.log(f"Processo morto: {proc.info['name']} (PID: {proc.info['pid']})")
                except Exception as e:
                    self.print_warning(f"Erro ao matar {proc.info['name']}: {e}")
        
        if killed_count > 0:
            self.print_success(f"{killed_count} processo(s) encerrado(s)")
            time.sleep(3)  # Aguardar sistema liberar arquivos
        else:
            self.print_info("Nenhum processo encontrado")
        
        return True
    
    def force_delete_directory(self, path):
        """Força exclusão de diretório com múltiplas tentativas"""
        if not path.exists():
            return True
        
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                self.print_info(f"Tentativa {attempt}/{max_attempts} de remover: {path.name}")
                
                # Método 1: shutil
                if path.exists():
                    shutil.rmtree(path, ignore_errors=True)
                
                time.sleep(1)
                
                # Método 2: CMD
                if path.exists():
                    subprocess.run(['cmd', '/c', 'rd', '/s', '/q', str(path)], 
                                 capture_output=True, timeout=10)
                
                time.sleep(1)
                
                # Verificar se removeu
                if not path.exists():
                    self.print_success(f"Diretório {path.name} removido")
                    return True
                
            except Exception as e:
                self.print_warning(f"Tentativa {attempt} falhou: {e}")
                time.sleep(2)
        
        if path.exists():
            self.print_error(f"Não foi possível remover {path.name}")
            return False
        
        return True
    
    def clean_directories(self):
        """Limpa diretórios de build"""
        self.print_step(2, 8, "🗑️  Limpando diretórios...")
        
        dirs_to_clean = [
            self.project_root / "dist",
            self.project_root / "build",
            self.project_root / "__pycache__"
        ]
        
        success = True
        for directory in dirs_to_clean:
            if directory.exists():
                result = self.force_delete_directory(directory)
                success = success and result
        
        # Remover arquivos .spec
        for spec_file in self.project_root.glob("*.spec"):
            try:
                spec_file.unlink()
                self.print_success(f"Arquivo removido: {spec_file.name}")
            except Exception as e:
                self.print_warning(f"Erro ao remover {spec_file.name}: {e}")
        
        if success:
            self.print_success("Limpeza concluída!")
        else:
            self.print_warning("Limpeza parcial - alguns arquivos podem estar em uso")
        
        return success
    
    def clear_pyinstaller_cache(self):
        """Limpa cache do PyInstaller"""
        self.print_step(3, 8, "🧹 Limpando cache do PyInstaller...")
        
        cache_paths = [
            Path(os.environ.get('LOCALAPPDATA', '')) / 'pyinstaller',
            Path.home() / '.pyinstaller'
        ]
        
        for cache_path in cache_paths:
            if cache_path.exists():
                try:
                    shutil.rmtree(cache_path, ignore_errors=True)
                    self.print_success(f"Cache removido: {cache_path}")
                except Exception as e:
                    self.print_warning(f"Erro ao limpar cache: {e}")
        
        self.print_success("Cache limpo!")
        return True
    
    def verify_dependencies(self):
        """Verifica dependências necessárias"""
        self.print_step(4, 8, "📦 Verificando dependências...")
        
        required = [
            'numpy', 'scipy', 'requests', 'beautifulsoup4',
            'openpyxl', 'reportlab', 'Pillow', 'pyinstaller', 'psutil'
        ]
        
        missing = []
        for package in required:
            try:
                __import__(package)
                self.print_info(f"✓ {package}")
            except ImportError:
                missing.append(package)
                self.print_warning(f"✗ {package} - FALTANDO")
        
        if missing:
            self.print_warning(f"Instalando pacotes faltantes: {', '.join(missing)}")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, 
                         capture_output=True)
            self.print_success("Dependências instaladas!")
        else:
            self.print_success("Todas as dependências OK!")
        
        return True
    
    def validate_source_file(self):
        """Valida arquivo fonte"""
        self.print_step(5, 8, "🔍 Validando arquivo fonte...")
        
        source_file = self.project_root / self.main_file
        
        if not source_file.exists():
            self.print_error(f"Arquivo não encontrado: {self.main_file}")
            return False
        
        # Verificar sintaxe
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                compile(f.read(), source_file, 'exec')
            self.print_success(f"Sintaxe válida: {self.main_file}")
            return True
        except SyntaxError as e:
            self.print_error(f"Erro de sintaxe: {e}")
            return False
    
    def build_executable(self):
        """Compila o executável"""
        self.print_step(6, 8, "🔨 Compilando executável...")
        self.print_info("Isso pode levar 3-5 minutos. Aguarde...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',
            f'--name={self.exe_name}',
            '--collect-data', 'setuptools',
            '--collect-data', 'scipy',
            '--hidden-import=scipy.special.cython_special',
            '--hidden-import=pkg_resources.extern',
            '--hidden-import=numpy.core._dtype_ctypes',
            self.main_file
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                self.print_success(f"Compilação concluída em {elapsed:.1f}s")
                self.log(f"Build bem-sucedido - Tempo: {elapsed:.1f}s")
                return True
            else:
                self.print_error("Erro na compilação")
                self.log(f"Erro no build: {result.stderr}")
                
                # Salvar log detalhado
                with open('build_error.log', 'w', encoding='utf-8') as f:
                    f.write(result.stderr)
                self.print_info("Log de erro salvo em: build_error.log")
                
                return False
                
        except subprocess.TimeoutExpired:
            self.print_error("Timeout na compilação (>10 minutos)")
            return False
        except Exception as e:
            self.print_error(f"Erro inesperado: {e}")
            return False
    
    def validate_build(self):
        """Valida build gerado"""
        self.print_step(7, 8, "✅ Validando build...")
        
        exe_path = self.dist_path / f"{self.exe_name}.exe"
        
        if not exe_path.exists():
            self.print_error(f"Executável não encontrado: {exe_path}")
            return False
        
        # Verificar tamanho
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        self.print_info(f"Tamanho: {size_mb:.1f} MB")
        
        if size_mb < 10:
            self.print_warning("Arquivo muito pequeno - pode estar incompleto")
            return False
        
        # Contar arquivos na pasta dist
        file_count = len(list(self.dist_path.rglob('*')))
        self.print_info(f"Total de arquivos: {file_count}")
        
        self.print_success("Build validado com sucesso!")
        return True
    
    def create_shortcuts(self):
        """Cria atalhos"""
        self.print_step(8, 8, "🔗 Criando atalhos...")
        
        exe_path = self.dist_path / f"{self.exe_name}.exe"
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / f"{self.exe_name}.lnk"
        
        try:
            # Criar atalho usando PowerShell
            ps_script = f"""
            $WS = New-Object -ComObject WScript.Shell
            $SC = $WS.CreateShortcut('{shortcut_path}')
            $SC.TargetPath = '{exe_path}'
            $SC.WorkingDirectory = '{self.dist_path}'
            $SC.Description = 'Lotofácil QUANTUM ULTIMATE'
            $SC.Save()
            """
            
            subprocess.run(['powershell', '-Command', ps_script], 
                         capture_output=True, timeout=10)
            
            if shortcut_path.exists():
                self.print_success(f"Atalho criado: {shortcut_path}")
            else:
                self.print_info("Atalho não criado (não obrigatório)")
                
        except Exception as e:
            self.print_warning(f"Erro ao criar atalho: {e}")
        
        return True
    
    def launch_application(self):
        """Inicia aplicação"""
        exe_path = self.dist_path / f"{self.exe_name}.exe"
        
        try:
            self.print_info("Iniciando aplicação...")
            subprocess.Popen(str(exe_path), shell=True)
            time.sleep(2)
            
            # Abrir pasta
            subprocess.Popen(f'explorer "{self.dist_path}"', shell=True)
            
            self.print_success("Aplicação iniciada!")
            return True
            
        except Exception as e:
            self.print_error(f"Erro ao iniciar: {e}")
            return False
    
    def run(self):
        """Executa processo completo de build"""
        self.print_header("LOTOFÁCIL QUANTUM - BUILD MANAGER ULTIMATE", "═")
        
        print(f"{Fore.CYAN}Sistema de Build Inteligente v2.0")
        print(f"{Fore.CYAN}Robinson Tax Master - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        
        steps = [
            ("Encerrar processos", self.kill_processes),
            ("Limpar diretórios", self.clean_directories),
            ("Limpar cache", self.clear_pyinstaller_cache),
            ("Verificar dependências", self.verify_dependencies),
            ("Validar fonte", self.validate_source_file),
            ("Compilar", self.build_executable),
            ("Validar build", self.validate_build),
            ("Criar atalhos", self.create_shortcuts)
        ]
        
        for step_name, step_func in steps:
            try:
                result = step_func()
                if not result:
                    self.print_error(f"Falha em: {step_name}")
                    self.print_info(f"Verifique o log: {self.log_file}")
                    return False
            except Exception as e:
                self.print_error(f"Erro em {step_name}: {e}")
                self.log(f"ERRO em {step_name}: {str(e)}")
                return False
        
        # Sucesso!
        self.print_header("✅ BUILD CONCLUÍDO COM SUCESSO!", "═")
        
        print(f"{Fore.GREEN}📁 Localização: {self.dist_path}")
        print(f"{Fore.GREEN}📦 Executável: {self.exe_name}.exe")
        print(f"{Fore.GREEN}📝 Log: {self.log_file}\n")
        
        # Perguntar se quer executar
        try:
            response = input(f"{Fore.YELLOW}Deseja iniciar a aplicação agora? (S/n): ").strip().lower()
            if response != 'n':
                self.launch_application()
        except:
            pass
        
        return True

def main():
    """Função principal"""
    try:
        manager = BuildManager()
        success = manager.run()
        
        if success:
            print(f"\n{Fore.GREEN}Processo concluído com sucesso!")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}Processo falhou. Verifique os logs.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Processo cancelado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()