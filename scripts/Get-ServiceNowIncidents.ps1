#requires -Version 5.1
<# Read-only incident metadata query from an authorised ServiceNow test instance.
   Obtain a scoped OAuth access token separately and place it in the
   SERVICENOW_ACCESS_TOKEN environment variable. Never commit tokens. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InstanceUrl,
    [ValidateRange(1,100)][int]$Limit = 20
)
$ErrorActionPreference = 'Stop'
$uriObject = [uri]$InstanceUrl
if ($uriObject.Scheme -ne 'https' -or $uriObject.Host -notmatch '(?i)^[a-z0-9-]+\.service-now\.com$') {
    throw 'Expected an HTTPS ServiceNow instance URL (*.service-now.com).'
}
if ([string]::IsNullOrWhiteSpace($env:SERVICENOW_ACCESS_TOKEN)) {
    throw 'Missing SERVICENOW_ACCESS_TOKEN. Use an approved OAuth flow in your test environment.'
}
$base = $uriObject.GetLeftPart([System.UriPartial]::Authority)
$uri = "$base/api/now/table/incident?sysparm_fields=number,priority,state,opened_at&sysparm_limit=$Limit"
$headers = @{ Authorization = "Bearer $($env:SERVICENOW_ACCESS_TOKEN)"; Accept = 'application/json' }
$result = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -ErrorAction Stop
# Deliberately exclude caller, descriptions, comments, attachments and other PII.
$result.result | Select-Object number,priority,state,opened_at | Format-Table -AutoSize
