Write-Host "Iniciando robos de coleta..." -ForegroundColor Cyan

$robots = @("robot_tjrj.py", "robot_tjsp.py", "robot_tjrs.py")

foreach ($robot in $robots) {
    $robotPath = "robots/$robot"
    if (Test-Path $robotPath) {
        Write-Host "Iniciando $robot..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python $robotPath"
    }
}

Write-Host "`n[OK] Robos iniciados!" -ForegroundColor Green
