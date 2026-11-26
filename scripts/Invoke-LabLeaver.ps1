#requires -Version 5.1
# Demonstration only. Never use this script against production domains.
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-zA-Z][a-zA-Z0-9._-]{2,19}$')][string]$SamAccountName,
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
if (-not $Apply) {
    Write-Host "PREVIEW: would verify and disable $SamAccountName in the isolated lab.example domain. No action taken."
    return
}
Import-Module ActiveDirectory -ErrorAction Stop
if ((Get-ADDomain).DNSRoot -ine 'lab.example') { throw 'Refused: not in lab.example domain.' }
$user = Get-ADUser -Identity $SamAccountName -Properties DistinguishedName,Enabled -ErrorAction Stop
if ($user.DistinguishedName -notmatch '(?i),OU=LabUsers,DC=lab,DC=example$') {
    throw 'Refused: account is not in the dedicated LabUsers OU.'
}
if ($user.Enabled -and $PSCmdlet.ShouldProcess($SamAccountName, 'Disable lab account')) {
    Disable-ADAccount -Identity $user
    Write-Host 'Lab account disabled. Review group access and separately revoke cloud sessions if required.'
}
