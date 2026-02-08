param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey = "",
    
    [Parameter(Mandatory=$false)]
    [string[]]$Tribunais = @("TJGO", "TJSP")
)

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TESTE DE CONECTIVIDADE - API DataJud CNJ" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

if ([string]::IsNullOrEmpty($ApiKey)) {
    Write-Host ""
    Write-Host "AVISO: Nenhuma API Key fornecida. Testando apenas conectividade..." -ForegroundColor Yellow
    Write-Host ""
}

$results = @()

foreach ($tribunal in $Tribunais) {
    Write-Host ""
    Write-Host "Testando $tribunal..." -ForegroundColor White
    
    $url = "https://api-publica.datajud.cnj.jus.br/api_publica_$($tribunal.ToLower())/_search"
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if (-not [string]::IsNullOrEmpty($ApiKey)) {
            $headers["Authorization"] = "APIKey $ApiKey"
        }
        
        $body = @{
            "query" = @{
                "match_all" = @{}
            }
            "size" = 1
        } | ConvertTo-Json
        
        $startTime = Get-Date
        
        try {
            $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -TimeoutSec 10
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalMilliseconds
            
            Write-Host "  ✓ Conectado com sucesso!" -ForegroundColor Green
            Write-Host "  → Tempo de resposta: $([math]::Round($duration, 2))ms" -ForegroundColor Gray
            
            $results += [PSCustomObject]@{
                Tribunal = $tribunal
                Status = "Conectado"
                TempoResposta = "$([math]::Round($duration, 2))ms"
                URL = $url
            }
        }
        catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            $errorMsg = $_.Exception.Message
            
            if ($statusCode -eq 401) {
                Write-Host "  ✗ Erro 401: API Key inválida ou não fornecida" -ForegroundColor Red
                $status = "API Key Inválida"
            }
            elseif ($statusCode -eq 404) {
                Write-Host "  ✗ Erro 404: Tribunal não encontrado" -ForegroundColor Red
                $status = "Não Encontrado"
            }
            else {
                Write-Host "  ✗ Erro: $errorMsg" -ForegroundColor Red
                $status = "Erro de Conexão"
            }
            
            $results += [PSCustomObject]@{
                Tribunal = $tribunal
                Status = $status
                TempoResposta = "N/A"
                URL = $url
            }
        }
    }
    catch {
        Write-Host "  ✗ Falha na conexão: $($_.Exception.Message)" -ForegroundColor Red
        
        $results += [PSCustomObject]@{
            Tribunal = $tribunal
            Status = "Falha de Conexão"
            TempoResposta = "N/A"
            URL = $url
        }
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  RESUMO DOS TESTES" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
$results | Format-Table -AutoSize

$reportPath = Join-Path (Get-Location) "dados\logs\teste_api_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$results | ConvertTo-Json | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "Relatório salvo em: $reportPath" -ForegroundColor Green
