# Lab build plan

## Scope

This repository includes working **offline** ticket-analysis code, safe PowerShell **lab templates**, and instructions for building a real test environment. It does not claim that a Microsoft 365 tenant, Windows domain or Intune environment has been deployed.

## Prerequisites for optional live lab

- A **separate** Windows Server test VM with Active Directory Domain Services, DNS and an `lab.example` forest, using a dedicated `OU=LabUsers,DC=lab,DC=example`.
- A Windows 11 test client joined to that **lab** domain.
- Optional test tenant with an appropriate Intune license, administrative approval and disposable devices.
- PowerShell 5.1+, ActiveDirectory module for domain tasks, and Microsoft.Graph.Authentication for the read-only Intune report.

## Suggested workflow

1. Keep all VMs on a private virtual network and create snapshots.
2. Create the `lab.example` forest and `LabUsers` OU manually.
3. Exercise `Invoke-LabJoiner.ps1` in preview mode, then explicitly with `-Apply` on the test domain only.
4. Validate client sign-in and group policy; record **redacted** screenshots.
5. Run `Get-WorkstationDiagnostics.ps1` on the client, then compare it with a known synthetic DNS fault.
6. Test `Invoke-LabLeaver.ps1` in preview mode and with approval in the isolated domain.
7. Optionally connect to a licensed Intune test tenant for read-only device compliance reporting.
8. Reproduce sample ticket SLAs with the Python CLI and document the incident-handling sequence.

## Evidence to collect (not included yet)

- AD forest name, lab OU structure and domain-joined client; obscure user names and IPs.
- PowerShell preview then controlled execution and user lifecycle checks.
- Intune device compliance screenshots from the **test** tenant (if available).
- Five ticket examples with triage, resolution, escalation and runbook links.
- Real command output and execution results, not mock screenshots.

Do not point the AD scripts at an employer domain. Do not upload credentials, full tenant exports, real tickets, personal information or unredacted screenshots.
