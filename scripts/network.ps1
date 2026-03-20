# Check network status and connectivity
Write-Host "=== NETWORK ADAPTERS ===" -ForegroundColor Cyan
Get-NetAdapter | Select-Object Name, Status, LinkSpeed | Format-Table -AutoSize

Write-Host ""
Write-Host "=== PING TEST (Google) ===" -ForegroundColor Cyan
Test-Connection -ComputerName google.com -Count 4 | Format-Table -AutoSize

Write-Host ""
Write-Host "=== IP CONFIGURATION ===" -ForegroundColor Cyan
Get-NetIPAddress | Where-Object {$_.AddressFamily -eq "IPv4"} | Select-Object InterfaceAlias, IPAddress | Format-Table -AutoSize
