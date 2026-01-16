@echo off
title RECOMPILAR LIMPO
color 0E

echo ╔════════════════════════════════════════════════════════════╗
echo ║            RECOMPILAÇÃO LIMPA - LOTOFÁCIL                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 🛑 Matando processos...
taskkill /F /IM LotofacilULTIMATE.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul
echo ✅ Processos encerrados!
echo.

echo [2/5] 🗑️ Removendo pastas antigas...
if exist dist rd /s /q dist
if exist build rd /s /q build
if exist __pycache__ rd /s /q __pycache__
if exist *.spec del /f /q *.spec
timeout /t 1 >nul
echo ✅ Pastas removidas!
echo.

echo [3/5] 🧹 Limpando cache do PyInstaller...
if exist "%LOCALAPPDATA%\pyinstaller" (
    rd /s /q "%LOCALAPPDATA%\pyinstaller"
    echo ✅ Cache limpo!
) else (
    echo ℹ️ Cache não encontrado
)
echo.

echo [4/5] ⏳ Aguardando sistema liberar arquivos...
timeout /t 3 >nul
echo ✅ Pronto!
echo.

echo [5/5] 🔨 Compilando...
python -m PyInstaller --clean --noconfirm --windowed ^
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

echo.
echo ✅ COMPILAÇÃO CONCLUÍDA!
echo.

if exist "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe" (
    echo 🚀 Iniciando aplicação...
    timeout /t 2 >nul
    start "" "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe"
    start explorer "dist\LotofacilULTIMATE"
) else (
    echo ❌ Executável não criado!
)

pause