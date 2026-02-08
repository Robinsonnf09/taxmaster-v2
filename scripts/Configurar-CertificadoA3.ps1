param([switch]$Force)

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CONFIGURADOR DE CERTIFICADO A3" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$certs = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.HasPrivateKey -eq $true }

$i = 1
$certList = @()
foreach ($cert in $certs) {
    $subject = $cert.Subject -replace "CN=", "" -split "," | Select-Object -First 1
    Write-Host "$i. $subject" -ForegroundColor Gray
    Write-Host "   Emissor: $($cert.Issuer -replace '.*OU=', '' -replace ',.*', '')" -ForegroundColor DarkGray
    Write-Host ""
    $certList += $cert
    $i++
}

Write-Host "Digite o número do certificado [1-$($certList.Count)] ou ENTER para TAX MASTER:" -ForegroundColor Yellow
$escolha = Read-Host

if ([string]::IsNullOrEmpty($escolha)) {
    $certEscolhido = $certList | Where-Object { $_.Subject -like "*TAX MASTER*" } | Select-Object -First 1
    if (-not $certEscolhido) { $certEscolhido = $certList[0] }
} else {
    $certEscolhido = $certList[$escolha - 1]
}

Write-Host ""
Write-Host "✅ Certificado selecionado:" -ForegroundColor Green
Write-Host "   $($certEscolhido.Subject)" -ForegroundColor White

$config = @{
    Thumbprint = $certEscolhido.Thumbprint
    Subject = $certEscolhido.Subject
    DataConfig = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$config | ConvertTo-Json | Out-File -FilePath ".\dados\certificado_config.json" -Encoding UTF8

Write-Host ""
Write-Host "✅ Configuração salva!" -ForegroundColor Green
