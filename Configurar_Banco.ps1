Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     CONFIGURANDO BANCO DE DADOS POSTGRESQL                " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n[1/5] Verificando PostgreSQL..." -ForegroundColor Yellow

# Verificar se PostgreSQL esta instalado
$pgVersion = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] PostgreSQL instalado: $pgVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] PostgreSQL nao encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/5] Criando banco de dados..." -ForegroundColor Yellow

# Criar banco de dados
$createDbScript = @"
-- Criar banco de dados taxmaster_crm
DROP DATABASE IF EXISTS taxmaster_crm;
CREATE DATABASE taxmaster_crm;

-- Conectar ao banco
\c taxmaster_crm;

-- Criar extensoes
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Mensagem de sucesso
SELECT 'Banco de dados criado com sucesso!' as status;
"@

# Salvar script SQL
$createDbScript | Out-File -FilePath "config/create_db.sql" -Encoding UTF8

# Executar script (usuario postgres padrao)
Write-Host "Executando script de criacao..." -ForegroundColor Cyan
Write-Host "Senha padrao do PostgreSQL (geralmente 'postgres' ou vazio)" -ForegroundColor Yellow

psql -U postgres -f "config/create_db.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Banco de dados criado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Erro ao criar banco. Tente manualmente:" -ForegroundColor Yellow
    Write-Host "psql -U postgres -c 'CREATE DATABASE taxmaster_crm;'" -ForegroundColor Cyan
}

Write-Host "`n[3/5] Criando tabelas..." -ForegroundColor Yellow

# Criar tabelas usando SQLAlchemy
python -c "import sys; sys.path.append('src'); from database import Base, engine; Base.metadata.create_all(bind=engine); print('[OK] Tabelas criadas com sucesso')"

Write-Host "`n[4/5] Inserindo dados de exemplo..." -ForegroundColor Yellow

$insertDataScript = @"
\c taxmaster_crm;

-- Inserir processos de exemplo
INSERT INTO processos (numero_processo, tribunal, tipo, valor_principal, valor_atualizado, credor_nome, fase, score_oportunidade, dados_completos, created_at, updated_at)
VALUES 
('0001234-56.2024.8.19.0001', 'TJRJ', 'Precatorio', 2300000, 2530000, 'Joao Silva', 'Expedido', 9.2, '{"exemplo": true}', NOW(), NOW()),
('1234567-89.2024.8.26.0100', 'TJSP', 'Precatorio', 450000, 495000, 'Maria Santos', 'Transito em julgado', 8.7, '{"exemplo": true}', NOW(), NOW()),
('0012345-67.2024.4.01.0000', 'TRF1', 'Precatorio', 1800000, 1980000, 'Pedro Costa', 'Fase final', 8.9, '{"exemplo": true}', NOW(), NOW()),
('9876543-21.2024.8.21.0001', 'TJRS', 'Precatorio', 680000, 748000, 'Ana Oliveira', 'Em andamento', 7.5, '{"exemplo": true}', NOW(), NOW()),
('5555555-55.2024.4.02.0000', 'TRF2', 'Precatorio', 320000, 352000, 'Carlos Souza', 'Inicial', 6.8, '{"exemplo": true}', NOW(), NOW());

SELECT 'Dados de exemplo inseridos!' as status;
SELECT COUNT(*) as total_processos FROM processos;
"@

$insertDataScript | Out-File -FilePath "config/insert_data.sql" -Encoding UTF8

psql -U postgres -d taxmaster_crm -f "config/insert_data.sql"

Write-Host "`n[5/5] Testando conexao..." -ForegroundColor Yellow

python -c @"
import sys
sys.path.append('src')
from database import SessionLocal, Processo

db = SessionLocal()
try:
    total = db.query(Processo).count()
    print(f'[OK] Conexao estabelecida! Total de processos: {total}')
except Exception as e:
    print(f'[ERRO] Falha na conexao: {str(e)}')
finally:
    db.close()
"@

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "     BANCO DE DADOS CONFIGURADO COM SUCESSO!               " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`nCONFIGURACAO:" -ForegroundColor Cyan
Write-Host "Host: localhost" -ForegroundColor White
Write-Host "Porta: 5432" -ForegroundColor White
Write-Host "Banco: taxmaster_crm" -ForegroundColor White
Write-Host "Usuario: postgres" -ForegroundColor White

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Iniciar API: .\Iniciar_API.ps1" -ForegroundColor White
Write-Host "2. Testar robos: python robots/robot_tjsp.py" -ForegroundColor White
Write-Host "3. Dashboard real: python -m streamlit run dashboard/app_real.py" -ForegroundColor White

Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
