Write-Host "Instalando Microsoft Edge WebDriver..." -ForegroundColor Cyan

# Criar diretorio
New-Item -Path "C:\WebDriver" -ItemType Directory -Force | Out-Null

# Detectar versao do Edge
$edgePaths = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

$edgePath = $edgePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($edgePath) {
    $edgeVersion = (Get-Item $edgePath).VersionInfo.FileVersion
    Write-Host "Versao do Edge detectada: $edgeVersion" -ForegroundColor Green
    
    # Baixar WebDriver
    $driverUrl = "https://msedgedriver.azureedge.net/$edgeVersion/edgedriver_win64.zip"
    $zipPath = "$env:TEMP\edgedriver.zip"
    
    Write-Host "Baixando WebDriver..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $driverUrl -OutFile $zipPath
    
    Write-Host "Extraindo arquivos..." -ForegroundColor Yellow
    Expand-Archive -Path $zipPath -DestinationPath "C:\WebDriver" -Force
    Remove-Item $zipPath
    
    Write-Host "[OK] Edge WebDriver instalado em C:\WebDriver\msedgedriver.exe" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Microsoft Edge nao encontrado" -ForegroundColor Red
}

Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
