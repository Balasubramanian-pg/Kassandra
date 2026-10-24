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
