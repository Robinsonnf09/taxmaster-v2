@echo off
echo ============================================================
echo TAX MASTER - CONFIGURANDO INICIALIZACAO AUTOMATICA
echo ============================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "APP_DIR=%~dp0"
set "SHORTCUT=%STARTUP_FOLDER%\TaxMaster.lnk"

echo Criando atalho na pasta de inicializacao...

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%APP_DIR%start_background.bat'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.IconLocation = 'shell32.dll,21'; $Shortcut.Save()"

echo.
echo [OK] Inicializacao automatica configurada!
echo.
echo O Tax Master sera iniciado automaticamente quando o Windows iniciar.
echo.
echo Para DESABILITAR, delete o arquivo:
echo %SHORTCUT%
echo.
pause
