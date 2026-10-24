# Deduplication Agent Specification

## Responsibilities
1. Identify duplicate job records across multi-platform discovery runs.
2. Compare primary signals: `source_job_id` and normalized URL paths.
3. Compare secondary signals: fuzzy matching on company, title, and location.
4. Merge duplicate listings into a single canonical Markdown record, consolidating source URLs.
5. Prevent redundant downstream scoring and application preparation.
