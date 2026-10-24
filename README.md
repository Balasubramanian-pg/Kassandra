# Kassandra — Antigravity Job Application Engine

> **The Obsidian Markdown vault is the database and single source of truth.**
> A local-first, privacy-respecting, agent-driven job discovery, qualification, resume tailoring, ATS validation, and application tracking platform.

---

## 🌟 Overview

**Kassandra** is an intelligent job search and application engine built on top of Antigravity agent automation and Playwright. It automates the end-to-end job application lifecycle while adhering strictly to ethical guidelines and human-in-the-loop validation:

1. **Job Discovery**: Discovers high-affinity roles from configured job portals (e.g., Naukri) using Playwright browser automation.
2. **Job Extraction**: Captures complete, unadulterated Job Descriptions (JDs) and extracts structured requirements.
3. **Normalization & Deduplication**: Canonicalizes titles, skills, locations, and companies using taxonomy tables; deduplicates multi-source postings.
4. **Hard Qualification Filtering**: Disqualifies roles outside candidate experience ranges, incompatible locations, or excluded seniority tiers.
5. **Explainable Job Fit Scoring**: Scores opportunities against the candidate profile using weighted criteria with transparent reasoning.
6. **Candidate Evidence Mapping**: Maps JD requirements to verified candidate achievements, skills, and projects using Obsidian wiki-links.
7. **Tailored Resume Generation**: Generates truthful, ATS-optimized Markdown resumes, compiled into `.docx` and `.pdf` without hallucinated claims.
8. **ATS / Application Validation**: Verifies requirement coverage and ensures strict evidence integrity before human review.
9. **Controlled Application Assistance**: Prepares applications and aids browser navigation, requiring explicit human confirmation before submission.
10. **Application Tracking & Analytics**: Audits every status transition within Obsidian Markdown files.

---

## 🏗️ Architectural Core Principles

- **Markdown is the Database**: Every persistent entity (job, candidate skill, project, resume, application) is a Markdown file with structured YAML frontmatter.
- **No Secondary Databases**: No SQLite, PostgreSQL, Airtable, Notion, or Supabase. The Obsidian vault is canonical.
- **Evidence-Based Tailoring (Zero Hallucination)**: The generator may only use claims backed by candidate evidence files (`[[SQL]]`, `[[Healthcare MDM]]`).
- **Human-Controlled Submission**: Never automatically submits applications without explicit confirmation.
- **Extensible & Source-Agnostic**: Modular architecture designed to scale to LinkedIn, Indeed, and direct company careers portals.

---

## 📁 Repository Structure

```text
├── README.md                           # Project documentation
├── LICENSE                             # MIT License
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git exclusions
├── config/
│   ├── system_config.yaml              # Browser, rate-limiting & model settings
│   ├── scoring_config.yaml             # Evaluation weights & thresholds
│   └── search_config.yaml              # Search filters & target roles
├── vault/                              # Canonical Obsidian Vault
│   ├── 00 - Dashboard/                 # Pipeline overviews & progress logs
│   ├── 01 - Jobs/                      # Discovered job records by date
│   ├── 02 - Job Analysis/              # Evidence maps & requirement audits
│   ├── 03 - Applications/              # Application tracking records
│   ├── 04 - Resumes/                   # Master resume & tailored artifacts
│   ├── 05 - Candidate Profile/         # Skills, experience, projects KB
│   ├── 06 - Companies/                 # Company intelligence graph
│   ├── 08 - Search Configuration/      # Configurable search parameters
