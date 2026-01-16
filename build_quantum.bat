@echo off
chcp 65001 >nul
title LOTOFÁCIL QUANTUM - BUILD AUTOMATIZADO
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          LOTOFÁCIL QUANTUM - BUILD AUTOMATIZADO           ║
echo ║                    Robinson Tax Master                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: ============================================================
:: ETAPA 1: Verificação do Python
:: ============================================================
echo [1/8] 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo Instale Python em: https://www.python.org/downloads/
    echo Marque a opção "Add Python to PATH" durante instalação
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado!
echo.

:: ============================================================
:: ETAPA 2: Atualizar pip
:: ============================================================
echo [2/8] 📦 Atualizando pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip atualizado!
echo.

:: ============================================================
:: ETAPA 3: Instalar dependências
:: ============================================================
echo [3/8] 📚 Instalando dependências...
echo.
echo Instalando numpy...
pip install numpy --quiet
echo ✅ numpy

echo Instalando scipy...
pip install scipy --quiet
echo ✅ scipy

echo Instalando requests...
pip install requests --quiet
echo ✅ requests

echo Instalando beautifulsoup4...
pip install beautifulsoup4 --quiet
echo ✅ beautifulsoup4

echo Instalando openpyxl...
pip install openpyxl --quiet
echo ✅ openpyxl

echo Instalando reportlab...
pip install reportlab --quiet
echo ✅ reportlab

echo Instalando Pillow...
pip install Pillow --quiet
echo ✅ Pillow

echo Instalando pyinstaller...
pip install pyinstaller --quiet
echo ✅ pyinstaller

echo.
echo ✅ Todas as dependências instaladas!
echo.

:: ============================================================
:: ETAPA 4: Encerrar processos
:: ============================================================
echo [4/8] 🛑 Encerrando processos antigos...
taskkill /F /IM LotofacilQUANTUM.exe 2>nul
timeout /t 1 >nul
echo ✅ Processos encerrados!
echo.

:: ============================================================
:: ETAPA 5: Limpar pastas antigas
:: ============================================================
echo [5/8] 🗑️ Limpando pastas antigas...
if exist dist rd /s /q dist
if exist build rd /s /q build
if exist *.spec del /f /q *.spec
echo ✅ Pastas limpas!
echo.

:: ============================================================
:: ETAPA 6: Gerar executável
:: ============================================================
echo [6/8] 🔨 Gerando executável...
echo.
echo ⏳ Isso pode levar 2-5 minutos dependendo do seu computador...
echo.

python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --windowed ^
  --onedir ^
  --icon=icone_trevo.ico ^
  --name=LotofacilQUANTUM ^
  --collect-data setuptools ^
  --collect-data scipy ^
  --hidden-import=scipy.special.cython_special ^
  --hidden-import=pkg_resources.extern ^
  --hidden-import=numpy.core._dtype_ctypes ^
  --hidden-import=scipy._lib.messagestream ^
  --exclude-module=matplotlib ^
  --exclude-module=pandas ^
  --exclude-module=IPython ^
  lotofacil_quantum.py

echo.
if errorlevel 1 (
    echo ❌ ERRO no build!
    echo.
    echo Verifique os logs acima para detalhes.
    pause
    exit /b 1
)

echo ✅ Build concluído!
echo.

:: ============================================================
:: ETAPA 7: Verificar resultado
:: ============================================================
echo [7/8] ✅ Verificando resultado...
echo.

if not exist "dist\LotofacilQUANTUM\LotofacilQUANTUM.exe" (
    echo ❌ ERRO: Executável não foi criado!
    pause
    exit /b 1
)

echo ✅ Executável criado com sucesso!
echo.
echo 📁 Localização: dist\LotofacilQUANTUM\
echo 📦 Arquivo: LotofacilQUANTUM.exe
echo.

:: Calcular tamanho
for /f "tokens=3" %%a in ('dir /s "dist\LotofacilQUANTUM" ^| find "bytes"') do set size=%%a
echo 💾 Tamanho aproximado: %size% bytes
echo.

:: ============================================================
:: ETAPA 8: Executar automaticamente
:: ============================================================
echo [8/8] 🚀 Iniciando aplicação...
echo.

timeout /t 2 >nul

start "" "dist\LotofacilQUANTUM\LotofacilQUANTUM.exe"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                   ✅ BUILD CONCLUÍDO!                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Aplicação iniciada com sucesso!
echo.
echo 📂 Abrindo pasta...
timeout /t 1 >nul
start "" explorer "dist\LotofacilQUANTUM"

echo.
echo Pressione qualquer tecla para fechar...
pause >nul