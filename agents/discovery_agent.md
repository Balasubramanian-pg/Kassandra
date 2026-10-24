# Discovery Agent Specification

## Responsibilities
1. Read search filters from `vault/08 - Search Configuration/Search Configuration.md`.
2. Connect to configured job platforms (e.g., Naukri) through Playwright with persistent sessions.
3. Formulate query URLs across target titles and target locations.
4. Collect job listing links, basic snippets, and source identifiers.
5. Filter out already-scraped canonical URLs.
6. Write discovered stub records to `vault/01 - Jobs/YYYY/MM/YYYY-MM-DD/`.

## Boundary Constraints
- Do NOT score jobs.
- Do NOT generate resumes.
- Do NOT attempt to solve CAPTCHAs or bypass anti-bot mechanisms.
- Halt and alert immediately upon encountering access barriers.
