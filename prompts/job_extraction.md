# Job Extraction Prompt Template

```markdown
Analyze the following Job Description (JD) and extract details into a JSON object.
Do not invent or assume fields. Keep them empty or null if not found.

JSON keys to return:
- responsibilities (list of strings)
- required_skills (list of strings)
- preferred_skills (list of strings)
- technologies (list of strings)
- education_requirements (list of strings)
- certifications (list of strings)
- domain (string)
- remote_type (string, e.g. "remote", "hybrid", "onsite", "unknown")

JD Content:
---
{raw_jd}
---

Return ONLY raw JSON, starting with { and ending with }. Do not wrap it in markdown code blocks.
```
