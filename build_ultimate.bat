@echo off
chcp 65001 >nul
title LOTOFÁCIL ULTIMATE PRO - BUILD
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║       LOTOFÁCIL QUANTUM ULTIMATE PRO - BUILD              ║
echo ║               Robinson Tax Master                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/8] 🔍 Verificando Python...
python --version
if errorlevel 1 (
    echo ❌ Python não encontrado!
    pause
    exit
)
echo ✅ Python OK!
echo.

echo [2/8] 📦 Atualizando pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip OK!
echo.

echo [3/8] 📚 Instalando dependências ULTIMATE...
pip install numpy scipy requests beautifulsoup4 openpyxl reportlab Pillow pyinstaller --quiet
echo ✅ Dependências instaladas!
echo.

echo [4/8] 🛑 Encerrando processos...
taskkill /F /IM LotofacilULTIMATE.exe 2>nul
timeout /t 1 >nul
echo ✅ Processos encerrados!
echo.

echo [5/8] 🗑️ Limpando...
if exist dist rd /s /q dist
if exist build rd /s /q build
if exist *.spec del /f /q *.spec
echo ✅ Limpo!
echo.

echo [6/8] 🔨 Gerando executável ULTIMATE (3-5 min)...
echo.
python -m PyInstaller --clean --noconfirm --windowed --icon=icone_trevo.ico --name=LotofacilULTIMATE --collect-data setuptools --collect-data scipy --hidden-import=scipy.special.cython_special --hidden-import=pkg_resources.extern --hidden-import=numpy.core._dtype_ctypes lotofacil_ultimate.py

echo.
if errorlevel 1 (
    echo ❌ Erro no build!
    pause
    exit
)
echo ✅ Build OK!
echo.

echo [7/8] ✅ Verificando...
if exist "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe" (
    echo ✅ Executável criado!
    start explorer "dist\LotofacilULTIMATE"
) else (
    echo ❌ Erro!
    pause
    exit
)

echo.
echo [8/8] 🚀 Iniciando...
timeout /t 2 >nul
start "" "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                ✅ BUILD ULTIMATE COMPLETO!                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause