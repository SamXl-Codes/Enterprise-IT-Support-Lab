# Runbook: identity lockout or password reset

**Environment:** approved test directory, or follow an employer's documented process in a real environment.

1. Verify the requester's identity using an **approved** identity verification procedure; never use a caller-provided alternate number without verification.
2. Confirm scope: account status, MFA registration, sign-in logs and account lockout policy.
3. Distinguish expired password, disabled account, bad credentials, MFA issues and conditional access denial.
4. Execute only authorised reset or unlock actions following least privilege; do not email a temporary password in plaintext.
5. Require password change at next sign-in when supported and ensure MFA remains in effect.
6. Validate user access, update the ticket with timestamps, affected services and the final result.
7. Escalate repeated lockouts or anomalous geography to security operations.

**Evidence:** sanitized ticket timeline, exact error text, verification steps and resolution outcome.
