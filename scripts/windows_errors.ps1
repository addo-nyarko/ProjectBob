# Check recent Windows errors
Write-Host "=== RECENT SYSTEM ERRORS (Last 24hrs) ===" -ForegroundColor Cyan
Get-EventLog -LogName System -EntryType Error -Newest 10 | Select-Object TimeGenerated, Source, Message | Format-Table -AutoSize -Wrap
