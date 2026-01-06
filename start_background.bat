@echo off
echo ============================================================
echo TAX MASTER - INICIANDO EM BACKGROUND
echo ============================================================
echo.
echo Iniciando servidor em segundo plano...
echo O servidor continuara rodando mesmo se voce fechar esta janela.
echo.

REM Matar processos Python existentes (opcional)
REM taskkill /F /IM pythonw.exe >nul 2>&1

REM Iniciar servidor em background usando pythonw
start "" pythonw app.py

echo.
echo [OK] Servidor iniciado em background!
echo.
echo Para acessar: http://localhost:8080
echo.
echo Para PARAR o servidor, execute: stop_server.bat
echo.
timeout /t 3 >nul
exit
