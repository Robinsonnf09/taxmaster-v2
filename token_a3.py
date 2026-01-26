"""
Módulo TOKEN A3 - VERSÃO MELHORADA
Detecção mais robusta e tolerante a erros
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import ctypes

class TokenA3Manager:
    """Gerenciador de Token A3 - Versão Melhorada"""
    
    MIDDLEWARES = {
        'windows': {
            'safenet': r'C:\Windows\System32\eTPKCS11.dll',
            'certisign': r'C:\Windows\System32\aetpkss1.dll',
            'safeweb': r'C:\Program Files\Safeweb\*.dll',
            'gemalto': r'C:\Windows\System32\gclib.dll'
        }
    }
    
    def __init__(self):
        self.sistema = platform.system().lower()
        self.middleware_path = None
        self.middleware_nome = None
        self.token_detectado = False
        
    def detectar_middleware(self):
        """Detecta qual middleware está instalado"""
        print("\n🔍 Detectando middleware do token...")
        
        if 'windows' in self.sistema:
            middlewares = self.MIDDLEWARES['windows']
        else:
            print("❌ Sistema operacional não suportado")
            return False
        
        for nome, caminho in middlewares.items():
            if '*' in caminho:
                pasta = os.path.dirname(caminho)
                if os.path.exists(pasta):
                    arquivos = list(Path(pasta).glob('*.dll'))
                    if arquivos:
                        self.middleware_path = str(arquivos[0])
                        self.middleware_nome = nome
                        print(f"✅ Middleware {nome} detectado: {self.middleware_path}")
                        return True
            else:
                if os.path.exists(caminho):
                    self.middleware_path = caminho
                    self.middleware_nome = nome
                    print(f"✅ Middleware {nome} detectado: {caminho}")
                    return True
        
        print("❌ Nenhum middleware detectado!")
        return False
    
    def verificar_token_conectado_windows(self):
        """Verifica token no Windows usando múltiplos métodos"""
        print("\n🔌 Verificando token...")
        
        metodos = [
            self._verificar_com_certutil,
            self._verificar_com_wmi,
            self._verificar_com_registry
        ]
        
        for metodo in metodos:
            try:
                if metodo():
                    return True
            except:
                continue
        
        return False
    
    def _verificar_com_certutil(self):
        """Método 1: certutil (mais rápido)"""
        try:
            result = subprocess.run(
                ['certutil', '-scinfo'],
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            if 'Reader' in result.stdout or 'Smart Card' in result.stdout:
                print("✅ Token detectado via certutil!")
                return True
                
        except subprocess.TimeoutExpired:
            print("⚠️  certutil timeout (normal se token não conectado)")
        except Exception as e:
            print(f"⚠️  certutil não disponível: {str(e)}")
        
        return False
    
    def _verificar_com_wmi(self):
        """Método 2: WMI"""
        try:
            result = subprocess.run(
                ['wmic', 'path', 'Win32_USBControllerDevice', 'get', 'Dependent'],
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            # Procurar por termos relacionados a smart card/token
            termos = ['smart', 'card', 'token', 'safenet', 'gemalto', 'etoken']
            texto_lower = result.stdout.lower()
            
            for termo in termos:
                if termo in texto_lower:
                    print("✅ Token detectado via WMI!")
                    return True
                    
        except Exception as e:
            print(f"⚠️  WMI não disponível: {str(e)}")
        
        return False
    
    def _verificar_com_registry(self):
        """Método 3: Registry"""
        try:
            result = subprocess.run(
                ['reg', 'query', 'HKLM\SOFTWARE\Microsoft\Cryptography\Calais\SmartCards'],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Smart card detectado via registry!")
                return True
                
        except Exception as e:
            print(f"⚠️  Registry não acessível: {str(e)}")
        
        return False
    
    def validar_token_conectado(self):
        """Valida se token está conectado"""
        
        if self.verificar_token_conectado_windows():
            self.token_detectado = True
            print("\n✅ Token A3 conectado e pronto!")
            return True
        else:
            print("\n❌ Token não detectado")
            print("\n📋 TROUBLESHOOTING:")
            print("   1. Token está FISICAMENTE conectado na USB?")
            print("   2. LED do token está aceso?")
            print("   3. Já usou o token neste computador antes?")
            print("   4. Reinstale o middleware SafeNet")
            print("\n💡 DICA: O sistema funcionará mesmo sem token para testes!")
            return False
    
    def modo_teste_sem_token(self):
        """Permite usar sistema mesmo sem token (para desenvolvimento)"""
        print("\n⚠️  MODO TESTE ATIVADO (sem token)")
        print("   O sistema funcionará normalmente")
        print("   Mas não poderá acessar áreas autenticadas")
        self.token_detectado = False
        return True

# Teste
if __name__ == "__main__":
    print("="*60)
    print("🔐 TESTE DE TOKEN A3 - VERSÃO MELHORADA")
    print("="*60)
    
    manager = TokenA3Manager()
    
    # 1. Detectar middleware
    if manager.detectar_middleware():
        print(f"\n✅ Middleware: {manager.middleware_path}")
        print(f"   Fabricante: {manager.middleware_nome}")
    else:
        print("\n❌ Middleware não encontrado!")
        print("   Instale o software do token primeiro")
        sys.exit(1)
    
    # 2. Validar token
    token_ok = manager.validar_token_conectado()
    
    if not token_ok:
        print("\n⚠️  Deseja continuar no MODO TESTE? (s/n)")
        resposta = input("   > ").lower()
        
        if resposta == 's':
            manager.modo_teste_sem_token()
        else:
            print("\n❌ Conecte o token e tente novamente!")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ CONFIGURAÇÃO COMPLETA!")
    print("="*60)
