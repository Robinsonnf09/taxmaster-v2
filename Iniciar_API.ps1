Write-Host "Iniciando API REST do TaxMaster CRM..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000"

Write-Host "[OK] API iniciada em: http://localhost:8000" -ForegroundColor Green
Write-Host "Documentacao: http://localhost:8000/docs" -ForegroundColor Cyan
