@echo off
echo ============================================================
echo TAX MASTER - STATUS DO SERVIDOR
echo ============================================================
echo.

echo Verificando processos Python...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Servidor Python RODANDO
    tasklist /FI "IMAGENAME eq python.exe"
) else (
    echo [INFO] Servidor Python NAO esta rodando
)

echo.
echo Verificando processos PythonW...
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Servidor PythonW RODANDO (background)
    tasklist /FI "IMAGENAME eq pythonw.exe"
) else (
    echo [INFO] Servidor PythonW NAO esta rodando
)

echo.
echo Verificando se servidor responde...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080' -TimeoutSec 3 -UseBasicParsing; Write-Host '[OK] Servidor ONLINE - Status:' $response.StatusCode -ForegroundColor Green } catch { Write-Host '[ERRO] Servidor OFFLINE ou nao responde' -ForegroundColor Red }"

echo.
echo Verificando servico TaxMaster...
sc query TaxMaster >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [OK] Servico TaxMaster INSTALADO
    sc query TaxMaster
) else (
    echo [INFO] Servico TaxMaster NAO instalado
)

echo.
echo ============================================================
pause
