# ==========================================
# SCRIPT DE CONFIGURAÇÃO AUTOMÁTICA DO .ENV
# ==========================================

Write-Host "`n🔐 CONFIGURAÇÃO DE CREDENCIAIS TJSP" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

Write-Host "`n📋 Digite suas credenciais do e-SAJ TJSP:" -ForegroundColor Yellow
Write-Host ""

# Solicitar usuário
$usuario = Read-Host "   👤 Usuário TJSP (CPF ou Login)"

# Solicitar senha
$senha = Read-Host "   🔑 Senha TJSP"

Write-Host "`n⚙️  Atualizando arquivo .env..." -ForegroundColor Yellow

# Ler arquivo atual
$conteudo = Get-Content ".env" -Raw

# Substituir valores
$conteudo = $conteudo -replace "TJSP_USUARIO=seu_usuario_aqui", "TJSP_USUARIO=$usuario"
$conteudo = $conteudo -replace "TJSP_SENHA=sua_senha_aqui", "TJSP_SENHA=$senha"

# Salvar arquivo
$conteudo | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host "`n✅ CREDENCIAIS CONFIGURADAS COM SUCESSO!" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green

Write-Host "`n📄 Arquivo .env atualizado:" -ForegroundColor Cyan
Write-Host "   Usuário: $usuario" -ForegroundColor White
Write-Host "   Senha: " -NoNewline -ForegroundColor White
Write-Host ("*" * $senha.Length) -ForegroundColor White

Write-Host "`n🔒 SEGURANÇA:" -ForegroundColor Yellow
Write-Host "   Suas credenciais estão salvas localmente em .env" -ForegroundColor White
Write-Host "   Não compartilhe este arquivo!" -ForegroundColor White

Write-Host "`n"
