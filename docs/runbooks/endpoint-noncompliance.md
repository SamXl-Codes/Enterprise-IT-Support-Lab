# Runbook: Intune noncompliant endpoint

1. Identify the affected **test** device and check enrolment, OS version, compliance policy assignment and last sync.
2. Separate policy evaluation delays from actual control failures (encryption, antivirus, update rings, password lock).
3. Confirm how Conditional Access affects the user's access; do not disable protections merely to clear a ticket.
4. Remediate in the test tenant with approval, sync the device, wait for policy evaluation, and re-check status.
5. Document change reference, timestamps, policy, result and escalation to endpoint engineering if unresolved.

The supplied PowerShell tool is intentionally read-only. No access change or remote wipe is implemented.
