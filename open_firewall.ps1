param(
    [int]$Port = 8080,
    [string]$RuleName = "PDF to Word LAN Server"
)

$ErrorActionPreference = "Stop"

$existingRule = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
if ($null -eq $existingRule) {
    New-NetFirewallRule `
        -DisplayName $RuleName `
        -Direction Inbound `
        -Action Allow `
        -Protocol TCP `
        -LocalPort $Port `
        -Profile Private | Out-Null
}
else {
    Set-NetFirewallRule -DisplayName $RuleName -Enabled True -Profile Private | Out-Null
}

Write-Host "Đã mở Windows Firewall cho TCP port $Port trong mạng Private."
