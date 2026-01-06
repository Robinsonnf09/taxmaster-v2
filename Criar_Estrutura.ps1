Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     CRIANDO ESTRUTURA DO TAXMASTER CRM                    " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$baseDir = "C:\TAX_MASTER_DEV\tax_master_static"

# Criar estrutura de pastas
$folders = @(
    "robots",
    "src",
    "config",
    "data",
    "logs",
    "backups",
    "scripts",
    "dashboard"
)

Write-Host "`nCriando estrutura de pastas..." -ForegroundColor Yellow
foreach ($folder in $folders) {
    $path = Join-Path $baseDir $folder
    New-Item -Path $path -ItemType Directory -Force | Out-Null
    Write-Host "[OK] Criado: $folder" -ForegroundColor Green
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "     ESTRUTURA CRIADA COM SUCESSO!                         " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Vou gerar os arquivos de configuracao" -ForegroundColor White
Write-Host "2. Vou criar os robos de coleta" -ForegroundColor White
Write-Host "3. Vou criar o dashboard" -ForegroundColor White
Write-Host "4. Vou criar os scripts de execucao" -ForegroundColor White

Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
