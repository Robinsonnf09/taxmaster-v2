param(
    [Parameter(Mandatory=$true)]
    [string]$Tribunal,
    
    [Parameter(Mandatory=$false)]
    [string]$ApiKey = "",
    
    [Parameter(Mandatory=$false)]
    [string]$NumeroProcesso = "",
    
    [Parameter(Mandatory=$false)]
    [string]$CPF = "",
    
    [Parameter(Mandatory=$false)]
    [string]$NomeParte = ""
)

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CONSULTA DE PROCESSOS - $Tribunal" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

if ([string]::IsNullOrEmpty($ApiKey)) {
    Write-Host ""
    Write-Host "ERRO: API Key é obrigatória para consultas!" -ForegroundColor Red
    Write-Host "Use: -ApiKey 'SUA_CHAVE_AQUI'" -ForegroundColor Yellow
    exit 1
}

$url = "https://api-publica.datajud.cnj.jus.br/api_publica_$($Tribunal.ToLower())/_search"

$query = @{}

if (-not [string]::IsNullOrEmpty($NumeroProcesso)) {
    Write-Host "Buscando processo: $NumeroProcesso" -ForegroundColor White
    $numeroLimpo = $NumeroProcesso -replace '[^0-9]', ''
    $query = @{
        "match" = @{
            "numeroProcesso" = $numeroLimpo
        }
    }
}
elseif (-not [string]::IsNullOrEmpty($CPF)) {
    Write-Host "Buscando por CPF: $CPF" -ForegroundColor White
    $cpfLimpo = $CPF -replace '[^0-9]', ''
    $query = @{
        "match" = @{
            "cpfCnpjPartes" = $cpfLimpo
        }
    }
}
elseif (-not [string]::IsNullOrEmpty($NomeParte)) {
    Write-Host "Buscando por nome: $NomeParte" -ForegroundColor White
    $query = @{
        "match" = @{
            "nomePartes" = $NomeParte
        }
    }
}
else {
    Write-Host "ERRO: Especifique ao menos um critério de busca!" -ForegroundColor Red
    Write-Host "  -NumeroProcesso '0000000-00.0000.0.00.0000'" -ForegroundColor Yellow
    Write-Host "  -CPF '000.000.000-00'" -ForegroundColor Yellow
    Write-Host "  -NomeParte 'NOME DA PESSOA'" -ForegroundColor Yellow
    exit 1
}

$body = @{
    "query" = $query
    "size" = 50
} | ConvertTo-Json -Depth 10

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "APIKey $ApiKey"
}

try {
    Write-Host "Consultando API..." -ForegroundColor Gray
    
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -TimeoutSec 30
    
    if ($response.hits.hits.Count -eq 0) {
        Write-Host ""
        Write-Host "Nenhum processo encontrado com os critérios informados." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host ""
    Write-Host "✓ Encontrados $($response.hits.hits.Count) processo(s)!" -ForegroundColor Green
    Write-Host ""
    
    $processos = @()
    
    foreach ($hit in $response.hits.hits) {
        $processo = $hit._source
        
        Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "Processo: $($processo.numeroProcesso)" -ForegroundColor White
        Write-Host "  Classe: $($processo.classe.nome)" -ForegroundColor Gray
        Write-Host "  Assunto: $($processo.assuntos[0].nome)" -ForegroundColor Gray
        Write-Host "  Órgão: $($processo.orgaoJulgador.nome)" -ForegroundColor Gray
        
        $processos += [PSCustomObject]@{
            NumeroProcesso = $processo.numeroProcesso
            Classe = $processo.classe.nome
            Assunto = $processo.assuntos[0].nome
            OrgaoJulgador = $processo.orgaoJulgador.nome
            DataAjuizamento = $processo.dataAjuizamento
            Tribunal = $Tribunal
        }
    }
    
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $jsonPath = Join-Path (Get-Location) "resultados\processos_${Tribunal}_${timestamp}.json"
    $csvPath = Join-Path (Get-Location) "resultados\processos_${Tribunal}_${timestamp}.csv"
    
    $response | ConvertTo-Json -Depth 20 | Out-File -FilePath $jsonPath -Encoding UTF8
    $processos | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
    
    Write-Host ""
    Write-Host "Arquivos salvos:" -ForegroundColor Green
    Write-Host "  → JSON: $jsonPath" -ForegroundColor Gray
    Write-Host "  → CSV: $csvPath" -ForegroundColor Gray
}
catch {
    Write-Host ""
    Write-Host "ERRO na consulta: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
