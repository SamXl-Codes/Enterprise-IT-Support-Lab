#requires -Version 5.1
<#
.SYNOPSIS
  Controlled AD joiner provisioning for an isolated lab.example domain.
.DESCRIPTION
  Read-only preview by default. Requires -Apply and interactive confirmation
  before it creates an account. Refuses any OU outside lab.example.
.EXAMPLE
  .\Invoke-LabJoiner.ps1 -GivenName Alex -Surname Morgan -SamAccountName amorgan -LabOuDn 'OU=LabUsers,DC=lab,DC=example'
.EXAMPLE
  .\Invoke-LabJoiner.ps1 -GivenName Alex -Surname Morgan -SamAccountName amorgan -LabOuDn 'OU=LabUsers,DC=lab,DC=example' -Apply
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-zA-Z][a-zA-Z0-9._-]{2,19}$')][string]$SamAccountName,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$GivenName,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$Surname,
    [Parameter(Mandatory)][string]$LabOuDn,
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
if ($LabOuDn -notmatch '(?i)^OU=[^,]+,(?:OU=[^,]+,)*DC=lab,DC=example$') {
    throw 'Refused: target OU must belong to the isolated lab.example domain.'
}
$displayName = "$GivenName $Surname"
$userPrincipalName = "$SamAccountName@lab.example"
if (-not $Apply) {
    [pscustomobject]@{ Mode = 'Preview'; Name = $displayName; SamAccountName = $SamAccountName; UserPrincipalName = $userPrincipalName; TargetOu = $LabOuDn } | Format-List
    Write-Host 'No changes made. Specify -Apply to perform an authorised lab operation.'
    return
}
Import-Module ActiveDirectory -ErrorAction Stop
$domain = (Get-ADDomain -ErrorAction Stop).DNSRoot
if ($domain -ine 'lab.example') { throw "Refused: connected domain is $domain, expected lab.example." }
Get-ADOrganizationalUnit -Identity $LabOuDn -ErrorAction Stop | Out-Null
if (Get-ADUser -Filter "SamAccountName -eq '$SamAccountName'" -ErrorAction Stop) {
    throw 'User already exists; no operation performed.'
}
if ($PSCmdlet.ShouldProcess("$userPrincipalName in $LabOuDn", 'Create lab AD user')) {
    $secret = Read-Host 'Temporary lab account password (not saved)' -AsSecureString
    New-ADUser -Name $displayName -GivenName $GivenName -Surname $Surname `
        -SamAccountName $SamAccountName -UserPrincipalName $userPrincipalName `
        -Path $LabOuDn -AccountPassword $secret -Enabled $true -ChangePasswordAtLogon $true
    Write-Host "Lab joiner provisioned: $SamAccountName"
}
