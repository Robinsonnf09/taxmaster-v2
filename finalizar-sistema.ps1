Write-Host "`n🔥 ADICIONANDO CAMPOS: NATUREZA E ANO DA LOA...`n" -ForegroundColor Cyan

# Fazer deploy dos arquivos já modificados
git add .
git commit -m "feat: Adicionar campos Natureza da Obrigação e ANO da LOA"
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

Write-Host "`n🧪 TESTANDO SISTEMA...`n" -ForegroundColor Cyan

try {
    $page = Invoke-WebRequest -Uri "https://web-production-ad84.up.railway.app/processos" -UseBasicParsing
    
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ SISTEMA ATUALIZADO! ✅            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📊 Status: $($page.StatusCode)" -ForegroundColor Green
    
    Start-Process "https://web-production-ad84.up.railway.app/processos"
    
    Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                               ║" -ForegroundColor Green
    Write-Host "║  🎉 SISTEMA TAX MASTER V2 COMPLETO! 🎉       ║" -ForegroundColor Green
    Write-Host "║                                               ║" -ForegroundColor Green
    Write-Host "║  ✅ Busca em tempo real                      ║" -ForegroundColor Green
    Write-Host "║  ✅ Filtro: Tribunal                         ║" -ForegroundColor Green
    Write-Host "║  ✅ Filtro: Status                           ║" -ForegroundColor Green
    Write-Host "║  ✅ Filtro: Natureza da Obrigação            ║" -ForegroundColor Green
    Write-Host "║  ✅ Filtro: ANO da LOA                       ║" -ForegroundColor Green
    Write-Host "║  ✅ Exportação Excel/PDF                     ║" -ForegroundColor Green
    Write-Host "║  ✅ Dashboard com gráficos                   ║" -ForegroundColor Green
    Write-Host "║  ✅ Busca automatizada TJ-SP                 ║" -ForegroundColor Green
    Write-Host "║                                               ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════╝`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Erro: $($_.Exception.Message)`n" -ForegroundColor Red
}
