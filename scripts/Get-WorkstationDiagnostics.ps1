#requires -Version 5.1
# Read-only diagnostic summary, Windows 10/11. Omits identity and address information.
[CmdletBinding()]
param([string]$HostToResolve = 'example.com')
$ErrorActionPreference = 'Continue'
$os = Get-CimInstance Win32_OperatingSystem
$adapter = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1
$dnsOk = $false
try { $dnsOk = @((Resolve-DnsName -Name $HostToResolve -ErrorAction Stop)).Count -gt 0 } catch { $dnsOk = $false }
[pscustomobject]@{
    TimestampUtc = (Get-Date).ToUniversalTime().ToString('o')
    OSName = $os.Caption
    OSBuild = $os.BuildNumber
    PrimaryAdapterStatus = if ($adapter) { $adapter.Status } else { 'No active adapter' }
    DnsLookupTarget = $HostToResolve
    DnsLookupSucceeded = $dnsOk
    RemediationPerformed = $false
} | ConvertTo-Json -Depth 3
