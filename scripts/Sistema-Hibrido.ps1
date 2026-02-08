param(
    [Parameter(Mandatory=$true)]
    [string]$NumeroProcesso,
    
    [Parameter(Mandatory=$true)]
    [string]$Tribunal
)

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SISTEMA HÍBRIDO DE PRECATÓRIOS" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Processo: $NumeroProcesso" -ForegroundColor White
Write-Host "Tribunal: $Tribunal" -ForegroundColor White
Write-Host ""

$apiKey = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

# ETAPA 1: API DataJud
Write-Host "[1/3] Buscando na API DataJud..." -ForegroundColor Cyan

$encontradoAPI = $false
try {
    $result = .\scripts\Get-ProcessosPrecatorios.ps1 -Tribunal $Tribunal -ApiKey $apiKey -NumeroProcesso $NumeroProcesso 2>&1
    
    if ($result -notlike "*Nenhum processo encontrado*") {
        $encontradoAPI = $true
        Write-Host "  ✅ Encontrado na API DataJud!" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Não encontrado na API" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "  ⚠️  Erro na API: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# ETAPA 2: Web Scraping
Write-Host "[2/3] Executando scraping com certificado..." -ForegroundColor Cyan

try {
    python ".\scripts\scraper_tjgo_cert.py" $NumeroProcesso $Tribunal
    Write-Host "  ✅ Scraping concluído!" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠️  Scraping não disponível" -ForegroundColor Yellow
}

Write-Host ""

# ETAPA 3: Consolidar
Write-Host "[3/3] Consolidando resultados..." -ForegroundColor Cyan

$jsonFiles = Get-ChildItem ".\resultados\processos_${Tribunal}_*.json" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

if ($jsonFiles) {
    Write-Host "  ✅ Dados disponíveis!" -ForegroundColor Green
    
    $excelPath = ".\Controle_Precatorios_Hibrido.xlsx"
    
    Write-Host "  → Exportando para Excel..." -ForegroundColor Gray
    .\scripts\Export-PrecatoriosToExcel.ps1 -JsonPath $jsonFiles.FullName -ExcelPath $excelPath
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ✅ CONCLUÍDO!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Arquivo: $excelPath" -ForegroundColor White
    Write-Host ""
    
    Start-Process $excelPath
} else {
    Write-Host "  ❌ Nenhum dado encontrado" -ForegroundColor Red
}
