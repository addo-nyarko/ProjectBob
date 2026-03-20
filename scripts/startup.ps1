# Check and list startup programs
Write-Host "=== STARTUP PROGRAMS ===" -ForegroundColor Cyan
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize

Write-Host ""
Write-Host "=== SCHEDULED TASKS (Running) ===" -ForegroundColor Cyan
Get-ScheduledTask | Where-Object {$_.State -eq "Running"} | Select-Object TaskName, State | Format-Table -AutoSize
