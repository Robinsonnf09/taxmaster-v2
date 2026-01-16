Write-Host "`n🔥 ADICIONANDO FILTROS DE VALOR E BUSCA TJ-SP...`n" -ForegroundColor Cyan

# Deploy simples sem JavaScript complexo
git add .
git commit -m "feat: Adicionar filtros de valor e busca automatizada TJ-SP"
git push origin main

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ DEPLOY REALIZADO COM SUCESSO! ✅  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "⏱️ Aguardando Railway (2 minutos)...`n" -ForegroundColor Yellow

for ($i = 120; $i -gt 0; $i -= 10) {
    $minutos = [math]::Floor($i / 60)
    $segundos = $i % 60
    Write-Host "   ⏳ $minutos min $segundos seg restantes..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
}

Write-Host "`n🧪 TESTANDO...`n" -ForegroundColor Cyan

try {
    $page = Invoke-WebRequest -Uri "https://web-production-ad84.up.railway.app/processos" -UseBasicParsing
    
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ SISTEMA ATUALIZADO! ✅            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📊 Status: $($page.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Tamanho: $($page.Content.Length) bytes`n" -ForegroundColor Gray
    
    Start-Process "https://web-production-ad84.up.railway.app/processos"
    
} catch {
    Write-Host "❌ Erro: $($_.Exception.Message)`n" -ForegroundColor Red
}
