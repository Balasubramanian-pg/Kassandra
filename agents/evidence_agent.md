# Evidence Agent Specification

## Responsibilities
1. Load verified candidate assets from `vault/05 - Candidate Profile/`:
   - Experience Markdown records
   - Skill demonstration logs
   - Project case studies
2. Match every JD requirement against available candidate evidence.
3. Classify matches into:
   - `STRONG_MATCH`
   - `MATCH`
   - `PARTIAL_MATCH`
   - `TRANSFERABLE`
   - `MISSING`
   - `UNKNOWN`
4. Emit `vault/02 - Job Analysis/<JOB-ID> - Evidence Map.md` linking directly to candidate files with wiki-links.
