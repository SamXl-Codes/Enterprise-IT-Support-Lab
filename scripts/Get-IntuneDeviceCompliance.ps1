#requires -Version 5.1
<# Read-only report. Requires Microsoft.Graph.Authentication and an Intune-licensed tenant.
   Delegated scope: DeviceManagementManagedDevices.Read.All.
   No device IDs, user identities, serial numbers or tokens are written to disk. #>
[CmdletBinding()]
param([string]$OutputCsv)
$ErrorActionPreference = 'Stop'
Import-Module Microsoft.Graph.Authentication -ErrorAction Stop
Connect-MgGraph -Scopes 'DeviceManagementManagedDevices.Read.All' -NoWelcome -ErrorAction Stop
$uri = 'https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$select=deviceName,operatingSystem,complianceState,lastSyncDateTime&$top=100'
$results = [System.Collections.Generic.List[object]]::new()
while ($uri) {
    $page = Invoke-MgGraphRequest -Method GET -Uri $uri -ErrorAction Stop
    foreach ($device in $page.value) {
        $results.Add([pscustomobject]@{
            DeviceName = [string]$device.deviceName
            OperatingSystem = [string]$device.operatingSystem
            ComplianceState = [string]$device.complianceState
            LastSyncUtc = [string]$device.lastSyncDateTime
        })
    }
    $uri = $page.'@odata.nextLink'
}
$results | Sort-Object DeviceName | Format-Table -AutoSize
if ($OutputCsv) {
    Write-Warning 'CSV exports may contain identifiable device names. Use fictional/test devices only.'
    $results | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8
}
