# Job Extraction Prompt Template

```markdown
Analyze the following Job Description (JD) and extract details into a JSON object.
Do not invent or assume fields. Keep them empty or null if not found.

JSON keys to return:
- responsibilities (list of strings)
- required_skills (list of strings)
- preferred_skills (list of strings)
- technologies (list of strings)
