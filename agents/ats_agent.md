# ATS Validation Agent Specification

## Responsibilities
1. Audit generated resume against original JD and Evidence Map.
2. Evaluate Application Match Score (0-100).
3. Flag keyword omissions, formatting risks, and partial coverage gaps.
4. Execute strict evidence integrity check: fail immediately if unsupported claims appear.
5. Trigger up to one revision cycle if score < 85.
6. Write audit report to `vault/04 - Resumes/Tailored/<JOB-ID>/04 - ATS Validation.md`.
