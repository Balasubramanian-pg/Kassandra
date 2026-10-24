---
type: schema_documentation
version: "1.0.0"
---

# Vault Schema & Frontmatter Specifications

This document defines the schema rules for all persistent entities within the Kassandra Markdown vault.

## 1. Job Entity (`vault/01 - Jobs/YYYY/MM/YYYY-MM-DD/JOB-XXXXXX - Company - Title.md`)

```yaml
---
type: job
job_id: JOB-000001
source: naukri
source_job_id: "123456789"
source_url: "https://..."
company: Example Company
title: Business Intelligence Developer
location:
  - Pune
posted_date: 2026-08-28
discovered_date: 2026-08-28
experience_min: 2
experience_max: 5
status: discovered | qualified | shortlisted | rejected
fit_score: 91
priority: high | medium | low
resume_status: pending | cv_generated | cv_validated
ats_status: pending | pass | needs_review
application_status: not_applied | ready_to_apply | applied
tags:
  - job
  - naukri
  - bi
---
```

## 2. Candidate Skill (`vault/05 - Candidate Profile/Skills/<Skill>.md`)

```yaml
---
type: skill
skill: SQL
level: advanced
years_experience: 3
---
```

## 3. Tailored Resume (`vault/04 - Resumes/Tailored/<JOB-ID>/03 - Resume.md`)

```yaml
---
type: resume
job_id: JOB-000001
version: "1.0"
generated_date: 2026-08-28
---
```

## 4. Application Record (`vault/03 - Applications/<JOB-ID> - Company - Title.md`)

```yaml
---
type: application
job_id: JOB-000001
status: ready_to_apply | applied | screening | interview | offer | rejected
resume_id: RESUME-JOB-000001
prepared_date: 2026-08-28
applied_date: null
application_method: naukri
interview_stage: none
response_status: pending
---
```
