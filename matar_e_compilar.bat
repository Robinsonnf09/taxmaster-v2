@echo off
title MATADOR E COMPILADOR
color 0C

echo ╔════════════════════════════════════════════════════════════╗
echo ║         MATANDO PROCESSOS E RECOMPILANDO                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/6] 🔫 Matando processos Lotofacil...
taskkill /F /IM LotofacilULTIMATE.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo ✅ Processos mortos!
echo.

echo [2/6] ⏳ Aguardando sistema liberar arquivos...
timeout /t 5 /nobreak >nul
echo ✅ Aguardou 5 segundos!
echo.

echo [3/6] 🗑️ Removendo pastas (tentativa 1)...
rd /s /q dist 2>nul
rd /s /q build 2>nul
rd /s /q __pycache__ 2>nul
del /f /q *.spec 2>nul
echo ✅ Tentativa 1 completa!
echo.

echo [4/6] ⏳ Aguardando mais um pouco...
timeout /t 3 /nobreak >nul

echo [5/6] 🗑️ Removendo pastas (tentativa 2 - forçada)...
rd /s /q dist 2>nul
rd /s /q build 2>nul

if exist dist (
    echo ⚠️ Pasta dist ainda existe, mas continuando...
) else (
    echo ✅ Pasta dist removida!
)
echo.

echo [6/6] 🔨 Compilando...
python -m PyInstaller --clean --noconfirm --windowed ^
  --name=LotofacilULTIMATE ^
  --collect-data setuptools ^
  --collect-data scipy ^
  --hidden-import=scipy.special.cython_special ^
  --hidden-import=pkg_resources.extern ^
  --hidden-import=numpy.core._dtype_ctypes ^
  lotofacil_ultimate_final.py

echo.
if exist "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe" (
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║              ✅ COMPILAÇÃO BEM-SUCEDIDA!                  ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 🚀 Iniciando aplicação...
    timeout /t 2 >nul
    start "" "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe"
    start explorer "dist\LotofacilULTIMATE"
) else (
    echo ❌ ERRO: Executável não foi criado!
)

pause