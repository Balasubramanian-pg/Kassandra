# ATS Validation Prompt Template

```markdown
Perform an ATS audit comparing the target Job Description, Candidate Resume, and Evidence Map.
Verify that:
1. No unsupported or fabricated candidate claims exist in the resume.
2. The resume matches the terminology and structure of the job description.

Job Description:
---
{job_description}
---

Candidate Resume:
---
{candidate_resume}
---

Evidence Map:
---
{evidence_map}
---

Return a JSON response containing:
- application_match_score (integer 0-100)
- strong_coverage (list of strings)
- partial_coverage (list of strings)
- missing (list of strings)
- unsupported_claims_detected (boolean)
- revision_needed (boolean, set to true if score < 85 or if unsupported claims were detected)
- revision_suggestions (string)

Return ONLY raw JSON, starting with { and ending with }. Do not wrap it in markdown code blocks.
```
