Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     INICIANDO TAXMASTER CRM                                " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Verificando dependencias..." -ForegroundColor Yellow
python -c "import playwright; print('[OK] Playwright')"
python -c "import streamlit; print('[OK] Streamlit')"
python -c "import sqlalchemy; print('[OK] SQLAlchemy')"

Write-Host "`n[2/3] Iniciando Dashboard..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; streamlit run dashboard/app.py"

Write-Host "`n[3/3] Dashboard iniciado!" -ForegroundColor Green
Write-Host "Acesse: http://localhost:8501" -ForegroundColor Cyan

Write-Host "`nPara iniciar os robos, execute: .\Iniciar_Robos.ps1" -ForegroundColor Yellow
