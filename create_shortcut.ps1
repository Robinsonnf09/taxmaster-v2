# Script para criar atalho no desktop

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = "$DesktopPath\Tax Master.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "$PWD\start_background.bat"
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.IconLocation = "shell32.dll,21"
$Shortcut.Description = "Tax Master - Sistema de Gestão de Precatórios"
$Shortcut.Save()

Write-Host "[OK] Atalho criado na area de trabalho!" -ForegroundColor Green
Write-Host "Nome: Tax Master.lnk" -ForegroundColor Cyan
