@echo off
title Instalador Automático - Sistema Lotofácil Robinson
color 0D

echo ================================================
echo     SISTEMA LOTOFACIL - INSTALACAO AUTOMATICA
echo ================================================
echo.

echo Verificando Python...
py --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado.
    echo Instale o Python antes de continuar.
    pause
    exit
)

echo.
echo Instalando dependencias...
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m pip install openpyxl
py -m pip install reportlab

echo.
echo Dependencias instaladas com sucesso.
echo.

echo Verificando arquivos necessarios...
if not exist "lotofacil_sistema.py" (
    echo ERRO: Arquivo lotofacil_sistema.py nao encontrado.
    pause
    exit
)

if not exist "icone_trevo.ico" (
    echo ERRO: Arquivo icone_trevo.ico nao encontrado.
    pause
    exit
)

if not exist "splash.png" (
    echo ERRO: Arquivo splash.png nao encontrado.
    pause
    exit
)

echo Todos os arquivos foram encontrados.
echo.

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist lotofacil_sistema.spec del lotofacil_sistema.spec

echo.
echo Gerando EXE profissional...
py -m PyInstaller --noconfirm --windowed --icon=icone_trevo.ico --splash=splash.png lotofacil_sistema.py

echo.
echo EXE gerado com sucesso!
echo.

echo Criando atalho de execucao rapida...
(
echo @echo off
echo cd /d "%%~dp0dist\lotofacil_sistema"
echo start "" "lotofacil_sistema.exe"
echo exit
) > rodar_lotofacil.bat

echo Atalho criado: rodar_lotofacil.bat
echo.

echo Abrindo o programa...
start "" "dist\lotofacil_sistema\lotofacil_sistema.exe"

echo.
echo Instalacao concluida com sucesso!
echo Pressione qualquer tecla para sair.
pause >nul
exit