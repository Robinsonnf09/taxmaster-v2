param(
    [Parameter(Mandatory=$true)]
    [string]$ArquivoExcel
)

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DOWNLOAD DE OFÍCIOS REQUISITÓRIOS" -ForegroundColor Yellow
Write-Host "  TJSP ESAJ" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivo
if (-not (Test-Path $ArquivoExcel)) {
    Write-Host "❌ Arquivo não encontrado: $ArquivoExcel" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Arquivo: $ArquivoExcel" -ForegroundColor White
Write-Host ""

# Criar pasta de destino
if (-not (Test-Path ".\oficios_pdf")) {
    New-Item -ItemType Directory -Path ".\oficios_pdf" | Out-Null
    Write-Host "✅ Pasta criada: oficios_pdf" -ForegroundColor Green
}

# Executar Python
Write-Host "🚀 Iniciando download..." -ForegroundColor Yellow
Write-Host ""

python ".\scripts\Baixar-Oficios-TJSP.py" $ArquivoExcel

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Ofícios salvos em: oficios_pdf\" -ForegroundColor White
Write-Host "📊 Relatório em: resultados\relatorio_oficios_*.json" -ForegroundColor White
Write-Host ""

# Abrir pasta
Write-Host "Abrir pasta de ofícios? (S/N)" -ForegroundColor Yellow
$resposta = Read-Host

if ($resposta -eq "S" -or $resposta -eq "s") {
    Start-Process ".\oficios_pdf"
}
