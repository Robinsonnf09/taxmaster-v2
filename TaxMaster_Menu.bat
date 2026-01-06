@echo off
:menu
cls
echo ============================================================
echo        TAX MASTER v2.0 - MENU DE GERENCIAMENTO
echo ============================================================
echo.
echo  1. Iniciar servidor em BACKGROUND (sem janela)
echo  2. Iniciar servidor NORMAL (com janela)
echo  3. Parar servidor
echo  4. Verificar STATUS do servidor
echo  5. Abrir navegador (http://localhost:8080)
echo.
echo  6. Instalar como SERVICO do Windows
echo  7. Desinstalar servico
echo  8. Habilitar inicializacao automatica
echo  9. Criar atalho na area de trabalho
echo.
echo  0. SAIR
echo.
echo ============================================================
echo.
set /p opcao="Escolha uma opcao (0-9): "

if "%opcao%"=="1" goto start_background
if "%opcao%"=="2" goto start_normal
if "%opcao%"=="3" goto stop
if "%opcao%"=="4" goto status
if "%opcao%"=="5" goto open_browser
if "%opcao%"=="6" goto install_service
if "%opcao%"=="7" goto uninstall_service
if "%opcao%"=="8" goto enable_autostart
if "%opcao%"=="9" goto create_shortcut
if "%opcao%"=="0" exit
goto menu

:start_background
cls
echo Iniciando em background...
call start_background.bat
pause
goto menu

:start_normal
cls
echo Iniciando servidor normal...
echo.
echo Pressione Ctrl+C para parar o servidor
echo.
python app.py
goto menu

:stop
cls
echo Parando servidor...
call stop_server.bat
goto menu

:status
cls
call status_server.bat
goto menu

:open_browser
start http://localhost:8080
goto menu

:install_service
cls
call install_service.bat
goto menu

:uninstall_service
cls
call uninstall_service.bat
goto menu

:enable_autostart
cls
call enable_autostart.bat
goto menu

:create_shortcut
cls
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
pause
goto menu
