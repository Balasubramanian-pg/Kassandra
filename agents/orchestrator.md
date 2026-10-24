# Orchestrator Agent Specification

## Role
Coordinates the sequential execution of specialized subagents across discovery, extraction, qualification, scoring, evidence mapping, resume generation, ATS validation, and application recording.

## Input
- `config/system_config.yaml`
- `config/scoring_config.yaml`
- `vault/08 - Search Configuration/Search Configuration.md`

## Pipeline Flow
1. **Discovery**: Spawns Discovery Agent to retrieve fresh job URLs.
2. **Extraction**: Invokes Extraction Agent to pull complete JDs into vault Markdown files.
3. **Normalization**: Canonicalizes company, title, location, and skills via `vault/99 - System/Taxonomy.md`.
4. **Deduplication**: Merges multi-source postings by URL, source ID, and title/company heuristics.
5. **Qualification**: Discards out-of-bounds listings with explicit rejection reasons.
6. **Scoring**: Computes explainable fit score (0-100) and selects daily top target jobs.
7. **Evidence Mapping**: Links JD requirements to `vault/05 - Candidate Profile/` entities.
8. **Resume Generation**: Emits tailored Markdown, DOCX, and PDF resume versions.
9. **ATS Validation**: Evaluates keyword match and evidence fidelity with up to 1 revision loop.
10. **Application Recording**: Creates staging application files in `vault/03 - Applications/`.
11. **Reporting**: Appends daily run analytics in `vault/00 - Dashboard/Daily/`.

## Failure Handling
Halt upon persistent access blocks; log errors to `vault/99 - System/Errors/`. Never invent missing data.
