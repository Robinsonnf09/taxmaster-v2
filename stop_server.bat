@echo off
echo ============================================================
echo TAX MASTER - PARANDO SERVIDOR
echo ============================================================
echo.
echo Parando todos os processos Python...

taskkill /F /IM pythonw.exe
taskkill /F /IM python.exe

echo.
echo [OK] Servidor parado!
echo.
pause
