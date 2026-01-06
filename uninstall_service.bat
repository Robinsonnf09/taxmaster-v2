@echo off
echo ============================================================
echo TAX MASTER - REMOVENDO SERVICO
echo ============================================================
echo.

echo Parando servico...
nssm stop TaxMaster

echo Removendo servico...
nssm remove TaxMaster confirm

echo.
echo [OK] Servico removido!
echo.
pause
