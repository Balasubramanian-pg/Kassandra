# Qualification Agent Specification

## Responsibilities
1. Evaluate hard criteria before committing LLM evaluation tokens:
   - Required experience exceeds candidate ceiling (`experience_max`).
   - Title diverges completely from target roles.
   - Location is strictly incompatible and non-remote.
   - Executive or senior managerial tier when excluded.
2. Mark filtered listings as `status: rejected` with explicit `rejection_reason`.
3. Append status change to `## Status History` in the job Markdown body.
4. Retain rejected records in the vault for historical analysis.
