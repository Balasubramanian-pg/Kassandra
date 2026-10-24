# Resume Agent Specification

## Responsibilities
1. Consume JD Analysis and the Evidence Map.
2. Draft a tailored Markdown resume (`03 - Resume.md`).
3. Enforce the Zero-Hallucination Prime Directive:
   - Never invent skills, employers, titles, dates, or metrics.
   - Tailor summary and bullet emphasis truthfully using candidate evidence.
   - Preserve chronological integrity and genuine company titles.
4. Compile the canonical Markdown representation into `.docx` (via `python-docx`) and `.pdf` (via Playwright browser print).
5. Version iterations cleanly (`RESUME-000001`, `RESUME-000001-v2`).
