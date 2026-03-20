# Check disk space and health
Write-Host "=== DISK SPACE ===" -ForegroundColor Cyan
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name="Used (GB)";Expression={[math]::Round($_.Used/1GB,2)}}, @{Name="Free (GB)";Expression={[math]::Round($_.Free/1GB,2)}} | Format-Table -AutoSize

Write-Host ""
Write-Host "=== DISK HEALTH ===" -ForegroundColor Cyan
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, Size | Format-Table -AutoSize
