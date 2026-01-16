@echo off
chcp 65001 >nul
title INSTALAÇÃO CORRIGIDA - LOTOFÁCIL ULTIMATE
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     INSTALAÇÃO AUTOMÁTICA - LOTOFÁCIL ULTIMATE            ║
echo ║                  Robinson Tax Master                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 📦 Instalando dependências (pode demorar 2-3 min)...
python -m pip install --upgrade pip
python -m pip install numpy scipy requests beautifulsoup4 openpyxl reportlab Pillow pyinstaller --upgrade

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências!
    echo.
    echo Tente instalar manualmente:
    echo python -m pip install numpy scipy requests beautifulsoup4 openpyxl reportlab Pillow pyinstaller
    pause
    exit
)
echo ✅ Dependências instaladas!
echo.

echo [2/5] 🧪 Testando conexão com API...
if exist teste_conexao_rapido.py (
    python teste_conexao_rapido.py
) else (
    echo⚠️ Arquivo teste_conexao_rapido.py não encontrado, pulando...
)
echo.

echo [3/5] 🔨 Compilando aplicação (pode demorar 3-5 min)...
if not exist lotofacil_ultimate_final.py (
    echo ❌ ERRO: lotofacil_ultimate_final.py não encontrado!
    echo.
    echo Certifique-se que os arquivos estão na pasta:
    echo - lotofacil_ultimate_final.py
    echo - teste_conexao_rapido.py
    pause
    exit
)

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
echo ✅ Compilação OK!
echo.

echo [4/5] ✅ Criando atalhos...
if exist "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe" (
    powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Lotofacil ULTIMATE.lnk'); $SC.TargetPath = '%CD%\dist\LotofacilULTIMATE\LotofacilULTIMATE.exe'; $SC.Save()"
    echo ✅ Atalho criado na Área de Trabalho!
) else (
    echo ⚠️ Executável não encontrado!
)
echo.

echo [5/5] 🚀 Iniciando aplicação...
if exist "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe" (
    timeout /t 2 >nul
    start "" "dist\LotofacilULTIMATE\LotofacilULTIMATE.exe"
    start explorer "dist\LotofacilULTIMATE"
) else (
    echo ❌ Executável não foi criado!
    pause
    exit
)

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