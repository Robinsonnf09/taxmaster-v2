# ============================================
# TAXMASTER CRM - ANALISE E PREPARACAO
# Script de Verificacao Automatica - Windows
# ============================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     TAXMASTER CRM - ANALISE DO SISTEMA WINDOWS            " -ForegroundColor Cyan
Write-Host "     Verificando configuracao e preparando ambiente...     " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Funcao para verificar comandos
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Funcao para obter versao
function Get-Version {
    param($Command, $VersionArg = "--version")
    try {
        $version = & $Command $VersionArg 2>&1 | Select-Object -First 1
        return $version
    } catch {
        return "Nao instalado"
    }
}

Write-Host "[1/10] Verificando Sistema Operacional..." -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
Write-Host "[OK] OS: $($os.Caption)" -ForegroundColor Green
Write-Host "[OK] Versao: $($os.Version)" -ForegroundColor Green
Write-Host "[OK] Arquitetura: $($os.OSArchitecture)" -ForegroundColor Green

Write-Host "`n[2/10] Verificando Memoria RAM..." -ForegroundColor Yellow
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
if ($ram -ge 8) {
    Write-Host "[OK] RAM: $ram GB (Suficiente)" -ForegroundColor Green
} elseif ($ram -ge 4) {
    Write-Host "[AVISO] RAM: $ram GB (Minimo, recomendado 8GB+)" -ForegroundColor Yellow
} else {
    Write-Host "[ERRO] RAM: $ram GB (Insuficiente, necessario minimo 4GB)" -ForegroundColor Red
}

Write-Host "`n[3/10] Verificando Espaco em Disco..." -ForegroundColor Yellow
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
if ($freeGB -ge 20) {
    Write-Host "[OK] Espaco Livre: $freeGB GB (Suficiente)" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Espaco Livre: $freeGB GB (Recomendado 20GB+)" -ForegroundColor Yellow
}

Write-Host "`n[4/10] Verificando Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pyVersion = Get-Version python
    Write-Host "[OK] Python instalado: $pyVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Python NAO instalado" -ForegroundColor Red
    Write-Host "   -> Instalando Python 3.11..." -ForegroundColor Cyan
    winget install Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
}

Write-Host "`n[5/10] Verificando pip..." -ForegroundColor Yellow
if (Test-Command pip) {
    $pipVersion = Get-Version pip
    Write-Host "[OK] pip instalado: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] pip NAO instalado" -ForegroundColor Red
    Write-Host "   -> Instalando pip..." -ForegroundColor Cyan
    python -m ensurepip --upgrade
}

Write-Host "`n[6/10] Verificando Git..." -ForegroundColor Yellow
if (Test-Command git) {
    $gitVersion = Get-Version git
    Write-Host "[OK] Git instalado: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Git NAO instalado" -ForegroundColor Red
    Write-Host "   -> Instalando Git..." -ForegroundColor Cyan
    winget install Git.Git --silent --accept-source-agreements --accept-package-agreements
}

Write-Host "`n[7/10] Verificando Node.js..." -ForegroundColor Yellow
if (Test-Command node) {
    $nodeVersion = Get-Version node
    Write-Host "[OK] Node.js instalado: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Node.js NAO instalado" -ForegroundColor Red
    Write-Host "   -> Instalando Node.js 20 LTS..." -ForegroundColor Cyan
    winget install OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
}

Write-Host "`n[8/10] Verificando Docker Desktop..." -ForegroundColor Yellow
if (Test-Command docker) {
    $dockerVersion = Get-Version docker
    Write-Host "[OK] Docker instalado: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Docker NAO instalado (Opcional, mas recomendado)" -ForegroundColor Yellow
}

Write-Host "`n[9/10] Verificando PostgreSQL..." -ForegroundColor Yellow
if (Test-Command psql) {
    $pgVersion = Get-Version psql
    Write-Host "[OK] PostgreSQL instalado: $pgVersion" -ForegroundColor Green
} else {
    Write-Host "[AVISO] PostgreSQL NAO instalado" -ForegroundColor Yellow
}

Write-Host "`n[10/10] Verificando Microsoft Edge WebDriver..." -ForegroundColor Yellow
$edgeDriverPath = "C:\WebDriver\msedgedriver.exe"
if (Test-Path $edgeDriverPath) {
    Write-Host "[OK] Edge WebDriver instalado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Edge WebDriver NAO encontrado em C:\WebDriver" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "                  RESUMO DA ANALISE                         " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n[EXTRA] Instalando dependencias Python..." -ForegroundColor Yellow
$requirements = @(
    "selenium",
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pandas",
    "openpyxl",
    "python-dotenv",
    "requests",
    "beautifulsoup4",
    "lxml",
    "cryptography",
    "pydantic",
    "playwright"
)

Write-Host "Instalando pacotes Python necessarios..." -ForegroundColor Cyan
foreach ($package in $requirements) {
    Write-Host "  -> Instalando $package..." -NoNewline
    try {
        pip install $package --quiet --disable-pip-version-check 2>&1 | Out-Null
        Write-Host " [OK]" -ForegroundColor Green
    } catch {
        Write-Host " [ERRO]" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "              ANALISE CONCLUIDA!                            " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Revise os itens marcados como [ERRO] ou [AVISO]" -ForegroundColor White
Write-Host "2. Instale manualmente o que estiver faltando" -ForegroundColor White
Write-Host "3. Execute novamente para confirmar" -ForegroundColor White

Write-Host "`nPressione qualquer tecla para sair..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
