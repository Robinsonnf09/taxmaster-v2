@echo off
chcp 65001 >nul
title INSTALAÇÃO COMPLETA - LOTOFÁCIL ULTIMATE
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     INSTALAÇÃO AUTOMÁTICA - LOTOFÁCIL ULTIMATE            ║
echo ║                  Robinson Tax Master                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 📦 Instalando dependências...
pip install numpy scipy requests beautifulsoup4 openpyxl reportlab Pillow pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências!
    pause
    exit
)
echo ✅ Dependências instaladas!
echo.

echo [2/5] 🧪 Testando conexão com API...
python teste_conexao_rapido.py
if errorlevel 1 (
    echo ⚠️ Aviso: Conexão com problemas, mas continuando...
)
echo.

echo [3/5] 🔨 Compilando aplicação...
python -m PyInstaller --clean --noconfirm --windowed ^
  --icon=icone_trevo.ico ^
  --name=LotofacilULTIMATE ^
  --collect-data setuptools ^
  --collect-data scipy ^
  --hidden-import=scipy.special.cython_special ^
  --hidden-import=pkg_resources.extern ^
  --hidden-import=numpy.core._dtype_ctypes ^
  lotofacil_ultimate_final.py

if errorlevel 1 (
    echo ❌ Erro na compilação!
    pause
    exit
)
echo ✅ Compilação OK!
echo.

echo [4/5] ✅ Criando atalhos...
if exist "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe" (
    powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Lotofacil ULTIMATE.lnk'); $SC.TargetPath = '%CD%\dist\LotofacilULTIMATE\LotofacilULTIMATE.exe'; $SC.Save()"
    echo ✅ Atalho criado na Área de Trabalho!
) else (
    echo ❌ Executável não encontrado!
)
echo.

echo [5/5] 🚀 Iniciando aplicação...
timeout /t 2 >nul
start "" "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe"
start explorer "dist\LotofacilULTIMATE"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║            ✅ INSTALAÇÃO COMPLETA!                        ║
echo ║                                                            ║
echo ║  📁 Executável: dist\LotofacilULTIMATE\                   ║
echo ║  🖥️ Atalho criado na Área de Trabalho                    ║
echo ║  🚀 Aplicação iniciada automaticamente                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause