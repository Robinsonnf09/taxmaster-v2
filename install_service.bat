@echo off
echo ============================================================
echo TAX MASTER - INSTALANDO COMO SERVICO DO WINDOWS
echo ============================================================
echo.

REM Verificar se NSSM esta instalado
where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] NSSM nao encontrado!
    echo.
    echo NSSM e necessario para instalar como servico.
    echo.
    echo Para instalar:
    echo 1. Baixe NSSM de: https://nssm.cc/download
    echo 2. Extraia nssm.exe para C:\Windows\System32
    echo 3. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo [1/4] Removendo servico existente (se houver)...
nssm stop TaxMaster >nul 2>&1
nssm remove TaxMaster confirm >nul 2>&1

echo [2/4] Instalando novo servico...
set "APP_DIR=%~dp0"
set "PYTHON_EXE=%APP_DIR%venv\Scripts\python.exe"
set "APP_PY=%APP_DIR%app.py"

nssm install TaxMaster "%PYTHON_EXE%" "%APP_PY%"

echo [3/4] Configurando servico...
nssm set TaxMaster AppDirectory "%APP_DIR%"
nssm set TaxMaster DisplayName "Tax Master v2.0"
nssm set TaxMaster Description "Sistema de Gestão de Precatórios"
nssm set TaxMaster Start SERVICE_AUTO_START
nssm set TaxMaster AppStdout "%APP_DIR%logs\service_output.log"
nssm set TaxMaster AppStderr "%APP_DIR%logs\service_error.log"

echo [4/4] Iniciando servico...
nssm start TaxMaster

echo.
echo ============================================================
echo [OK] SERVICO INSTALADO COM SUCESSO!
echo ============================================================
echo.
echo O Tax Master agora rodara automaticamente como servico do Windows.
echo.
echo Comandos uteis:
echo   - Parar servico: nssm stop TaxMaster
echo   - Iniciar servico: nssm start TaxMaster
echo   - Remover servico: nssm remove TaxMaster confirm
echo.
echo Acesse: http://localhost:8080
echo.
pause
