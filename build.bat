@echo off
title LOTOFÁCIL QUANTUM - BUILD ULTIMATE
color 0B

:: Instalar psutil se não existir
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Instalando psutil...
    python -m pip install psutil colorama --quiet
)

:: Executar build manager
python build_manager.py

pause