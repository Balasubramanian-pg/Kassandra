# Evidence Mapping Prompt Template

```markdown
Given the following Candidate Knowledge Base (experience, skills, projects) and the Job Description,
map each key job requirement to candidate evidence. 

For each requirement, classify it as: STRONG_MATCH, MATCH, PARTIAL_MATCH, TRANSFERABLE, MISSING, or UNKNOWN.
Use Obsidian wiki-links (e.g. [[SQL]], [[Company A]], [[Healthcare MDM]]) to point to the source of evidence.

Candidate Knowledge Base:
---
Experience:
{candidate_experience_json}

Skills:
{candidate_skills_json}

Projects:
{candidate_projects_json}
---
