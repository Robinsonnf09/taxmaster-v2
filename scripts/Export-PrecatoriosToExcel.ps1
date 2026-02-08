param(
    [Parameter(Mandatory=$true)]
    [string]$JsonPath,
    
    [Parameter(Mandatory=$false)]
    [string]$ExcelPath = ".\Controle_Precatorios.xlsx"
)

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  IMPORTAÇÃO PARA EXCEL" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

if (-not (Test-Path $JsonPath)) {
    Write-Host "ERRO: Arquivo JSON não encontrado: $JsonPath" -ForegroundColor Red
    exit 1
}

Write-Host "Lendo arquivo JSON..." -ForegroundColor White
$dados = Get-Content $JsonPath -Raw | ConvertFrom-Json

if (-not $dados.hits -or $dados.hits.hits.Count -eq 0) {
    Write-Host "Nenhum processo encontrado no arquivo JSON." -ForegroundColor Yellow
    exit 0
}

Write-Host "Processando $($dados.hits.hits.Count) processo(s)..." -ForegroundColor White

$processos = @()

foreach ($hit in $dados.hits.hits) {
    $p = $hit._source
    
    $processos += [PSCustomObject]@{
        'Número do Processo' = $p.numeroProcesso
        'Tribunal' = $p.tribunal
        'Classe' = $p.classe.nome
        'Assunto' = $p.assuntos[0].nome
        'Órgão Julgador' = $p.orgaoJulgador.nome
        'Data de Ajuizamento' = $p.dataAjuizamento
        'Valor da Causa' = if ($p.valorCausa) { "R$ $($p.valorCausa)" } else { "N/A" }
        'Status' = 'ATIVO'
    }
}

if (Get-Module -ListAvailable -Name ImportExcel) {
    Write-Host "Exportando para Excel..." -ForegroundColor White
    Import-Module ImportExcel
    $processos | Export-Excel -Path $ExcelPath -WorksheetName "CADASTRO" -AutoSize -TableName "Precatorios" -TableStyle Medium2
    Write-Host "✓ Dados exportados para: $ExcelPath" -ForegroundColor Green
}
else {
    Write-Host "Módulo ImportExcel não instalado. Exportando como CSV..." -ForegroundColor Yellow
    $csvPath = $ExcelPath -replace '\.xlsx$', '.csv'
    $processos | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
    Write-Host "✓ Dados exportados para: $csvPath" -ForegroundColor Green
}
