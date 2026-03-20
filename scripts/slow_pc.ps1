# Check top CPU and RAM consuming processes
Write-Host "=== TOP CPU PROCESSES ===" -ForegroundColor Cyan
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet | Format-Table -AutoSize

Write-Host ""
Write-Host "=== TOP RAM PROCESSES ===" -ForegroundColor Cyan
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 Name, @{Name="RAM (MB)";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Format-Table -AutoSize

Write-Host ""
Write-Host "=== SYSTEM UPTIME ===" -ForegroundColor Cyan
(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime
